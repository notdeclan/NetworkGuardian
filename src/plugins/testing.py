import time
import uuid
from random import randint

from jinja2 import Template

from networkguardian.exceptions import PluginInitializationError
from networkguardian.framework.plugin import AbstractPlugin, Category, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Test", Category.INFO, "Declan W", 1.0)
class TestPlugin(AbstractPlugin):
    """
    Plugin returns a random UUID and sleeps the thread for a random duration from 1 second to 4.
    """

    def initialize(self):
        raise PluginInitializationError("Testing this shit boi")

    sleep_time = randint(1, 4)

    @executor(Template("UUID: {{uuid}}, Slept for: {{sleep}}"))
    def execute(self):
        time.sleep(self.sleep_time)
        return {
            "uuid": uuid.uuid4(),
            "sleep": self.sleep_time
        }
