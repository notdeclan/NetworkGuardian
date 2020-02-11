import inspect
import platform
from enum import Enum

from jinja2 import Template

from networkguardian.exceptions import PluginUnsupportedPlatformError, PluginProcessingError


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


class PluginCategory(Enum):
    """
    Enum is used to differentiate between plugin types
    """
    INFO = 'Informational'
    SCANNER = 'Scanner'
    OTHER = 'Other'
    ATTACK = 'Attack'


def executor(template: Template, *platforms: SystemPlatform):
    """
        Decorators are called BEFORE class is built i.e __new__, so with a decorator we can tag the function with the
        supported platform e.t.c, and then post process it later with the base class
    """

    def decorator(fn):
        fn._template = template  # add template attribute to function

        if len(platforms) == 0:  # if no platform specified, automatically support all Platforms...
            fn._platforms = [p for p in SystemPlatform]
        else:
            fn._platforms = platforms  # add platform support attribute to function

        return fn

    return decorator


class MetaPlugin(type):

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


class AbstractPlugin(metaclass=MetaPlugin):
    _executors = {}  # suppress IDE errors but is replaced with __new__ in metaclass

    def __init__(self, name: str, category: PluginCategory, author: str, version: float):
        # Required Plugin Information
        self.name = name
        self.category = category
        self.description = inspect.cleandoc(self.__doc__) if self.__doc__ else "No description available."
        self.author = author
        self.version = version

        # Variables populated during runtime
        self._loaded = False  # used to signify whether a plugin has been successfully loaded
        self.loading_exception = None  # used to store any exception raised when load() is called to be displayed in GUI
        self._running_platform = None  # used to store the system platform that is running

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
        self._running_platform = running_platform

        if not self.supported:
            raise PluginUnsupportedPlatformError(f'Plugin is only supported on {self.supported_platforms}')

        self.initialize()  # call plugin's initialization method  MAY :raise: PluginInitializationError
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

    def process(self):  # TODO, MAKE THIS MUCH NICER
        if self.loaded:  # further check to ensure somehow the plugin isn't executed if
            pe = self._executors[self._running_platform]  # pe == platform executor
            return pe(self), pe._template
        else:  # TODO: change this to a plugin exception error, then again its kinda WTF because it shouldn't happen
            raise PluginProcessingError("Plugin must be loaded before processing.")

    @property
    def supported(self) -> bool:
        return self._running_platform in self._executors

    @property
    def supported_platforms(self):
        return list(self._executors.keys())

    def json(self) -> {}:
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "author": self.author,
            "version": self.version
        }