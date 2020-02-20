import time
import uuid
from random import randint

from networkguardian.exceptions import PluginInitializationError
from networkguardian.framework.plugin import PluginCategory, AbstractPlugin, executor, SystemPlatform
from networkguardian.framework.registry import register_plugin


@register_plugin("Initialization Error", PluginCategory.OTHER, "Declan W", 1.0)
class InitializationErrorPlugin(AbstractPlugin):
    """
    Plugin is used to test the GUI, and Plugin class functionality

    If working correctly, the GUI should display a "Plugin Initialization Error" warning message when viewing the plugin, and the plugin should be disabled.

    The plugin works by throwing an exception during initialization.
    """

    def initialize(self):
        raise PluginInitializationError("This should be displayed in the GUI")

    @executor("template.html")
    def execute(self):
        return {}


@register_plugin("Unsupported Platform", PluginCategory.OTHER, "Declan W", 1.0)
class UnsupportedPlatformPlugin(AbstractPlugin):
    """
    Plugin is used to test the GUI, and Plugin class functionality

    If working correctly, the GUI should display a "Unsupported Platform Error" warning message when viewing the plugin, and the plugin should be disabled.

    The plugin works by detecting the current platform, and then only supporting the others.
    """

    # loop through platforms and return list of all platforms other that running one
    supported_platforms = [platform for platform in SystemPlatform if platform is not SystemPlatform.detect()]

    @executor("template.html", *supported_platforms)
    def execute(self):
        return {}


@register_plugin("Execution Exception", PluginCategory.OTHER, "Declan W", 1.0)
class ExecutionExceptionPlugin(AbstractPlugin):
    """
    Plugin is used to test the GUI, and Plugin class functionality

    If working correctly, the GUI should display a "Unsupported Platform Error" warning message when viewing the plugin, and the plugin should be disabled.

    The plugin works by detecting the current platform, and then only supporting the others.
    """

    @executor("template.html")
    def execute(self):
        raise Exception("uh oh")


@register_plugin("No Executor Exception", PluginCategory.OTHER, "Declan W", 1.0)
class NoExecutorExceptionPlugin(AbstractPlugin):
    """
    Plugin is used to test the GUI, and Plugin class functionality

    If working correctly, the GUI should display "No executor found" message when viewing the plugin, and the plugin should be disabled.
    """
    ...


@register_plugin("Sleep Plugin", PluginCategory.OTHER, "Declan W", 1.0)
class SleepPlugin(AbstractPlugin):
    """
    Plugin returns a random UUID and sleeps the thread for a random duration from 1 second to 4.
    """

    @executor("sleep.template.html")
    def execute(self):
        sleep_time = randint(1, 4)  # generate sleep time
        time.sleep(sleep_time)  # sleep

        return {
            "uuid": uuid.uuid4(),  # generate random uuid
            "sleep": sleep_time  # return sleep time
        }
