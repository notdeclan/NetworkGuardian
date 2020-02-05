import os
import platform
import time
import uuid
from random import randint
from urllib.error import URLError
from urllib.request import urlopen

import psutil
from jinja2 import Template

from networkguardian.exceptions import PluginInitializationError
from networkguardian.plugin import AbstractPlugin, Category, Platform
from networkguardian.registry import register_plugin

"""
    Module is used to store all the standard plugins
"""


@register_plugin
class ExamplePlugin(AbstractPlugin):
    """
        An example plugin to demonstrate the functionality and api to developers of custom plugins.

        This doc comment will be used by network guardian as the description for the plugin, and information
        relating to the description, requirements, and operational instructions should be stored here to be displayed.

        <b>HTML elements are supported, but major changes to formatting is discouraged.</b>
    """

    def __init__(self):
        super().__init__("Example", Category.ATTACK, "Declan W", 0.1,
                         [Platform.MAC_OS, Platform.WINDOWS, Platform.LINUX])

    def initialize(self):
        # Should a plugin require a dependency or further checks when loading, this should be done here.
        if "test" not in "test":
            # if a plugin for whatever reason cannot be loaded, PluginInitializationError should be raised
            raise PluginInitializationError("Test was not in test, so the plugin could not be initialized properly")

    def execute(self) -> {}:
        # Do plugin execution here, IE scan or produce results from some data source
        # Then data should be formatted into a dictionary used for storage, and for rendering in the plugin template
        return {
            "results": {
                1: "Example Result",
                2: "Another Result"
            },
        }

    @property
    def template(self) -> Template:
        # The plugins Jinja template should be returned here
        # Data that is returned from execute should be rendered here
        # For more information on how Jinja templating works, see https://jinja.palletsprojects.com/en/2.11.x/templates/
        return Template("""
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


@register_plugin
class SystemInformationPlugin(AbstractPlugin):
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


@register_plugin
class TestPlugin(AbstractPlugin):
    """
    Plugin returns
    """

    def __init__(self):
        super().__init__("Test Plugin", Category.INFO, "Declan W", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])
        self.sleep_time = randint(1, 4)

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


@register_plugin
class NetworkInterfaceInformation(AbstractPlugin):
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
        address = psutil.net_if_addrs()
        online = psutil.net_if_stats()
        adapter_names = list(address.keys())
        i = 0
        nested_dict = {}
        """
            Loop through each adapter
        """
        while i < len(adapter_names):
            length = len(address[adapter_names[i]])
            name = adapter_names[i]
            """
                If adapter has 3 variables then it holds standard information so goes through this,
                Otherwise goes through the 2nd loop below that will dynamically add the information it stores
            """
            if length == 3:
                nested_dict.update({name: {'IsUp': online[name][0],
                                           'Mac': address[name][0][1],
                                           'IP': address[name][1][1],
                                           'Broadcast': address[name][1][3],
                                           'Netmask': address[name][1][2]}})
            elif length != 3:
                nested_dict.update({name: {'Address': address[name][0][1],
                                           'Broadcast': address[name][0][3],
                                           'Netmask': address[name][0][2]}})
            i += 1

        return {
            "result": nested_dict
        }

    @property
    def template(self) -> Template:
        return Template("""
            <h3> Network Interfaces </h3>
            <table>
                <thead>
                    <tr>
                        <th>Adapter Name</th>
                        <th>Is Up?</th>
                        <th>Mac</th>
                        <th>IP</th>
                        <th>Broadcast</th>
                        <th>Netmask</th>
                    </tr>
                </thead>
                <tbody>
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
                </tbody>
            </table>

            <h3> Non-Standard Interfaces </h3>
            <table>
                <thead>
                    <tr>
                        <th>Adapter Name</th>
                        <th>IP</th>
                        <th>Broadcast</th>
                        <th>Netmask</th>
                    </tr>
                </thead>
                <tbody>
                    {%- for name, value in result.items() -%}
                        {%- if value.Mac is undefined %}
                            <tr>
                                <td>{{name}}</td>
                                <td>{{value.Address}}</td>
                                <td>{{value.Broadcast}}</td>
                                <td>{{value.Netmask}}</td>
                            </tr>
                        {%- endif -%}
                    {%- endfor %}
                </thead>
            </table>
        """)


@register_plugin
class CheckInternetConnectivityPlugin(AbstractPlugin):
    """
        This plugin determines whether the local machine has access to the internet
    """

    def __init__(self):
        super().__init__("Internet Connectivity Plugin", Category.INFO, "Velislav V", 1.0,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])

    @property
    def template(self) -> Template:
        return Template("""
            System is {{ 'Connected' if internet else 'not Connected' }} to the Internet
        """)

    @property
    def execute(self) -> {}:
        status = self.check_internet()  # get internet status
        return {
            "internet": status
        }

    @staticmethod
    def check_internet() -> bool:
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
                continue  # if fail, go to next URL in loop

        return False  # if all URL's fail, return False
