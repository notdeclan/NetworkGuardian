import os
import platform
import time
import urllib
import uuid
from urllib.error import URLError
from urllib.request import urlopen

import psutil
from psutil._common import bytes2human

from jinja2 import Template

import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM

from networkguardian.exceptions import PluginInitializationError
from networkguardian.plugin import BasePlugin, Category, Platform

"""
    Module is used to store all the standard plugins
"""


class ExamplePlugin(BasePlugin):
    """
        An example plugin to demonstrate the functionality and api to developers of custom plugins.

        This doc comment will be used by network guardian as the description for the plugin, and information
        relating to the description, requirements, and operational instructions should be stored here to be displayed.

        <b>HTML elements are supported, but major changes to formatting is discouraged.</b>
    """

    def __init__(self):
        super().__init__("Example", Category.ATTACK, "Declan W", 0.1,
                         [Platform.MAC_OS, Platform.WINDOWS, Platform.LINUX])

    def execute(self) -> {}:
        # Do plugin execution here, IE scan or produce results from some data source
        # Then data should be formatted into a dictionary used for storage, and for rendering in the plugin template
        return {

            "results": {
                1: "yessir",
            },
            "name": "dad",
        }

    def initialize(self):
        if "test" not in "test":
            raise PluginInitializationError("Test was not in test, so the plugin could not be initialized properly")

    @property
    def template(self) -> Template:
        return Template("""
            ID -  NAME
            {% for id, name in results.items() %}
            {{ id }} - {{ name }} 
            {% endfor %} 
            NAME: {{ name }}           
        """)

        # return Template(open("example.template").read())


class SystemInformationPlugin(BasePlugin):
    """
    Plugin returns
    """

    def __init__(self):
        super().__init__("System Information", Category.INFO, "Declan W", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])

    def execute(self) -> {}:
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

    @property
    def template(self) -> Template:
        return Template("""
            <table>
                {% for name, value in information.items() %}
                <tr>
                    <td>{{name}}</td>
                    <td>{{value}}</td>
                </tr>
                {% endfor %}
            </table>
        """)

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


class TestPlugin(BasePlugin):
    """
    Plugin returns
    """

    def __init__(self, sleep_time):
        super().__init__("Test Plugin", Category.INFO, "Declan W", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])
        self.sleep_time = sleep_time

    def execute(self) -> {}:
        print("Starting Sleep")
        time.sleep(self.sleep_time)
        return {
            "uuid": uuid.uuid4(),
            "sleep": self.sleep_time
        }

    @property
    def template(self) -> Template:
        return Template("""Test Plugin Completed {{uuid}} {{sleep}}""")


class NetworkInterfaceInformation(BasePlugin):
    """
        This plugin will return details about the network interfaces.
        Such as whether the device is online or not, the IP, broadcast address,
        netmask and mac address.
    """

    def __init__(self):
        super().__init__("Network Interface Information", Category.INFO, "Owen", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])

    def execute(self) -> {}:
        """
            Get information using psutil and stores into variables
        """

        af_map = {
            socket.AF_INET: 'IPv4',
            socket.AF_INET6: 'IPv6',
            psutil.AF_LINK: 'MAC',
        }

        duplex_map = {
            psutil.NIC_DUPLEX_FULL: "full",
            psutil.NIC_DUPLEX_HALF: "half",
            psutil.NIC_DUPLEX_UNKNOWN: "?",
        }

        main_list = {}

        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        for nic, addrs in psutil.net_if_addrs().items():
            main_list.update({nic: {

            }})
            """if nic in stats:
                st = stats[nic]
                print("    stats          : ", end='')
                print("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                    st.speed, duplex_map[st.duplex], st.mtu,
                    "yes" if st.isup else "no"))
            if nic in io_counters:
                io = io_counters[nic]
                print("    incoming       : ", end='')
                print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                    bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                    io.dropin))
                print("    outgoing       : ", end='')
                print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                    bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                    io.dropout))
            for addr in addrs:
                print("    %-4s" % af_map.get(addr.family, addr.family), end="")
                print(" address   : %s" % addr.address)
                if addr.broadcast:
                    print("         broadcast : %s" % addr.broadcast)
                if addr.netmask:
                    print("         netmask   : %s" % addr.netmask)
                if addr.ptp:
                    print("      p2p       : %s" % addr.ptp)"""
            print("")
        return "beep"

    @property
    def template(self) -> Template:
        """
        returns a template that will print all information using jinja2 loops
        """
        return Template("""
            <h3> Network Interfaces </h3>
            <table>
                <tr>
                    <th>Adapter Name</th>
                    <th>Is Up?</th>
                    <th>Mac</th>
                    <th>IP</th>
                    <th>Broadcast</th>
                    <th>Netmask</th>
                </tr>
                {% for name, value in result.items() %}
                {%- if value.Mac is defined %}
                <tr>
                    <td>{{name}}</td>
                    <td>{{value.IsUp}}</td>
                    <td>{{value.Mac}}</td>
                    <td>{{value.IP}}</td>
                    <td>{{value.Broadcast}}</td>
                    <td>{{value.Netmask}}</td> 
                </tr>
                {%- endif %}
                {%- endfor %}
            </table>
                
            <h3> Non-Standard Interfaces </h3>
            <table>
                <tr>
                    <th>Adapter Name</th>
                    <th>IP</th>
                    <th>Broadcast</th>
                    <th>Netmask</th>
                </tr>
                {%- for name, value in result.items() -%}
                {%- if value.Mac is undefined %}
                <tr>
                    <td> {{name}} </td>
                    <td> {{value.Address}} </td>
                    <td>{{value.Broadcast}}</td>
                    <td>{{value.Netmask}}</td>
                </tr>
                {%- endif -%}
                {%- endfor %}
            </table>
            
        """)


class CheckInternetConnectivityPlugin(BasePlugin):
    """
        This plugin determines whether the local machine has access to the internet
    """

    def __init__(self):
        super().__init__("Internet Connectivity Plugin", Category.INFO, "Velislav V", 1.0,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])

    @property
    def template(self) -> Template:
        return Template("""
            {% if internet %}
            <b>You are connected to the Internet !</b>
            {% else %}
            <b>No Internet Connection Present !</b>
            {% endif %}
        """)

    @property
    def execute(self) -> {}:
        return self.check_internet()

    @staticmethod
    def check_internet():
        """
        Function is used to return whether the local machine has internet access

        Works by looping through multiple URL's and connecting to them, if one successfully connects
        it will return True, otherwise False

        :return: True/False
        """
        urls = ["https://google.co.uk", "https://youtube.com", "https://bbc.co.uk"]
        for url in urls:
            try:
                urlopen(url, timeout=5)
                return {"internet": True}
            except URLError as Error:
                continue

        return {"internet": False}


class NetstatInformation(BasePlugin):
    """
        The plugin returns netstat information

        This tells you about the different connections and information about them such as
        the protocol, local address, remote address, status, PID and the program name
    """

    def __init__(self):
        super().__init__("Netstat Information", Category.INFO, "Owen", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])

    def execute(self) -> {}:
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

    @property
    def template(self) -> Template:
        """
        returns a template that will print all information using jinja2 loops
        """
        return Template("""
            <h3> Network Connections </h3>
            <table>
                <tr>
                    <th>#</th>
                    <th>Protocol</th>
                    <th>Local Address</th>
                    <th>Remote Address</th>
                    <th>Status</th>
                    <th>PID</th>
                    <th>Program Name</th>
                </tr>
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
            </table>
        """)


if __name__ == '__main__':
    p = NetstatInformation()
    d = p.execute()
    print(p.template.render(d))
