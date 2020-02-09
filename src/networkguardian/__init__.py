# noinspection PyUnresolvedReferences
import encodings.idna  # needed to fix random LookupError when starting when frozen
import logging

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
    logger = logging.getLogger(application_name)
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


initialize_logger()
