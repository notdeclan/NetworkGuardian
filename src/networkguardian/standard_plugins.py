import csv
import os
import platform
import time
import subprocess
import urllib
import uuid
from io import StringIO
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


class UserEnumerationPlugin(BasePlugin):

    """
    Plugin to enumerate users - as of 11/02/2020 does not work on Mac
    """

    def __init__(self):
        super().__init__("Example", Category.ATTACK, "Declan W", 0.1,
                         [Platform.MAC_OS, Platform.WINDOWS, Platform.LINUX])

    @property
    def template(self) -> Template:
        operating_system = Platform.detect()
        if operating_system is Platform.WINDOWS:
            return Template("""
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
        elif operating_system is Platform.LINUX:
            return Template("""
            
            """)

    # noinspection PyUnresolvedReferences
    @property
    def execute(self) -> {}:
        return self.user_enumeration()

    @staticmethod
    def user_enumeration():
        operating_system = Platform.detect()

        if operating_system is Platform.WINDOWS:

            # currently dumping all info for all users
            #    $options =
            #       AccountType, Description, Disabled, Domain, InstallDate, LocalAccount, Lockout,
            #       PasswordChangeable, PasswordExpires, PasswordRequired, SID, SIDType, and Status
            # adds line of whitespace to start of file

            process = subprocess.Popen(["wmic", "useraccount", "list", "full", "/format:csv"], stdout=subprocess.PIPE)
            users_output = process.communicate()[0]
            file_stream = StringIO(users_output.decode())
            for i in range(2):
                file_stream.readline()

            reader = csv.reader(file_stream)

            return {"reader": reader}

        elif operating_system is Platform.LINUX:
            # user + group
            import grp
            users = {}
            for p in psutil.pwd.getpwall():
                users[p[0]] = grp.getgrgid(p[3])[0]
            return users
        # elif operating_system is Platform.MAC_OS:
        #     import grp
        #     users = {}
        #     for p in psutil.pwd.getpwall():
        #         users[p[0]] = grp.getgrgid(p[3])[0]
        # return {}


if __name__ == '__main__':
    p = UserEnumerationPlugin()
    print(p.template.render(p.execute))
