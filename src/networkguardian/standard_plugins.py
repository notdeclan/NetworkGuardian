import csv
import os
import platform
import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM
from urllib.error import URLError
from urllib.request import urlopen
from io import StringIO

import psutil
from jinja2 import Template
from psutil._common import bytes2human

from networkguardian.exceptions import PluginInitializationError
from networkguardian.framework.plugin import AbstractPlugin, PluginCategory, SystemPlatform, executor
from networkguardian.framework.registry import register_plugin

"""
    Module is used to store all the standard plugins
"""


# @register_plugin("Example", Category.ATTACK, "Declan W", 0.1)
class ExamplePlugin(AbstractPlugin):
    """
        An example plugin to demonstrate the functionality and api to developers of custom plugins.

        This doc comment will be used by network guardian as the description for the plugin, and information
        relating to the description, requirements, and operational instructions should be stored here to be displayed.

        <b>HTML elements are supported, but major changes to formatting is discouraged.</b>
    """

    def initialize(self):
        # Should a plugin require a dependency or further checks when loading, this should be done here.
        if "test" not in "test":
            # if a plugin for whatever reason cannot be loaded, PluginInitializationError should be raised
            raise PluginInitializationError("Test was not in test, so the plugin could not be initialized properly")

    # The plugins Jinja template should be returned here
    # Data that is returned from execute should be rendered here
    # For more information on how Jinja templating works, see https://jinja.palletsprojects.com/en/2.11.x/templates/
    template = Template("""
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
                {% for id, result in results.items() %}
                    <tr>
                        <td>{{ id }}</td>
                        <td>{{ result }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    """)

    @executor(template, SystemPlatform.WINDOWS, SystemPlatform.LINUX, SystemPlatform.MAC_OS)
    def execute(self) -> {}:
        # Do plugin execution here, IE scan or produce results from some data source
        # Then data should be formatted into a dictionary used for storage, and for rendering in the plugin template
        return {
            "results": {
                1: "Example Result",
                2: "Another Result"
            },
        }


@register_plugin("System Information", PluginCategory.INFO, "Declan W", 0.1)
class SystemInformationPlugin(AbstractPlugin):
    """
    Plugin returns
    """

    template = Template("""
            <table class="table">
                {% for name, value in information.items() %}
                <tr>
                    <th class="bg-dark text-light">{{name}}</th>
                    <td>{{value}}</td>
                </tr>
                {% endfor %}
            </table>
        """)

    @executor(template)
    def execute(self):
        # get information required
        system_name = platform.node()
        username = os.getlogin()
        system_platform = platform.platform()
        system = platform.system()
        processor = platform.processor()
        memory = self.get_memory()
        # return information to be formatted in the template with appropriate data label
        return {
            "information": {
                "System Name": system_name,
                "Username": username,
                "Platform": system_platform,
                "System": system,
                "Processor": processor,
                "Memory": memory
            }
        }

    def get_memory(self):
        """
        Converts bytes to a string representation providing the size to 2 decimal points, and the correct label for
        kilobytes, megabytes, gigabytes, and terabytes

        :return:
        """
        total_memory = psutil.virtual_memory().total
        size, power = self.format_bytes(total_memory)
        return f'{size:.2f} {power}'

    @staticmethod
    def format_bytes(byte_count):
        """
        :param byte_count: 4294967296
        :return: Size.2f Label - Example : 4.00 GB
        """
        # 2**10 = 1024
        power = 2 ** 10
        n = 0
        power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
        while byte_count > power:
            byte_count /= power
            n += 1

        return byte_count, power_labels[n]


