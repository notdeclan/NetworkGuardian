import platform
from datetime import datetime

from networkguardian import application_version
from networkguardian.executor import PluginResult
from networkguardian.plugin import Platform


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
        Object used to store the result of a scan when initiated.
        Somehow this class will be serialized into a database so it can be loaded, exported e.t.c...

        essentially a model
    """

    def __init__(self, scan_name):
        self.scan_name = scan_name
        self.system_name = report_system_name()
        self.date = report_time()
        self.software_version = application_version
        self.system_platform = None  # TODO: this

        self.results = []

    def add_result(self, result: PluginResult):
        if isinstance(result, PluginResult):
            self.results.append(result)
        else:
            raise ValueError("result should be an instance of Result")

    def add_results(self, results: [PluginResult]):
        for result in results:
            self.add_result(result)
