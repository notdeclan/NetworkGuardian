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

import winreg as wr
import netifaces
from netaddr import IPNetwork
import ipaddress

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
# @test_plugin
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


# @register_plugin("NMapNetworkScan", PluginCategory.INFO, "Owen", 0.1)
@test_plugin
class NMapNetworkScan(AbstractPlugin):
    """
        Blank
    """

    template = Template("""
        <table>
                <tr>
                    <th>IP</th>
                    <th>Host Name</th>
                    <th>MAC</th>
                    <th>Vendor</th>
                    <th>OS - Estimation</th>
                    <th>TCP - Closed Ports</th>
                    <th>TCP - Filtered Ports</th>
                    <th>TCP - Open Ports</th>
                    <th>UDP - Closed Ports</th>
                    <th>UDP - Filtered Ports</th>
                    <th>UDP - Open Filtered Ports</th>
                    <th>UDP - Open Ports</th>
                </tr>
                {% for name, value in results.items() %}
                <tr>
                    <td>{{name}}</td>
                    <td>{{value.hostname}}</td>
                    <td>{{value.mac}}</td>
                    <td>{{value.vendor}}</td>
                    <td>{{value.os}}</td>
                    <td>{{value.tcp_closed}}</td>
                    <td>{{value.tcp_filtered}}</td>
                    <td>{{value.tcp_open}}</td  
                    <td>{{value.udp_closed}}</td>
                    <td>{{value.udp_filtered}}</td>
                    <td>{{value.udp_open_filtered}}</td  
                    <td>{{value.udp_open}}</td  
                </tr>
                {% endfor %}
            </table>
        """)

    @executor(template)
    def execute(self):

        temp_dict = {}
        new_dict = {}
        i = 0
        e = 0
        networks = {}

        for interface_name, interfaces in psutil.net_if_addrs().items():
            for interface in interfaces:

                # Validate
                try:
                    if ipaddress.IPv4Address(interface.address).is_loopback:  # if loopback
                        continue  # goto next one
                except ValueError:  # not valid ip address
                    continue  # goto next one
                ipn = IPNetwork(f"{interface.address}/{interface.netmask}")
                networks[interface_name] = [ipn[0], ipn.broadcast, interface.address, interface.netmask, ipn.cidr, ipn._prefixlen,
                                            ipn.cidr.size]

        current_ip = networks['Wi-Fi'][2]
        network_addr = str(networks['Wi-Fi'][4])
        print(networks['Wi-Fi'])
        print(networks)

        nm = nmap.PortScanner()
        temp_dict = nm.scan(hosts=network_addr, arguments='-O -sU -sT --top-ports 20')

        keys = temp_dict['scan'].keys()
        keys = list(keys)

        while i < len(keys):
            print(i)
            open_list, filtered_list, closed_list = [], [], []
            udp_open_list, udp_openfil_list, udp_filtered_list, udp_closed_list = [], [], [], []
            if keys[i] == current_ip:
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

                try:
                    hostname = temp_dict['scan'][keys[i]]['hostnames'][0]['name']
                except IndexError:
                    hostname = "Unknown"

                try:
                    keys2 = temp_dict['scan'][keys[i]]['tcp'].keys()
                    keys2 = list(keys2)
                except KeyError:
                    keys2 = 'Nothanks'

                x = 0

                if keys2 != 'Nothanks':
                    while x < len(keys2):
                        if temp_dict['scan'][keys[i]]['tcp'][keys2[x]]['state'] == "open":
                            open_list.append(keys2[x])
                        elif temp_dict['scan'][keys[i]]['tcp'][keys2[x]]['state'] == "filtered":
                            temp = temp_dict['scan'][keys[i]]['tcp'][keys2[x]]
                            filtered_list.append(keys2[x])
                        else:
                            closed_list.append(keys2[x])
                        x += 1
                else:
                    open_list, filtered_list, closed_list = 'No Ports', 'No Ports', 'NoPorts'

                try:
                    keys3 = temp_dict['scan'][keys[i]]['udp'].keys()
                    keys3 = list(keys3)
                except KeyError:
                    keys3 = 'Nothanks'

                h = 0
                if keys3 != 'Nothanks':
                    while h < len(keys3):
                        if temp_dict['scan'][keys[i]]['udp'][keys3[h]]['state'] == "open":
                            udp_open_list.append(keys3[h])
                        elif temp_dict['scan'][keys[i]]['udp'][keys3[h]]['state'] == "open|filtered":
                            udp_openfil_list.append(keys3[h])
                        elif temp_dict['scan'][keys[i]]['udp'][keys3[h]]['state'] == "filtered":
                            temp = temp_dict['scan'][keys[i]]['udp'][keys3[h]]
                            udp_filtered_list.append(keys3[h])
                        else:
                            udp_closed_list.append(keys3[h])
                        h += 1
                else:
                    udp_open_list, udp_openfil_list, udp_filtered_list, udp_closed_list = 'No Ports', 'No Ports', \
                                                                                          'No Ports', 'No Ports'

                new_dict.update({keys[i]: {"mac": mac or '-',
                                           "vendor": vendor or '-',
                                           "os": oss,
                                           "tcp_closed": closed_list,
                                           "tcp_filtered": filtered_list,
                                           "tcp_open": open_list,
                                           "udp_closed": udp_closed_list,
                                           "udp_filtered": udp_filtered_list,
                                           "udp_open_filtered": udp_openfil_list,
                                           "udp_open": udp_open_list,
                                           "hostname": hostname or 'N/A'
                                           }})

            i += 1

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