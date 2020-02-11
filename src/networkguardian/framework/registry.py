import multiprocessing
import sys
from concurrent import futures
from concurrent.futures.thread import ThreadPoolExecutor
from glob import glob
from os.path import join, basename

from networkguardian import logger
from networkguardian.exceptions import PluginProcessingError
from networkguardian.framework.plugin import PluginCategory, SystemPlatform
from networkguardian.framework.report import PluginResult

registered_plugins = []
max_threads = None  # ie if it has been set by the user TODO: add this into config when done


def register_plugin(name: str, category: PluginCategory, author: str, version: float):
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
    TODO: remove this / look for better alternative
    to use comment out the @register annotation above an AbstractPlugin abstraction, and place above...
    """
    print("Testing: ", cls)
    instance = cls("Test", PluginCategory.INFO, "Author", 1)
    instance.load(SystemPlatform.detect())
    data, template = instance.process()
    print("\tSupports:", instance.supported_platforms)
    print("\tData:", data)
    print("\tRender:", template.render(data))
    return instance


def import_external_plugins(directory: str):
    """
    Import's python modules from directory paths

    :param directory: directory to look for modules
    """
    # Import all classes in this directory so that classes with @register_plugin are registered.
    sys.path.append(directory)  # append directory to path so can be imported
    for x in glob(join(directory, '*.py')):  # for each file in working directory that have file
        if not x.startswith('__'):  # if not private
            __import__(basename(x)[:-3], globals(), locals())


def load_plugins():
    """
    Function is used to all plugins stored in the registered_plugins list
    """
    running_platform = SystemPlatform.detect()  # store running platform as a variable for efficiency
    for plugin in registered_plugins:
        try:
            plugin.load(running_platform)  # attempt to load
            logger.debug(f'Successfully loaded {plugin}')
        except Exception as loading_exception:  # if exception add to the plugin so it can be displayed later in GUI
            logger.error(f'Failed to load {plugin} due to {loading_exception}, disabling.')
            plugin.loading_exception = loading_exception


def process_plugins(selected_plugins: []) -> []:
    """
    Function will process all plugins that are passed asynchronously using a ThreadPool and return a list
    of Result objects

    :param selected_plugins: plugins to execute
    :return: List of Result objects
    """
    thread_count = get_thread_count(max_required=len(selected_plugins))
    logger.debug(f'Processing {len(selected_plugins)} Plugins with {thread_count} Threads')
    results = []

    with ThreadPoolExecutor(max_workers=thread_count) as tpe:
        # loop through all plugins, submit future for each one
        future_to_plugin = {
            tpe.submit(p.process): p for p in selected_plugins
        }

        for future in futures.as_completed(future_to_plugin):
            plugin = future_to_plugin[future]
            print(plugin.name, "has finished yeet")

            result = PluginResult(plugin)
            try:
                data, template = future.result()
                result.add_data(data, template)

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

    if max_threads is not None:
        if thread_count > max_threads:  # if the thread count is higher than the max allowed threads set by
            # the user
            thread_count = max_threads  # set the thread count

    return thread_count
