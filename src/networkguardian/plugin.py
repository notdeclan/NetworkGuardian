import inspect
import os
import platform
from abc import abstractmethod
from enum import Enum

import psutil
from jinja2 import Template

from networkguardian import log
from networkguardian.exceptions import PluginInitializationError

""" 
    TODO: When installing, processing a plugin, use sys.modules[__name__] to get the list of packages required by the 
    plugin, then check if it is installed on the system, attempt to include the plugin and if it raises a ImportError,
    throw an error to the user asking them to install the module to the running python environment

    OR ...
    
    Create a plugin installation erorr, and provide documentation in the exception which can be displayed in the GUI.
    For example, if import error is given because the plugin requires uninstalled python package, display "Plugin 
    requires extra installation, python package "psutil" requires installation. 
"""


class Platform(Enum):
    """
    Enum class to used by Network Guardian to determine the running operating system, and to be used to specify platforms
    are supported by plugins.

    Be careful not to confuse with Pythons in-built platform module
    """

    WINDOWS = 'Windows'
    LINUX = 'Linux'
    MAC_OS = 'Darwin'

    @staticmethod
    def detect() -> Enum:
        """
        Function return's correct Platform enum for the running operating system
        """
        system = platform.system()  # get system tag
        return Platform(system)

    def __str__(self):
        """
        Returns string representation of enum

        Example: str(Platform.WINDOWS) == 'Windows'

        :return: string representation of enum
        """
        return self.value


class Category(Enum):
    """
    Enum is used to differentiate between plugin types
    """
    INFO = 'Informational'
    SCANNER = 'Scanner'
    ATTACK = 'Attack'
    OTHER = 'Other'


class BasePlugin:

    def __init__(self, name: str, category: Category, author: str, version: float, supported_platforms: [],
                 required_python_packages=...):
        # Required Plugin Information
        self.name = name
        self.category = category
        self.description = inspect.cleandoc(self.__doc__) if self.__doc__ else "No description available."
        self.author = author
        self.version = version
        self.supported_platforms = supported_platforms
        # Additional Plugin Information
        self.required_python_packages = []
        # Running information
        self._platform_support = False

    def __repr__(self):
        return 'Plugin(name=%r, description=%r, author=%r, version=%r)' \
               % (self.name, self.description, self.author, self.version)

    def load(self, running_platform):
        """
        Function is used to load running environment variables, and call initialization functions in derived plugins
        when loaded into the Plugin Manager.

        Do not override this function, if a plugin requires additional functionality when being loaded, the initialize()
        function should be used.
        """
        self._platform_support = True if running_platform in self.supported_platforms else False  # update supported variable

        log.debug(f'Attempting to initialize {self.name} plugin')
        self.initialize()
        log.debug(f'Initialized {self.name} plugin')

    @property
    @abstractmethod
    def template(self) -> Template:
        return Template()

    @abstractmethod
    def execute(self) -> {}:
        """
        Function is to be overridden by subclasses to provide the functionality for the plugin and should return the
        information required to appropriately display the plugin Template
        :return: dictionary containing result values
        """
        return {}

    def initialize(self):
        """
        If a derived plugin class requires additional functionality when being initialized such as checking the system
        for application based requirements, this function should be overridden.

        This function is always called when a plugin is loaded into the Plugin Manager
        """
        ...

    def process(self):
        if self.supported:  # further check to ensure somehow the plugin isn't executed if it is unsupported
            self.execute()
        else:
            raise EnvironmentError("Running platform is not supported by %r" % self)

    @property
    def supported(self) -> bool:
        return self._platform_support


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