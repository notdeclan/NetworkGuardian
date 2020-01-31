import platform
from datetime import datetime

from jinja2 import Template

from networkguardian import application_version
from networkguardian.plugin import Platform


class Result:
    """
    Potentially temporary way of storing a plugin result (could be maybe replaced with a
    """

    def __init__(self, plugin):
        self.plugin = plugin
        self.template = plugin.template
        self.data = None
        self.exception = None

    def add_exception(self, exception):
        self.exception = exception

    def add_data(self, data):
        self.data = data

    def render(self):
        return self.template.render(self.data)


# TODO: Finish These functions

def store_report(report):
    pass


def load_report(path):
    pass


def report_time():
    return str(datetime.now())


def report_platform():
    return Platform.detect().name


def report_system_name():
    return platform.node()


class Report:
    """
        Object used to store the result of a scan when initated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...
    """

    def __init__(self, scan_name):
        self.scan_name = scan_name
        self.system_name = report_system_name()
        self.date = report_time()
        self.software_version = application_version
        self.system_platform = None  # TODO: this

        self.results = []

    def render(self):
        # this function is probably temporary because rendering will be handled inside of the blueprint, however
        # for now this is adequate

        report_template = Template("""
            {% for result in results %}
                <h3>{{ result.plugin.name }}</h3>
                {{ result.render() }}
            {% endfor %}
        """)

        return report_template.render(results=self.results)

    def add_result(self, result: Result):
        if isinstance(result, Result):
            self.results.append(result)
        else:
            raise ValueError("result should be an instance of Result")

    def add_results(self, results: [Result]):
        for result in results:
            self.add_result(result)
