import os
import pickle
import platform
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from threading import Thread

from jinja2 import Template

from networkguardian import application_version, reports_directory
from networkguardian.exceptions import PluginProcessingError
from networkguardian.framework.plugin import SystemPlatform, PluginStructure
from networkguardian.framework.registry import get_thread_count

# KEY == file path,  VALUE == Report obj

reports = {}

# Thread ID, Report obj
processing_reports = {}

report_filename_template = "{{ name }} ({{ system_name }}/{{ platform }}) {{date}} {{time}}"


class Result(PluginStructure):

    def __init__(self, plugin, data=None, exception=None, template=None):
        super().__init__(plugin.name, plugin.category, plugin.author, plugin.version)
        self.description = plugin.description

        self.data = data
        self.exception = exception
        self.template = template

        if exception is None:
            if template is None:
                self.exception = PluginProcessingError("No plugin template was found")
            if data is None:
                self.exception = PluginProcessingError("Plugin returned no data to render")

    def render(self):
        return Template(self.template).render(self.data)


class Report:
    """
        Object used to store the result of a scan when initiated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...

        essentially a model probably convert this to just a dict at some point when its completely figured out
    """

    def __init__(self, name):
        self.date = datetime.now()
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


def store_report(report: Report):
    report_filename = Template(report_filename_template).render({
        "name": report.name,
        "system_name": report.system_name,
        "platform": report.system_platform,
        "date": report.date
    })

    report_path = os.path.join(reports_directory, '.'.join((report_filename, '.rng')))

    with open(report_path, "wb") as fw:
        data = pickle.dumps(report)
        fw.write(data)


def name_settings(template: str):
    template = Template(template)
    name = template.render()


def load_reports():
    for root, dirs, files in os.walk(reports_directory):
        for file in files:
            print(f"Found file {file}")
            if file.endswith('.rng'):
                print(f"Found potential report file {file}")
                report_pickle = pickle.load(open(os.path.join(reports_directory, file), "rb"))
                print(f"Opened potential report file {file}")
                if isinstance(report_pickle, Report):
                    reports[report_pickle.name] = report_pickle
                    print(f"Loaded report {report_pickle.name}")
                else:
                    print(f"Dodgy shit {file}")


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
