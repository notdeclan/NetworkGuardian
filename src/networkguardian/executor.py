import multiprocessing
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

from networkguardian.exceptions import PluginProcessingError
from networkguardian.plugin import BasePlugin


class PluginResult:
    """
    Potentially temporary way of storing a plugin result
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


class PluginExecutor:

    def __init__(self):
        self.plugins = []
        self.max_threads = None

    def add_plugin(self, plugin: BasePlugin):
        self.plugins.append(plugin)

    def process(self, selected_plugins: []) -> []:
        """
        Function will process all plugins that are passed asynchronously using a ThreadPool and return a list
        of Result objects

        :param selected_plugins: plugins to execute
        :return: List of Result objects
        """
        thread_count = self.get_thread_count(max_required=len(selected_plugins))
        results = []

        with ThreadPoolExecutor(max_workers=thread_count) as tpe:
            # loop through all plugins, submit future for each one
            future_to_plugin = {
                tpe.submit(p.execute): p for p in selected_plugins
            }

            for future in futures.as_completed(future_to_plugin):
                plugin = future_to_plugin[future]
                result = PluginResult(plugin)
                try:
                    result.add_data(future.result())
                except PluginProcessingError as ppe:
                    # TODO : add handling for this, whether its adding exception to "Result" object or displaying on
                    #  UI etc
                    result.add_exception(ppe)

                results.append(result)

        return results

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
