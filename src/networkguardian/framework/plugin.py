import inspect
import platform
from enum import Enum

from jinja2 import Template


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
    OTHER = 'Other'
    ATTACK = 'Attack'


"""
    Decorators are called BEFORE class is built i.e __new__, so with a decorator we can tag the function with the 
    supported platform e.t.c, and then post process it later with the base class
"""


def executor(template: Template, *platforms: Platform):
    def ret_fun(fn):
        fn._template = template

        if len(platforms) == 0:  # if no platform specified, automatically support all Platforms...
            fn._platforms = [p for p in Platform]
        else:
            fn._platforms = platforms

        return fn

    return ret_fun


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

    def __init__(self, name: str, category: Category, author: str, version: float):
        # Required Plugin Information
        self.name = name
        self.category = category
        self.description = inspect.cleandoc(self.__doc__) if self.__doc__ else "No description available."
        self.author = author
        self.version = version

        # Running information
        self._running_platform = None

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

        # log.debug(f'Attempting to initialize {self.name} plugin')
        self.initialize()
        # log.debug(f'Initialized {self.name} plugin')

    def initialize(self):
        """
        If a derived plugin class requires additional functionality when being initialized such as checking the system
        for application based requirements, this function should be overridden.

        This function is always called when a plugin is loaded into the Plugin Manager
        """
        pass

    def process(self):
        if self.supported:  # further check to ensure somehow the plugin isn't executed if
            pe = self._executors[self._running_platform]  # pe == platform executor
            return pe(self), pe._template
        else:  # TODO: change this to a plugin exception error, then again its kinda WTF because it shouldn't happen
            raise EnvironmentError("Running platform is not supported by %r" % self)

    @property
    def supported(self) -> bool:
        return self._running_platform in self._executors

    @property
    def supported_platforms(self):
        return list(self._executors.keys())


class PluginResult:
    """
    Potentially temporary way of storing a plugin result
    """

    def __init__(self, plugin: AbstractPlugin):
        self.plugin = plugin
        self.data, template = None
        self.exception = None

    def add_exception(self, exception):
        self.exception = exception

    def add_data(self, data):
        self.data = data

    def render(self):
        return self.template.render(self.data)
