import logging
import sys
from http.client import HTTPConnection
from threading import Thread

from networkguardian import application_frozen, logger
from networkguardian.gui import app, server_host, server_port


def disable_flask_logging():
    # DISABLE FLASK MESSAGE
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    # LOWER FLASK LOGGING LEVEL
    logging.getLogger('werkzeug').setLevel(logging.ERROR)


def start_server(host: str = server_host, port: int = server_port):
    if application_frozen or logger.level is logging.INFO:
        disable_flask_logging()

    """
    Start's the flask web server in its own thread
    """
    flask_arguments = {
        'host': host,
        'port': port,
        'threaded': True
    }

    t = Thread(target=app.run, kwargs=flask_arguments)  # create new thread and run flask inside of it
    t.daemon = True  # make thread non blocking
    t.start()


def is_alive():
    """
    Function is used to test whether a web server is responding by sending a HTTP HEAD request
    :return: True if the web server responds, False if not
    """

    try:
        conn = HTTPConnection(server_host, server_port)
        conn.request('HEAD', '/')
        r = conn.getresponse()
        return r.status == 200

    except ConnectionRefusedError:
        return False
