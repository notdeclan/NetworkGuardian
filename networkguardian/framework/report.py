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

from networkguardian import application_version, reports_directory, logger, threading_enabled
from networkguardian.exceptions import PluginProcessingError
from networkguardian.framework.plugin import SystemPlatform, PluginInformation, AbstractPlugin
from networkguardian.framework.registry import get_thread_count, usable_plugins

reports = []  # Used to store all Report obj's
processing_reports = {}  # Thread ID, Report obj

report_filename_template = "{{ name }} ({{ system_name }} - {{ platform }}) {{ date }}"
report_extension = 'rng'


class PluginResult(PluginInformation):

    def __init__(self, plugin: AbstractPlugin, data: {} = None, exception: Exception = None, template: str = None):
        super().__init__(plugin.name, plugin.category, plugin.author, plugin.version)
        # description is usually loaded from __doc__ so needs to be copied manually
        self.description = plugin.description

        self.data = data  # store the data produced by executor
        self.exception = exception  # store the exception produced by executor
        self.template = template  # store the plugin template

        if exception is None:
            if template is None:
                self.exception = PluginProcessingError("No plugin template was found")
            if data is None:
                self.exception = PluginProcessingError("Plugin returned no data to render")

    def render(self) -> str:
        """
        Function is used to produce the HTML output of the result for display
        :return: HTML String
        """
        return Template(self.template).render(self.data)  # render plugin template with data produced


class Report:
    """
        Object used to store the result of a scan when initiated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...

        essentially a model probably convert this to just a dict at some point when its completely figured out
    """

    def __init__(self, name: str):
        self.date = str(datetime.now().date()).replace(":", "-")  # get current time
        self.name = name  # user set name of the report
        self.system_name = platform.node()  # the name of the system
        self.system_platform = SystemPlatform.detect()  # the os the report was performed on
        self.software_version = application_version  # application version

        self.results = []  # used to store PluginResult instances
        self.path = None  # path variable to where the report is saved to, which is updated at program startup and save

    def __repr__(self):
        return f"Report(name='{self.name}', system_name='{self.system_name}', system_platform='{self.system_platform}', date='{self.date}')"

    def add_result(self, plugin: AbstractPlugin, data: {}, template: str):
        """
        Function is used to add successful results to the Report
        :param plugin: Plugin which produced the result
        :param data:  data produced by the plugin executor
        :param template:  template html required to render the data
        """
        self.results.append(PluginResult(plugin, data=data, template=template))

    def add_exception(self, plugin: AbstractPlugin, exception: Exception):
        """
        Function is used to add failed results to the Report i.e the plugin raised an exception during execution
        :param plugin: Plugin which produced the result
        :param exception: Exception raised by Plugin Executor
        """
        self.results.append(PluginResult(plugin, exception=exception))


def load_reports() -> bool:
    for root, dirs, files in os.walk(reports_directory):
        for file in files:
            if file.endswith(report_extension):
                import_report(os.path.join(reports_directory, file))

    return len(reports) > 0


def import_report(report_path: str) -> bool:
    try:
        report_pickle = pickle.load(open(report_path, "rb"))
        if isinstance(report_pickle, Report):
            report_pickle.path = report_path
            reports.append(report_pickle)
            logger.debug(f'Successfully imported {report_pickle}')

            return True
    except AttributeError:
        logger.error(f'Failed to import {report_path} due to missing dependency, skipping.')
        return False
    except Exception as e:
        logger.error(f'Failed to import {report_path} due to an exception, skipping.')
        logger.debug(e)


def store_report(report: Report) -> int:
    export_path = export_report(report)  # export report to file and get path
    reports.append(report)  # add report to list
    report.path = export_path  # update path

    return len(reports) - 1  # return index of report in list


def generate_report_filename(report: Report, append_extension: str = report_extension):
    # get user set config filename template and replace needed variables
    report_filename = Template(report_filename_template).render({
        "name": report.name,
        "system_name": report.system_name,
        "platform": report.system_platform,
        "date": str(report.date)
    })

    if append_extension:
        report_filename = '.'.join((report_filename, append_extension))

    return report_filename


def export_report(report: Report):
    report_filename = generate_report_filename(report)
    if not os.path.exists(reports_directory):
        os.mkdir(reports_directory)

    # combine filename with path and extension
    report_path = os.path.abspath(os.path.join(reports_directory, report_filename))

    # save it
    print(report_path)
    with open(report_path, "wb") as fw:
        data = pickle.dumps(report)
        fw.write(data)  # dump to pickle then write the bytes

    return report_path  # return the final saved abs path


def export_report_as_html(report: Report, path: str):
    export_template = render_template("layouts/export.html", report=report)

    # TODO add exception handling for permission errors, file exists, e.t.c...
    with open(path, "w") as f:
        f.write(export_template)


def start_report(report_name: str, plugins: [AbstractPlugin]) -> int:
    if threading_enabled:
        logger.debug("Starting threaded report processor")
        processor = ThreadedReportProcessor(report_name, plugins)
        processor.daemon = True
    else:
        logger.debug("Starting non-threaded report processor")
        processor = ReportProcessor(report_name, plugins)

    processor.start()

    thread_id = randint(0, 10000)
    processing_reports[thread_id] = processor

    return thread_id


def start_quick_report():
    return start_report("Quick Report", usable_plugins())


class ReportProcessor:

    def __init__(self, report_name, plugins):
        self.report = Report(report_name)
        self.plugins = {plugin: False for plugin in plugins}  # create dict with all plugins as key and value as false

        self.report_id = None

    def start(self):
        for plugin, complete in self.plugins.items():
            try:
                template = plugin.template()
                data = plugin.process()

                self.plugins[plugin] = True

                self.report.add_result(plugin, data, template)
            except Exception as ppe:
                self.report.add_exception(plugin, ppe)

    @property
    def progress(self):
        return len([status for status in self.plugins.values() if status]) * (100 / len(self.plugins))


class ThreadedReportProcessor(Thread, ReportProcessor):

    def __init__(self, report_name, plugins):
        Thread.__init__(self)
        ReportProcessor.__init__(self, report_name, plugins)

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
                    template = plugin.template
                    data = future.result()
                    self.report.add_result(plugin, data, template)
                except Exception as executor_exception:
                    self.report.add_exception(plugin, executor_exception)

        self.report_id = store_report(self.report)
