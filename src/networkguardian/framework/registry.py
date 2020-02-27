import glob
import importlib.util
import multiprocessing
import os
import sys
from os.path import basename

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


def import_external_plugins(directory: str):
    """
    Import's python modules from directory paths

    :param directory: directory to look for modules
    """
    for file_path in glob.iglob(os.path.join(directory, '**/*.py'), recursive=True):
        if os.path.isfile(file_path):  # filter dirs
            module_name = basename(file_path)[:-3]
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
            except Exception as e:
                """
                Using a broader expression is difficult here because there are so many which the user plugin may raise.
                Therefore it is easier, and safer for program execution, to just ignore loading the plugin if any
                exception is raised.
                """
                logger.error(f'Failed to load module {module_name}', e)
                continue


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
