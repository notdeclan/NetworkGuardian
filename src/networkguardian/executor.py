import multiprocessing
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

from networkguardian.exceptions import PluginProcessingError
from networkguardian.plugin import BasePlugin


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


class PluginExecutor:

    def __init__(self):
        self.plugins = []
        self.max_threads = None

    def add_plugin(self, plugin: BasePlugin):
        self.plugins.append(plugin)

    def generate_report(self, selected_plugins: []) -> []:
        thread_count = self.get_thread_count(max_required=len(selected_plugins))
        results = []

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
                    results.append(Result(plugin, result, template))
                except PluginProcessingError as ppe:
                    # TODO : add handling for this, whether its adding exception to "Result" object or displaying on UI etc
                    pass

        return results

    def display_report(self, results):
        pass


    def get_thread_count(self, max_required: int = None):
        """
        Function is used to calculate the amount of threads that should be used based on three different factors, the function
        can be used in multiple use cases

        The idea around the function is that it will return by default the max allowed threads if set, if not it will
        either return the maxmium amount of threads possible in the system unless the job count (ie how many threads are
        even needed) is lower, in that case it will use that

        :param max_required:
        :return:
        """

        # by default use the amount of CPU cores installed in the system
        thread_count = multiprocessing.cpu_count()

        # if there's a max required specified, IE theres only like 2 plugins loaded so why bother creating a larger pool
        if isinstance(max_required, int):
            if max_required < thread_count:  # if the required is smaller than thread count
                thread_count = max_required  # just set it the required amount

        if self.max_threads is not None:
            if thread_count > self.max_threads:  # if the thread count is higher than the max allowed threads set by the user
                thread_count = self.max_threads  # set the thread count

        return thread_count
