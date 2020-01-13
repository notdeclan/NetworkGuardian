import logging

application_version = 0.1
logging_mode = logging.DEBUG


def initialize_logger():
    logger = logging.getLogger('Network Guardian')
    logger.setLevel(logging_mode)

    # create console handler with a higher log level (ie only print important shite to console etc)
    ch = logging.StreamHandler()
    ch.setLevel(logging_mode)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add the handler to the logger
    logger.addHandler(ch)

    return logger

log = initialize_logger()