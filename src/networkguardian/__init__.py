import logging
from glob import glob
from os.path import basename, dirname, join

application_name = "Network Guardian"
application_version = 0.1

logging_mode = logging.DEBUG
logger = None


def initialize_logger():
    """
    Function is used to
    :return:
    """
    global logger
    logger = logging.getLogger('Network Guardian')
    logger.setLevel(logging_mode)

    # create console handler with a higher log level (ie only print important shite to console etc)
    ch = logging.StreamHandler()
    ch.setLevel(logging_mode)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add the handler to the logger
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.addHandler(ch)

    return logger


def initialize_plugins():
    # Import all classes in this directory so that classes with @register_plugin are registered.
    # TODO: when freezing and building work out how to specify a user directory to load plugins from etc...
    pwd = dirname(__file__)

    for x in glob(join(pwd, '*.py')):  # for each file in working directory that have file
        if not x.startswith('__'):  # if not private
            __import__(basename(x)[:-3], globals(), locals())  # import it


initialize_logger()
initialize_plugins()
