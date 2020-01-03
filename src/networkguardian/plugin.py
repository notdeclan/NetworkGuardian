import platform
from abc import abstractmethod
from enum import Enum

from src.networkguardian import log


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
        Return's correct Platform enum for the running operating system
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


class BasePlugin:

    def __init__(self, name: str, description: str, author: str, version: float, supported_platforms: []):
        # Plugin Information
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.supported_platforms = supported_platforms

        # Running information
        self._platform_support = False

    def __repr__(self):
        return 'Plugin(name=%r, description=%r, author=%r, version=%r)' \
               % (self.name, self.description, self.author, self.version)

    def load(self, platform):
        """
        Function is used to load running environment variables, and call initialization functions in derived plugins
        when loaded into the Plugin Manager.

        Do not override this function, if a plugin requires additional functionality when being loaded, the initialize()
        function should be used.
        """
        self._platform_support = True if platform in self.supported_platforms else False # update supported variable

        log.debug(f'Attempting to initialize {self.name} plugin')
        self.initialize()
        log.debug(f'Initialized {self.name} plugin')

    def initialize(self):
        """
        If a derived plugin class requires additional functionality when being initialized such as checking the system
        for application based requirements, this function should be overridden.

        This function is always called when a plugin is loaded into the Plugin Manager
        """
        pass

    def process(self):
        if self.supported: # further check to ensure somehow the plugin isn't executed if it is unsupported
            self.execute()

    @abstractmethod
    def execute(self):
        pass

    @property
    def supported(self) -> bool:
        return self._platform_support


class PluginInitializationError(Exception):
    pass


class ExamplePlugin(BasePlugin):

    def __init__(self):
        super().__init__("Example", "Example Description", "Declan W", 0.1,
                         [Platform.WINDOWS, Platform.MAC_OS])

    def execute(self):
        print("EXAMPLE")

    def initialize(self):
        if "test" not in "test":
            raise PluginInitializationError("Test was not in test, so the plugin could not be initialized properly")


