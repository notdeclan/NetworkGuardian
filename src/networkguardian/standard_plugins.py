import os
import platform
import time
import uuid

import psutil
from jinja2 import Template

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
        super().__init__("Example", Category.ATTACK, "Declan W", 0.1, [Platform.MAC_OS, Platform.WINDOWS])

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
        time.sleep(4)
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
        Plugin returns
    """

    def __init__(self, sleep_time):
        super().__init__("Network Interface Information", Category.INFO, "Owen", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])
        self.sleep_time = sleep_time

    def execute(self) -> {}:
        """Takes network interfaces using psutil and puts into list"""
        address = psutil.net_if_addrs()
        adapter_names = list(address.keys())
        i = 0
        x = 1
        nested_dict = {}
        while i < len(adapter_names):
            length = len(address[adapter_names[i]])
            if length == 3:
                nested_dict.update({adapter_names[i]: {'Mac': address[adapter_names[i]][0][1],
                                    'IP': address[adapter_names[i]][1][1]}})
            elif length != 3:
                nested_dict.update({adapter_names[i]: {'Address1': address[adapter_names[i]][0][1]}})
                while x < length:
                    key = "Address" + str(x + 1)
                    nested_dict[adapter_names[i]].update({key: address[adapter_names[i]][x][1]})
                    x += 1
            i += 1

        return nested_dict

    @property
    def template(self) -> Template:
        return Template("""
                    <table>
                        {% for name, value in nested_dict.items() %}
                        <tr>
                            <td>{{name}}</td>
                            <td>{{value}}</td>
                        </tr>
                        {% endfor %}
                    </table>
                """)


if __name__ == '__main__':
    """p = ExamplePlugin()
    print(p.__doc__)"""
    p = NetworkInterfaceInformation(1)
    result = p.execute()
    template = p.template.render(result)
    print(template)
