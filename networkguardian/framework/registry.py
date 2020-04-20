import ctypes
import glob
import importlib.util
import multiprocessing
import os
import sys
from os.path import basename

from networkguardian import logger
from networkguardian.framework.plugin import PluginCategory, SystemPlatform, AbstractPlugin

registered_plugins = {}


def usable_plugins() -> [AbstractPlugin]:
    """
    :return: Returns a list of all the plugins registered which are supported by the operating system and loaded without
    any exceptions
    """
    return [plugin for plugin in registered_plugins.values() if plugin.loaded and plugin.supported]


def register_plugin(name: str, category: PluginCategory, author: str, version: float):
    """
    Function annotation used to dynamically load/register plugins into the module

    Will fill out all of the variables required in PluginInformation.__init__
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

    # for each file in directory with .py extension
    for file_path in glob.iglob(os.path.join(directory, '**/*.py'), recursive=True):
        if os.path.isfile(file_path):  # double check its not a folder
            module_name = basename(file_path)[:-3]  # get the name of the module
            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)  # import and exec
            except Exception as e:
                """
                Using a broader expression is difficult here because there are so many which the user plugin may raise.
                Therefore it is easier, and safer for program execution, to just ignore loading the plugin if any
                exception is raised.
                """
                logger.debug(f'Failed to load module {module_name}', e)
                continue  # goto next file


def load_plugins() -> bool:
    """
    Function is used to all plugins stored in the registered_plugins list
    """
    running_platform = SystemPlatform.detect()  # store running platform as a variable for efficiency
    running_elevated = is_elevated()  # get status on whether software is running with adminstrator rights
    for plugin in registered_plugins.values():  # loop through all plugins
        try:
            plugin.load(running_platform, running_elevated)  # attempt to load
            logger.debug(f'Successfully loaded {plugin}')
        except Exception as loading_exception:  # if exception add to the plugin so it can be displayed later in GUI
            logger.debug(f'Failed to load {plugin} due to {loading_exception}, disabling.')
            plugin.loading_exception = loading_exception

    return len(usable_plugins()) > 0


def is_elevated() -> bool:
    """
    Attempts to determine whether Network Guardian is running with elevated permissions (i.e. Sudo or Administrator)
    :return: True if elevated, False otherwise
    """
    try:
        return os.getuid() == 0  # unix
    except AttributeError:  # windows
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def get_thread_count(max_required: int = None) -> int:
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