@register_plugin("Network Interface Information", PluginCategory.INFO, "Owen", 0.1)
class NetworkInterfaceInformation(AbstractPlugin):
    """
        This plugin will return details about the network interfaces. Such as whether the device is online or not, the IP, broadcast address, netmask and mac address.

        It will also display information about packets, speed, dropped packets and more.
    """

    template = Template("""
            <table class="table table-responsive table-sm">
                <thead class="thead-dark">
                    <tr>
                        <th>Adapter Name</th>
                        <th>Speed</th>
                        <th>Duplex</th>
                        <th>MTU</th>
                        <th>Is-Up?</th>
                        <th>Bytes In</th>
                        <th>Packets In</th>
                        <th>Errors In</th>
                        <th>Drops In</th>
                        <th>Bytes Out</th>
                        <th>Packets Out</th>
                        <th>Errors Out</th>
                        <th>Drops Out</th>
                        <th>Mac</th>
                        <th>IPv4 Broadcast</th>
                        <th>IPv4 Netmask</th>
                        <th>IPv6 Broadcast</th>
                        <th>IPv6 Netmask</th>
                    </tr>
                </thead>
                <tbody>
                    {% for name, value in result.items() %}
                    {%- if value.Mac is defined %}
                    <tr>
                        <td>{{name}}</td>
                        <td>{{value.Speed}}MB</td>
                        <td>{{value.Duplex}}</td>
                        <td>{{value.MTU}}</td>
                        <td>{{value.up}}</td>
                        <td>{{value.bytesin}}</td> 
                        <td>{{value.packetsin}}</td> 
                        <td>{{value.errorsin}}</td> 
                        <td>{{value.dropsin}}</td> 
                        <td>{{value.bytesout}}</td> 
                        <td>{{value.packetsout}}</td> 
                        <td>{{value.errorsout}}</td> 
                        <td>{{value.dropsout}}</td> 
                        <td>{{value.Mac}}</td> 
                        <td>{{value.IPv4Broadcast}}</td> 
                        <td>{{value.IPv4Netmask}}</td> 
                        <td>{{value.IPv6Broadcast}}</td> 
                        <td>{{value.IPv6Netmask}}</td> 
                    </tr>
                    {%- endif %}
                    {%- endfor %}
                </tbody>
            </table>
        """)

    @executor(template)
    def execute(self):
        """
        Using psutil it gathers all the information required and puts it all into a list so it
        can be used in the template to be displayed into a table.
        """
        af_map = {
            socket.AF_INET: 'IPv4',
            socket.AF_INET6: 'IPv6',
            psutil.AF_LINK: 'MAC',
        }

        duplex_map = {
            psutil.NIC_DUPLEX_FULL: "Full",
            psutil.NIC_DUPLEX_HALF: "Half",
            psutil.NIC_DUPLEX_UNKNOWN: "?",
        }

        main_list = {}

        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        for nic, addrs in psutil.net_if_addrs().items():
            st = stats[nic]
            io = io_counters[nic]

            main_list.update({nic: {
                "Speed": st.speed or "-",
                "Duplex": duplex_map[st.duplex] or "-",
                "MTU": st.mtu or "-",
                "up": st.isup or "False",
                "bytesin": bytes2human(io.bytes_recv) or "0",
                "packetsin": io.packets_recv or "0",
                "errorsin": io.errin or "0",
                "dropsin": io.dropin or "0",
                "bytesout": bytes2human(io.bytes_sent) or "0",
                "packetsout": io.packets_sent or "0",
                "errorsout": io.errout or "0",
                "dropsout": io.dropout or "0",
            }})

            for addr in addrs:
                key = af_map.get(addr.family, addr.family)
                if key == "MAC":
                    main_list[nic]["Mac"] = addr.address or "-"
                else:
                    key_broadcast = key + "Broadcast"
                    key_netmask = key + "Netmask"
                    main_list[nic][key_broadcast] = addr.address or "-"
                    main_list[nic][key_netmask] = addr.netmask or "-"

        return {"result": main_list}


@register_plugin("Internet Connectivity", PluginCategory.INFO, "Velislav V", 1.0)
class CheckInternetConnectivityPlugin(AbstractPlugin):
    """
        This plugin determines whether the local machine has access to the internet
    """

    @executor(Template("System is {{ 'Connected' if internet else 'not Connected' }} to the Internet"))
    def execute(self):
        def check_internet():
            """
            Function is used to return whether the local machine has internet access

            Works by looping through multiple URL's and connecting to them, if one successfully connects
            it will return True, otherwise False

            :return: True/False
            """
            urls = ["https://google.co.uk", "https://youtube.com", "https://bbc.co.uk"]
            for url in urls:  # loop through all URL's
                try:
                    urlopen(url, timeout=5)
                    return True  # if connect, internet is working, return True
                except URLError:
                    print("timeout on", url)
                    continue  # if fail, go to next URL in loop

            return False  # if all URL's fail, return False

        return {"internet": check_internet()}


