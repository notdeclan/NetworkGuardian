import time
import uuid
from os.path import dirname, join
from random import randint

from jinja2 import Template

from networkguardian.exceptions import PluginInitializationError
from networkguardian.framework.plugin import AbstractPlugin, PluginCategory, executor, SystemPlatform
from networkguardian.framework.registry import register_plugin


@register_plugin("Test", PluginCategory.INFO, "Declan W", 1.0)
class TestPlugin(AbstractPlugin):
    """
    Plugin returns a random UUID and sleeps the thread for a random duration from 1 second to 4.
    """

    def initialize(self):
        raise PluginInitializationError("Testing this shit boi")

    sleep_time = randint(1, 4)

    @executor(Template("UUID: {{uuid}}, Slept for: {{sleep}}"), SystemPlatform.WINDOWS)
    def execute(self):
        time.sleep(self.sleep_time)
        return {
            "uuid": uuid.uuid4(),
            "sleep": self.sleep_time
        }


@register_plugin("Template File Test", PluginCategory.INFO, "Declan W", 1.0)
class TemplateFilePlugin(AbstractPlugin):

    @executor(Template(open(join(dirname(__file__), "test_template.html")).read()))
    def execute(self):
        time.sleep(1)
        return {
            "uuid": uuid.uuid4(),
            "sleep": 1
        }
