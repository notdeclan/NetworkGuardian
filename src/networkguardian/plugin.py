import inspect
import platform
from abc import abstractmethod
from enum import Enum

from jinja2 import Template

from networkguardian import log

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

