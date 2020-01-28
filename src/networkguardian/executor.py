import multiprocessing
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

from networkguardian.exceptions import PluginProcessingError
from networkguardian.plugin import BasePlugin
from networkguardian.report import Result, Report
from networkguardian.standard_plugins import TestPlugin


class PluginExecutor:

    def __init__(self):
        self.plugins = []
        self.max_threads = None

    def add_plugin(self, plugin: BasePlugin):
        self.plugins.append(plugin)

    def process(self, selected_plugins: []) -> Report:
        thread_count = self.get_thread_count(max_required=len(selected_plugins))
        report_v = Report("SYSTEM NAME", "CURRENT TIME/DATE", "VERSION")  # TODO: get actual values

        with ThreadPoolExecutor(max_workers=thread_count) as tpe:
            # loop through all plugins, submit future for each one
            future_to_plugin = {
                tpe.submit(p.execute): p for p in selected_plugins
            }

            # for f in future_to_plugin:
            #    f.add_done_callback(done_callback)

            for future in futures.as_completed(future_to_plugin):
                plugin = future_to_plugin[future]
                try:
                    result = future.result()
                    template = plugin.template
                    report_v.add_result(Result(plugin, result, template))
                except PluginProcessingError as ppe:
                    # TODO : add handling for this, whether its adding exception to "Result" object or displaying on
                    #  UI etc
                    pass

        return report_v

    def get_thread_count(self, max_required: int = None):
        """
        Function is used to calculate the amount of threads that should be used based on three different factors, the
        function can be used in multiple use cases

        The idea around the function is that it will return by default the max allowed threads if set, if not it will
        either return the maxmium amount of threads possible in the system unless the job count (ie how many threads are
        even needed) is lower, in that case it will use that

        :param max_required: Maximum amount of workers the thread pool needs to process
        :return: Thread Count to use
        """

        # by default use the amount of CPU cores installed in the system
        thread_count = multiprocessing.cpu_count()

        # if there's a max required specified, IE there's only like 2 plugins loaded so why bother creating a larger
        # pool

        if isinstance(max_required, int):
            if max_required < thread_count:  # if the required is smaller than thread count
                thread_count = max_required  # just set it the required amount

        if self.max_threads is not None:
            if thread_count > self.max_threads:  # if the thread count is higher than the max allowed threads set by
                # the user
                thread_count = self.max_threads  # set the thread count

        return thread_count


if __name__ == '__main__':
    e = PluginExecutor()
    e.max_threads = 3
    report = e.process([TestPlugin(4), TestPlugin(2), TestPlugin(3), TestPlugin(1)])

    print(report.render())
