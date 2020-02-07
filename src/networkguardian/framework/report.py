import base64
import json
import platform
from datetime import datetime

from networkguardian import application_version
from networkguardian.framework.plugin import SystemPlatform, AbstractPlugin

# KEY == file path,  VALUE == Report obj
reports = {}


class PluginResult:
    """
    Potentially temporary way of storing a plugin result
    """

    def __init__(self, plugin: AbstractPlugin):
        self.plugin = plugin
        self.exception = None
        self.data = None
        self.template = None

    def add_exception(self, exception):
        self.exception = exception

    def add_data(self, data, template):
        self.data = data
        self.template = template


class Report:
    """
        Object used to store the result of a scan when initiated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...

        essentially a model probably convert this to just a dict at some point when its completely figured out
    """

    def __init__(self, scan_name):
        self.date = str(datetime.now())
        self.scan_name = scan_name
        self.system_name = platform.node()
        self.system_platform = SystemPlatform.detect()
        self.software_version = application_version

        self.results = []

    def __repr__(self):
        return f"Report(scan_name={self.scan_name}, system_name={self.system_name})"

    def add_result(self, result: PluginResult):
        if isinstance(result, PluginResult):
            self.results.append(result)
        else:
            raise ValueError("result should be an instance of Result")

    def add_results(self, results: [PluginResult]):
        for result in results:
            self.add_result(result)

    def store(self, path):
        print("starting store")
        data = {
            'date': self.date,
            'system_name': self.system_name,
            'system_platform': self.system_platform.name,
            'software_version': self.software_version,
            'plugins': {}
        }

        for result in self.results:
            print("attempting as result")
            print(result.template)
            rendered_template = result.template.render(result.data).encode()
            encoded_pickle = base64.b64encode(rendered_template)
            data['plugins'][result.plugin.name] = {
                'version': result.plugin.name,
                'author': result.plugin.author,
                'template': str(encoded_pickle)
            }

        with open(path, 'w') as f:
            print("writing oit")
            json.dump({self.scan_name: data}, f)