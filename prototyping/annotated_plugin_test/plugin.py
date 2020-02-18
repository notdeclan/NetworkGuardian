from enum import Enum

from jinja2 import Template


class Platform(Enum):
    WINDOWS = 'w'
    LINUX = 'l'
    MAC_OS = 'm'


class Plugin:
    templates = {}
    executors = {}

    def __init__(self, name):
        self.name = name

    @classmethod
    def register_execute(cls, *platform):
        def decorator(f):
            for p in platform:
                cls.executors[p] = f

            return f

        return decorator

    @classmethod
    def register_template(cls, *platform):
        def decorator(f) -> Template:
            for p in platform:
                cls.templates[p] = f

            return f

        return decorator


class TestPlugin:
    __metadata__ = Plugin("Test Plugin")

    @Plugin.register_execute(Platform.WINDOWS)
    def windows_func(self):
        print("Test WINDOWS")

    @Plugin.register_execute(Platform.LINUX, Platform.MAC_OS)
    def nix_func(self):
        print("Test UNIX")

    @Plugin.register_template(Platform.WINDOWS)
    def windows_template(self):
        return Template("""LOL""")


class AnotherTestPlugin(Plugin):
    ref = None

    def __init__(self):
        global ref
        ref = self

        super().__init__("Another")

    @ref.register_execute(Platform.WINDOWS)
    def windows_func(self):
        print("Another WINDOWS")

    @ref.register_execute(Platform.LINUX, Platform.MAC_OS)
    def nix_func(self):
        print("Another UNIX")

    @ref.register_template(Platform.WINDOWS)
    def windows_template(self):
        return Template("""LOL""")


if __name__ == '__main__':
    t = TestPlugin()
    a = AnotherTestPlugin()
    a.executors[Platform.MAC_OS]("")
#
# plugin = Plugin("Test Plugin")
# @plugin.register_execute(Platform.MAC_OS)
# def mac():
#     print("MAC OS X")
#
#
# @plugin.register_execute(Platform.WINDOWS, Platform.LINUX)
# def windows():
#     print("WINDOWS/LINUX")
#
#
# @plugin.register_template(Platform.WINDOWS, Platform.MAC_OS)
# def windows_template():
#     return Template("""<b>Windows</b>""")
#
#
# @plugin.register_template(Platform.LINUX)
# def linux_t() -> Template:
#     return Template("""<b>Linux</b>""")
#
#
