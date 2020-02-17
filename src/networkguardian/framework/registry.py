import multiprocessing
import sys
from glob import glob
from os.path import join, basename

from networkguardian import logger
from networkguardian.framework.plugin import PluginCategory, SystemPlatform

registered_plugins = {}


def usable_plugins() -> []:
    return [plugin for plugin in registered_plugins.values() if plugin.loaded and plugin.supported]


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
        registered_plugins[name] = instance  # add to list

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
    for plugin in registered_plugins.values():
        try:
            plugin.load(running_platform)  # attempt to load
            logger.debug(f'Successfully loaded {plugin}')
        except Exception as loading_exception:  # if exception add to the plugin so it can be displayed later in GUI
            logger.error(f'Failed to load {plugin} due to {loading_exception}, disabling.')
            plugin.loading_exception = loading_exception


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

    return thread_count