@register_plugin("NetStat Information", PluginCategory.INFO, "Owen", 1.0)
class NetStatInformation(AbstractPlugin):
    """
        The plugin returns netstat information

        This tells you about the different connections and information about them such as
        the protocol, local address, remote address, status, PID and the program name
    """

    template = Template("""
        <table class="table table-hover table-sm">
            <thead class="thead-dark">
                <tr>
                    <th>#</th>
                    <th>Protocol</th>
                    <th>Local Address</th>
                    <th>Remote Address</th>
                    <th>Status</th>
                    <th>PID</th>
                    <th>Program Name</th>
                </tr>
            </thead>
            <tbody>
                {% for name, value in result.items() %}
                    <tr>
                        <td>{{name}}</td>
                        <td>{{value.Protocol}}</td>
                        <td>{{value.LocalAddress}}</td>
                        <td>{{value.RemoteAddress}}</td>
                        <td>{{value.Status}}</td>
                        <td>{{value.PID}}</td> 
                        <td>{{value.ProgramName}}</td> 
                    </tr>
                {%- endfor %}
            </tbody>
        </table>
        """)

    @executor(template)
    def execute(self):
        """
            Get information using psutil and stores into variables
        """
        AD = "-"
        AF_INET6 = getattr(socket, 'AF_INET6', object())
        proto_map = {
            (AF_INET, SOCK_STREAM): 'tcp',
            (AF_INET6, SOCK_STREAM): 'tcp6',
            (AF_INET, SOCK_DGRAM): 'udp',
            (AF_INET6, SOCK_DGRAM): 'udp6',
        }

        main_list = {}
        i = 1
        proc_names = {}

        for p in psutil.process_iter(attrs=['pid', 'name']):
            proc_names[p.info['pid']] = p.info['name']
        for c in psutil.net_connections(kind='inet'):
            laddr = "%s:%s" % (c.laddr)
            raddr = ""
            if c.raddr:
                raddr = "%s:%s" % (c.raddr)

                main_list.update({i: {
                    "Protocol": proto_map[(c.family, c.type)],
                    "LocalAddress": laddr,
                    "RemoteAddress": raddr or "-",
                    "Status": c.status,
                    "PID": c.pid or "-",
                    "ProgramName": proc_names.get(c.pid, '?')[:15],
                }})
                i += 1

        return {"result": main_list}


@register_plugin("User Enumeration", PluginCategory.INFO, "Alexandra", 1.0)
class UserEnumerationPlugin(AbstractPlugin):

    windows_template = Template("""
            <table>
                <thead>
                    <tr>
                        <th>Node</th>
                        <th>AccountType</th>
                        <th>Description</th>
                        <th>Disabled</th>
                        <th>Domain</th>
                        <th>FullName</th>
                        <th>InstallDate</th>
                        <th>LocalAccount</th>
                        <th>Lockout</th>
                        <th>Name</th>
                        <th>PasswordChangeable</th>
                        <th>PasswordExpires</th>
                        <th>PasswordRequired</th>
                        <th>SID</th>
                        <th>SIDType</th>
                        <th>Status</th>
                    </tr>
                </thead>
            <tbody>
                {% for row in reader %}
                    <tr>
                        {% for cell in row %}
                            <td>{{ cell }}</td>
                        {% endfor %}
                    </tr>
                {% endfor %}                            
            </tbody>
        </table>
    """)

    @executor(windows_template, SystemPlatform.WINDOWS)
    def windows(self):
        process = os.subprocess.Popen(["wmic", "useraccount", "list", "full", "/format:csv"], stdout=os.subprocess.PIPE)
        users_output = process.communicate()[0]
        file_stream = StringIO(users_output.decode())
        for i in range(2):
            file_stream.readline()

        reader = csv.reader(file_stream)

        return {"reader": reader}

    unix_template = Template("""
        <table>
            <thead>
                <tr>
                    <th>Users</th>
                    <th>User Group</th>
                </tr>
            </thead>
            <tbody>
                {% for user, user_group in users.items() %}
                   <tr>
                        <td> {{user}} </td>
                        <td> {{user_group}} </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    """)

    @executor(unix_template, SystemPlatform.MAC_OS, SystemPlatform.LINUX)
    def unix(self):
        import grp
        users = {}
        for p in psutil.pwd.getpwall():
            users[p[0]] = grp.getgrgid(p[3])[0]
        return {"users": users}


