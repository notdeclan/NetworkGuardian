import base64
import json
import platform
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from threading import Thread

from networkguardian import application_version
from networkguardian.framework.plugin import SystemPlatform
from networkguardian.framework.registry import get_thread_count

# KEY == file path,  VALUE == Report obj
reports = {}

# Report name, Report obj
processing_reports = {}


class Result:

    def __init__(self, plugin, data=None, exception=None, template=None):
        self.plugin = plugin
        self.data = data
        self.exception = exception
        self.template = template

    def render(self):
        return self.template.render(self.data)


class Report:
    """
        Object used to store the result of a scan when initiated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...

        essentially a model probably convert this to just a dict at some point when its completely figured out
    """

    def __init__(self, name):
        self.path = ""
        self.date = str(datetime.now())
        self.name = name
        self.system_name = platform.node()
        self.system_platform = SystemPlatform.detect()
        self.software_version = application_version

        self.results = []

    def __repr__(self):
        return f"Report(name={self.name}, system_name={self.system_name})"

    def add_result(self, plugin, data, template):
        self.results.append(Result(plugin, data=data, template=template))

    def add_exception(self, plugin, exception):
        self.results.append(Result(plugin, exception=exception))

    def store(self):
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

        with open(self.path, 'w') as f:
            print("writing oit")
            json.dump({self.name: data}, f)


class ReportProcessor(Thread):

    def __init__(self, report_name, plugins):
        self.report_name = report_name
        self.plugins = {}

        for plugin in plugins:
            self.plugins[plugin] = False

        self.progress = 0

        super().__init__()

    def run(self):
        plugin_count = len(self.plugins)
        thread_count = get_thread_count(max_required=plugin_count)
        report = Report(self.report_name)

        plugin_progress_worth = 100 / plugin_count

        with ThreadPoolExecutor(max_workers=thread_count) as tpe:
            # loop through all plugins, submit future for each one
            future_to_plugin = {
                tpe.submit(p.process): p for p in self.plugins.keys()
            }

            for future in futures.as_completed(future_to_plugin):
                plugin = future_to_plugin[future]
                self.plugins[plugin] = True
                try:
                    data, template = future.result()
                    report.add_result(plugin, data, template)
                except Exception as ppe:
                    report.add_exception(plugin, ppe)

                self.progress += plugin_progress_worth

                print(f"FINISHED {plugin.name} PROGRESS {self.progress}")

        # TODO: STORE
        # report.store()  # save to file
        reports[self.report_name] = report
