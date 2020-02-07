import time
import uuid
from random import randint

from jinja2 import Template

from networkguardian.framework.plugin import AbstractPlugin, Category, executor
from networkguardian.framework.registry import register_plugin


@register_plugin("Test Plugin", Category.INFO, "Declan W", 0.1)
class TestPlugin(AbstractPlugin):
    """
    Plugin returns
    """

    @executor(Template("UUID: {{uuid}}, Slept for: {{sleep}}"))
    def execute(self):
        sleep_time = randint(1, 4)
        time.sleep(sleep_time)
        return {
            "uuid": uuid.uuid4(),
            "sleep": sleep_time
        }
