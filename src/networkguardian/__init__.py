import logging

application_name = "Network Guardian"
application_version = 0.1

logging_mode = logging.DEBUG

flask_configuration = '127.0.0.1', 23948  # host, port TODO: Maybe create function to generate guaranteed free port


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
