import inspect
import os
import platform
from enum import Enum

from networkguardian.exceptions import PluginUnsupportedPlatformError, PluginProcessingError, \
    PluginRequiresElevationError


class SystemPlatform(Enum):
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
        return SystemPlatform(system)

    def __str__(self):
        """
        Returns string representation of enum

        Example: str(Platform.WINDOWS) == 'Windows'

        :return: string representation of enum
        """
        return self.value

    def __repr__(self):
        return self.value


class PluginCategory(Enum):
    """
    Enum is used to differentiate between plugin types
    """
    INFO = 'Informational'
    NETWORK = 'Networking'
    ATTACK = 'Attack'
    ENUMERATION = 'Enumeration'
    SYSTEM = 'System'
    OTHER = 'Other'

    def __repr__(self):
        return self.value


def executor(template_path, *platforms: SystemPlatform, requires_elevation=False):
    """
        Decorators are called BEFORE class is built i.e __new__, so with a decorator we can tag the function with the
        supported platform e.t.c, and then post process it later with the base class
    """

    def decorator(fn):
        # add template attribute to function
        plugin_path = os.path.dirname(inspect.getfile(fn))
        fn._template = open(os.path.join(plugin_path, template_path)).read()
        fn._requires_elevation = requires_elevation

        if len(platforms) == 0:  # if no platform specified, automatically support all Platforms...
            fn._platforms = [p for p in SystemPlatform]
        else:
            fn._platforms = platforms  # add platform support attribute to function

        return fn

    return decorator


class MetaPlugin(type):
    """
        Metaclass modifies the class-creation behavior
    """

    def __new__(mcs, name, bases, attrs):
        executors = {}
        for fn_name, fn in attrs.items():  # for each NAME, FUNCTION in class
            if inspect.isfunction(fn):  # if it's a function
                supported_platforms = getattr(fn, '_platforms', None)  # if its been marked by the annotation get value
                if supported_platforms is not None:  # if there's some platforms supplied
                    for sp in supported_platforms:  # for each platform supplied
                        executors[sp] = fn

        attrs["_executors"] = executors

        return type.__new__(mcs, name, bases, attrs)


class PluginInformation:

    def __init__(self, name: str, category: PluginCategory, author: str, version: float):
        # Required Plugin Information
        self.name = name
        self.category = category
        self.description = inspect.cleandoc(self.__doc__) if self.__doc__ else "No description available."
        self.author = author
        self.version = version


class AbstractPlugin(PluginInformation, metaclass=MetaPlugin):
    _executors = {}  # suppress IDE errors but is patched with __new__ in metaclass

    def __init__(self, name: str, category: PluginCategory, author: str, version: float):
        super().__init__(name, category, author, version)

        self.loading_exception = None  # used to store any exception raised when load() is called to be displayed in GUI

        self._loaded = False  # used to signify whether a plugin has been successfully loaded
        self._running_platform = None  # used to store the system platform that is running

        self.execute = None  # used to store platform specific execute function
        self.template = None  # used to store platform specific template data

    def __repr__(self):
        return 'Plugin(name=%r, description=%r, author=%r, version=%r)' \
               % (self.name, self.description, self.author, self.version)

    def load(self, running_platform, running_elevated):
        """
        Function is used to load running environment variables, and call initialization functions in derived plugins
        when loaded into the Plugin Manager.

        Do not override this function, if a plugin requires additional functionality when being loaded, the initialize()
        function should be used.
        """
        self._running_platform = running_platform

        if not self.supported:
            raise PluginUnsupportedPlatformError(
                f'Plugin is only supported on {", ".join(str(x) for x in self.supported_platforms)}')

        self.initialize()  # call plugin's initialization method  MAY :raise: PluginInitializationError

        self.execute = self._executors[running_platform]  # monkey patch the function
        self.template = self.execute._template

        if self.execute._requires_elevation and not running_elevated:
            raise PluginRequiresElevationError("Plugin requires elevated system permissions to run")

        self._loaded = True  # update loaded variable

    @property
    def loaded(self) -> bool:
        return self._loaded

    def initialize(self):
        """
        If a derived plugin class requires additional functionality when being initialized such as checking the system
        for application based requirements, this function should be overridden.

        This function is always called when a plugin is loaded into the Plugin Manager
        """
        pass

    def process(self):
        if not self.loaded:  # further check to ensure somehow the plugin isn't executed if not loaded
            raise PluginProcessingError("Plugin must be loaded before processing.")

        return self.execute(self), self.template

    @property
    def supported(self) -> bool:
        return self._running_platform in self._executors

    @property
    def supported_platforms(self):
        return list(self._executors.keys())