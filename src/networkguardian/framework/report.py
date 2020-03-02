import os
import pickle
import platform
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from random import randint
from threading import Thread

from flask import render_template
from jinja2 import Template

from networkguardian import application_version, reports_directory, logger
from networkguardian.exceptions import PluginProcessingError
from networkguardian.framework.plugin import SystemPlatform, PluginInformation, AbstractPlugin
from networkguardian.framework.registry import get_thread_count

reports = []  # Used to store all Report obj's
processing_reports = {}  # Thread ID, Report obj

report_filename_template = "{{ name }} ({{ system_name }} | {{ platform }}) {{ date }}"
report_extension = 'rng'


class PluginResult(PluginInformation):

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
        self.path = None

    def __repr__(self):
        return f"Report(name='{self.name}', system_name='{self.system_name}', system_platform='{self.system_platform}', date='{self.date}')"

    def add_result(self, plugin, data, template):
        self.results.append(PluginResult(plugin, data=data, template=template))

    def add_exception(self, plugin, exception):
        self.results.append(PluginResult(plugin, exception=exception))


def load_reports():
    for root, dirs, files in os.walk(reports_directory):
        for file in files:
            if file.endswith(report_extension):
                import_report(os.path.join(reports_directory, file))


def import_report(report_path: str):
    try:
        report_pickle = pickle.load(open(report_path, "rb"))
        if isinstance(report_pickle, Report):
            report_pickle.path = report_path
            reports.append(report_pickle)
            logger.debug(f'Successfully imported {report_pickle}')
    except AttributeError:
        logger.debug(f'Failed to import {report_path} due to missing dependency')


def store_report(report: Report):
    export_path = export_report(report)  # export report to file and get path
    reports.append(report)  # add report to list
    report.path = export_path  # update path

    return len(reports) - 1  # return index of report in list


def export_report(report: Report):
    report_filename = Template(report_filename_template).render({
        "name": report.name,
        "system_name": report.system_name,
        "platform": report.system_platform,
        "date": report.date
    })

    report_path = os.path.join(reports_directory, '.'.join((report_filename, report_extension)))

    with open(report_path, "wb") as fw:
        data = pickle.dumps(report)
        fw.write(data)

    return report_path


def export_report_as_html(report: Report, path: str):
    export_template = render_template("layouts/export.html", report=report)
    # TODO add exception handling for permission errors, file exists, e.t.c...
    with open(path, "w") as f:
        f.write(export_template)


def start_report(report_name: str, plugins: [AbstractPlugin]) -> str:
    processor = ReportProcessor(report_name, plugins)
    processor.daemon = True
    processor.start()

    thread_id = randint(0, 10000)
    processing_reports[thread_id] = processor

    return thread_id


class ReportProcessor(Thread):

    def __init__(self, report_name, plugins):
        self.report = Report(report_name)
        self.plugins = {}

        for plugin in plugins:
            self.plugins[plugin] = False

        self.report_id = None

        super().__init__()

    def run(self):
        plugin_count = len(self.plugins)
        thread_count = get_thread_count(max_required=plugin_count)

        # starting threads within another thread :^) wizardry
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
                    self.report.add_result(plugin, data, template)
                except Exception as ppe:
                    self.report.add_exception(plugin, ppe)

        self.report_id = store_report(self.report)

    @property
    def progress(self):
        return len([status for status in self.plugins.values() if status]) * (100 / len(self.plugins))
