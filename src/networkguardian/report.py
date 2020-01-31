import platform
from datetime import datetime

from jinja2 import Template

from networkguardian.plugin import Platform


class Result:
    """
    Potentially temporary way of storing a plugin result (could be maybe replaced with a
    """

    def __init__(self, plugin, result, template):
        self.plugin = plugin
        self.result = result
        self.template = template

    def render(self):
        return self.template.render(self.result)


def report_time():
    return datetime.now()


def report_platform():
    return Platform.detect().name


def report_system_name():
    return platform.node()


class Report:
    """
        Object used to store the result of a scan when initated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...
    """

    def __init__(self, scan_name, system_name, date, software_version):
        self.scan_name = scan_name
        self.system_name = system_name
        self.date = date
        self.software_version = software_version
        self.system_platform = None  # TODO: this

        self.results = []

    def render(self):
        # this function is probably temporary because rendering will be handled inside of the blueprint, however
        # for now this is adequate

        report_template = Template("""
            {% for result in results %}
                {{ result.render() }}
            {% endfor %}
        """)

        return report_template.render(results=self.results)

    def add_result(self, result: Result):
        self.results.append(result)