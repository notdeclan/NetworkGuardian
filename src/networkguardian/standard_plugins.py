import os
import platform
import subprocess
import time
import urllib
import uuid
from urllib.error import URLError
from urllib.request import urlopen

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


class LocalFirewallStatus(BasePlugin):
    """
        This plugin determines whether the local machine has firewall turned on or off

        Function is used to return whether the local machine has firewall turned on or off

        Works by looping through multiple commands for different OS and if firewall is on, it will return True, otherwise it will return False

        :return: True/False
    """

    @property
    def template(self) -> Template:
        os = Platform.detect()
        if os is Platform.MAC_OS:
            return Template("""
                {% if firewall %}
                    Firewall Enabled
                {% elif False %}
                    Firewall Disabled
                {% elif None %}
                    Unable to Detect
                {% endif %}
            """)
        elif os is Platform.WINDOWS:
            return Template("""
                <table>
                    <thead>
                        <tr>
                            <th>Firewall</th>
                            <th>Enabled</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for firewall, state in results.items() %}
                            <tr>
                                <td>{{ firewall }}</td>
                                <td>{{ state }}</td>
                            </tr>
                        {% endfor %}
                    </tbody>
                </table>
           """)
        elif os is Platform.LINUX:
            return False


    def __init__(self):
        super().__init__("Local Firewall Status Plugin", Category.INFO, "Velislav V", 0.1,
                         [Platform.WINDOWS, Platform.LINUX, Platform.MAC_OS])

    @property
    def execute(self) -> {}:
        os = Platform.detect()
        if os is Platform.MAC_OS:
            return {"firewall": self.check_mac_os()}
        elif os is Platform.WINDOWS:
            return {"results": self.check_windows()}
        elif os is Platform.LINUX:
            return False

    @staticmethod
    def check_mac_os():
        """
        Mac OS X Firewall Checker
        """
        process = subprocess.Popen(["defaults", "read", "/Library/Preferences/com.apple.alf", "globalstate"],
                                   stdout=subprocess.PIPE)
        return bool(int(process.communicate()[0].rstrip()))


    @staticmethod
    def check_windows():
        """
        Windows Firewall Checker
        """
        process = subprocess.Popen(["netsh", "advfirewall", "show", "allprofiles", "state"], stdout=subprocess.PIPE)
        """ Checks whether or not the Firewall State is ON or OFF and Returns the result in a table. """
        output = process.communicate()[0].decode()
        lines = output.split("\n")
        domain = "ON" in lines[3]
        private = "ON" in lines[7]
        public = "ON" in lines[11]

        return {"Domain": domain, "Private": private, "Public": public}


if __name__ == '__main__':
    p = LocalFirewallStatus()
    print(p.template.render(p.execute))
