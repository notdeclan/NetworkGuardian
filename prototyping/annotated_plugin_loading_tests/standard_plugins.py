from networkguardian.plugin import AbstractPlugin

from prototyping.annotated_plugin_loading_tests.registry import register_plugin


@register_plugin
class TestPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__("Test", "Cancer")


@register_plugin
class AnotherPlugin(AbstractPlugin):

    def __init__(self):
        super().__init__("Another", "Cancer")
