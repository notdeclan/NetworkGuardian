# noinspection PyUnresolvedReferences
import encodings.idna  # needed to fix random LookupError when starting when frozen
import logging
import os
import sys

application_name = "Network Guardian"
application_version = 1.0
application_config_file = "config.ini"

application_frozen = getattr(sys, 'frozen', False)
threading_enabled = True

logging_mode = logging.INFO

if application_frozen:
    application_path = os.path.dirname(sys.executable)  # executable entry point i.e Network Guardian.exe
else:  # if not frozen
    application_path = os.path.abspath(os.path.dirname(sys.argv[0]))  # entry point path

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


def find_resource(file_path: str):
    if application_frozen:
        resource_path = sys._MEIPASS
    else:
        resource_path = os.path.dirname(__file__)

    return os.path.join(resource_path, file_path)


def find_user_resource(file_path: str = ''):
    if application_frozen:
        user_resource_path = os.path.dirname(sys.executable)  # executable entry point i.e Network Guardian.exe
    else:  # if not frozen
        user_resource_path = os.path.abspath(os.path.dirname(sys.argv[0]))  # entry point path

    return os.path.join(user_resource_path, application_name, file_path)


application_directory = find_user_resource()
config_path = find_user_resource(application_config_file)
plugins_directory = find_user_resource('plugins')
reports_directory = find_user_resource('reports')
