import multiprocessing
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor

from networkguardian import logger
from networkguardian.exceptions import PluginProcessingError
from networkguardian.framework.plugin import PluginResult, Category, Platform

registered_plugins = []

max_threads = None


def register_plugin(name: str, category: Category, author: str, version: float):
    """
    Function annotation used to dynamically load/register plugins into the module

    :param name: Name of plugin
    :param category: Category of the plugin
    :param author: Author/Developer of the plugin
    :param version:
    :return:
    """

    def __init__(cls):
        instance = cls(name, category, author, version)  # create an instance
        registered_plugins.append(instance)  # add to list

    return __init__


def test_plugin(cls):
    """
    Temporary way of testing whether a plugin works as expected ...

    to use comment out the @register annotation above an AbstractPlugin abstraction, and place above...
    """
    print("Testing: ", cls)
    instance = cls("Test", Category.INFO, "Author", 1)
    instance.load(Platform.detect())
    data, template = instance.process()
    print("\tSupports:", instance.supported_platforms)
    print("\tData:", data)
    print("\tRender:", template.render(data))
    return instance


def load_plugins():
    running_platform = Platform.detect()
    for p in registered_plugins:
        try:
            p.load(running_platform)
            logger.debug(f'Loaded {p}')
        except Exception as loading_exception:
            logger.error(f'Failed to load {p} due to {loading_exception}, disabling.')
            p.loading_exception = loading_exception


def process_plugins(selected_plugins: []) -> []:
    """
    Function will process all plugins that are passed asynchronously using a ThreadPool and return a list
    of Result objects

    :param selected_plugins: plugins to execute
    :return: List of Result objects
    """
    thread_count = get_thread_count(max_required=len(selected_plugins))
    results = []

    with ThreadPoolExecutor(max_workers=thread_count) as tpe:
        # loop through all plugins, submit future for each one
        future_to_plugin = {
            tpe.submit(p.process): p for p in selected_plugins
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


def get_thread_count(max_required: int = None):
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

    if max_threads is not None:  # ie if it has been set by the user TODO: add this into config when done
        if thread_count > max_threads:  # if the thread count is higher than the max allowed threads set by
            # the user
            thread_count = max_threads  # set the thread count

    return thread_count
