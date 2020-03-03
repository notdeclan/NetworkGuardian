# noinspection PyUnresolvedReferences
import encodings.idna  # needed to fix random LookupError when starting when frozen
import logging
import os
import socket
import sys
from contextlib import closing

import webview

application_name = "Network Guardian"
application_version = 1.0
application_config_file = "config.ini"

application_frozen = getattr(sys, 'frozen', False)
threading_enabled = True

logging_mode = logging.INFO

if application_frozen:
    application_path = os.path.dirname(sys.executable)  # executable entry point i.e Network Guardian.exe
else:  # if not frozen
    application_path = os.path.dirname(sys.argv[0])  # entry point path

application_directory = os.path.join(application_path, application_name)
config_path = os.path.join(application_directory, application_config_file)
plugins_directory = os.path.join(application_directory, "plugins")
reports_directory = os.path.join(application_directory, "reports")

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


def get_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


host, port = "127.0.0.1", get_free_port()
window = webview.create_window(application_name, f'http://{host}:{port}', width=1000, confirm_close=True)
