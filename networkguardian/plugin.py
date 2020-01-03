import platform
import time
from abc import abstractmethod
from enum import Enum

from networkguardian import log


class Platform(Enum):
    """
    Enum class to used by Network Guardian to determine the running operating system, and to be used to specify platforms
    are supported by plugins.

    Be careful not to confuse with Pythons in-built platform module
    """

    WINDOWS = 'Windows',
    LINUX = 'Linux',
    MAC_OS = 'Mac OS X',

    @staticmethod
    def detect() -> Enum:
        """
        Return's correct Platform enum for the running operating system
        """
        if platform.system() == 'Windows':
            return Platform.WINDOWS
        elif platform.system() == 'Linux':
            return Platform.LINUX
        elif platform.system() == 'Darwin':
            return Platform.MAC_OS
        else:
            # realistically this should never happen, but if an absolute mad-lad decides to run on an unsupported os
            raise NotImplementedError('Running operating system platform is not supported')

    def __str__(self):
        """
        Returns string representation of enum

        Example: str(Platform.WINDOWS) == 'Windows'

        :return: string representation of enum
        """
        return self.value[0]


class PluginManager:

    def __init__(self):
        self._plugins = []


class BasePlugin:

    def __init__(self, name: str, description: str, author: str, version: float, supported_platforms: []):
        # Plugin Information
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.supported_platforms = supported_platforms
        # Running information
        self._supported = False

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
        self._supported = True if platform in self.supported_platforms else False
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

    @abstractmethod
    async def scan(self):
        pass

    @property
    def supported(self) -> bool:
        return self._supported


class ExamplePlugin(BasePlugin):

    def __init__(self):
        super().__init__("Example", "Example Description", "Declan W", 0.1,
                         [Platform.WINDOWS, Platform.MAC_OS])

    def scan(self):
        print("EXAMPLE")

    def initialize(self):
        print("just doin some initialization stuff")


if __name__ == '__main__':
    plugins = [ExamplePlugin()]
    for p in plugins:
        p.load(Platform.WINDOWS)

    print("STARTING SCANNING")
    for p in plugins:
        p.scan()
