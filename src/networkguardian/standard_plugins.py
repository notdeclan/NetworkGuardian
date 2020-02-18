import os
import platform
from urllib.error import URLError
from urllib.request import urlopen

import socket
import psutil
from jinja2 import Template

from networkguardian.exceptions import PluginInitializationError
from networkguardian.framework.plugin import AbstractPlugin, PluginCategory, SystemPlatform, executor
from networkguardian.framework.registry import register_plugin, test_plugin

import nmap

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
            <table>
                {% for name, value in information.items() %}
                <tr>
                    <td>{{name}}</td>
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


@register_plugin("NMap TCP Ports", PluginCategory.INFO, "Owen", 0.1)
#@test_plugin
class NMapTcpPorts(AbstractPlugin):
    """
        Blank
    """

    template = Template("""
        <table>
                <tr>
                    <th>Port</th>
                    <th>State</th>
                    <th>Reason</th>
                    <th>Name</th>
                    <th>Product</th>
                </tr>
                {% for name, value in results.items() %}
                <tr>
                    <td>{{name}}</td>
                    <td>{{value.State}}</td>
                    <td>{{value.Reason}}</td>
                    <td>{{value.Name}}</td>
                    <td>{{value.Product}}</td>
                </tr>
                {% endfor %}
            </table>
        """)

    @executor(template)
    def execute(self):

        nested_dict = {}
        new_dict = {}
        i = 0

        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)

        nm = nmap.PortScanner()
        a = nm.scan(ip_addr)
        nested_dict.update({'tcp': {'Port': a['scan'][ip_addr]['tcp']}})
        keys = nested_dict['tcp']['Port'].keys()
        keys = list(keys)

        while i < len(keys):
            new_dict.update({keys[i]: {'State': nested_dict['tcp']['Port'][keys[i]]['state'],
                                       'Reason': nested_dict['tcp']['Port'][keys[i]]['reason'],
                                       'Name': nested_dict['tcp']['Port'][keys[i]]['name'],
                                       'Product': nested_dict['tcp']['Port'][keys[i]]['product']

                                       }})
            i += 1

        return {'results': new_dict}

#@register_plugin("NMapNetworkScan", PluginCategory.INFO, "Owen", 0.1)
@test_plugin
class NMapNetworkScan(AbstractPlugin):
    """
        Blank
    """

    template = Template("""
        <table>
                <tr>
                    <th>IP</th>
                    <th>MAC</th>
                    <th>Vendor</th>
                    <th>OS - Estimation</th>
                    <th>Closed Ports</th>
                    <th>Filtered Ports</th>
                    <th>Open Ports</th>
                </tr>
                {% for name, value in results.items() %}
                <tr>
                    <td>{{name}}</td>
                    <td>{{value.mac}}</td>
                    <td>{{value.vendor}}</td>
                    <td>{{value.os}}</td>
                    <td>{{value.closed}}</td>
                    <td>{{value.filtered}}</td>
                    <td>{{value.open}}</td>
                </tr>
                {% endfor %}
            </table>
        """)

    @executor(template)
    def execute(self):

        temp_dict = {}
        new_dict = {}
        i = 0
        open_list = []
        filtered_list = []
        closed_list = []

        hostname = socket.gethostname()
        ip_addr = socket.gethostbyname(hostname)

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()

        split = ip.split('.')
        new_ip = split[0] + '.' + split[1] + '.' + split[2] + '.*'

        print(new_ip)

        nm = nmap.PortScanner()
        temp_dict = nm.scan(hosts='172.16.16.1-20', arguments='-O --top-ports 20')

        keys = temp_dict['scan'].keys()
        keys = list(keys)

        while i < len(keys):
            if keys[i] == ip:
                pass
            else:
                mac = temp_dict['scan'][keys[i]]['addresses']['mac']
                try:
                    vendor = temp_dict['scan'][keys[i]]['vendor'][mac]
                except KeyError:
                    vendor = "-"

                try:
                    oss = temp_dict['scan'][keys[i]]['osmatch'][0]['name']
                except IndexError:
                    oss = "Unknown"

                keys2 = temp_dict['scan'][keys[i]]['tcp'].keys()
                keys2 = list(keys2)

                x = 0
                while x < len(keys2):
                    if temp_dict['scan'][keys[i]]['tcp'][keys2[x]]['state'] == "open":
                        open_list.append(keys2[x])
                    elif temp_dict['scan'][keys[i]]['tcp'][keys2[x]]['state'] == "filtered":
                        temp = temp_dict['scan'][keys[i]]['tcp'][keys2[x]]
                        print(keys2[x])
                        filtered_list.append(keys2[x])
                    else:
                        closed_list.append(keys2[x])

                    x += 1

                new_dict.update({keys[i]: {"mac": mac or '-',
                                           "vendor": vendor,
                                           "os": oss,
                                           "closed": closed_list,
                                           "filtered": filtered_list,
                                           "open": open_list
                                           }})
            i += 1
        print(new_dict)
        return {'results': new_dict}


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

        return {
            "internet": check_internet()
        }

