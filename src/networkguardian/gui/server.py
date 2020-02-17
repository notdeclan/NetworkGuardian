import logging
import sys
from http.client import HTTPConnection
from threading import Thread

from flask import Flask

from networkguardian import application_frozen
from networkguardian.gui.blueprints import api, panel

if application_frozen:
    # DISABLE FLASK MESSAGE
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    # LOWER FLASK LOGGING LEVEL
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

# FLASK CONFIGURATION
app = Flask(__name__, static_folder=None)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
app.register_blueprint(panel.mod)
app.register_blueprint(api.mod)
app.secret_key = 'super secret key'  # TODO: something secret loL
app.config['SESSION_TYPE'] = 'filesystem'


@app.after_request
def add_header(response):
    """
    Event listener function is required to prevent browsers from caching page content stopping them from being able to
    update automatically.
    """
    response.headers['Cache-Control'] = 'no-store'  # disable caching
    return response


def start(host, port):
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


def is_alive(remote_url: str, remote_port: int, path: str = '/'):
    """
    Function is used to test whether a web server is responding by sending a HTTP HEAD request

    :param remote_url: Web Server domain or IP
    :param remote_port: Web Server port
    :param path: Page to request
    :return: True if the web server responds, False if not
    """
    try:
        conn = HTTPConnection(remote_url, remote_port)
        conn.request('HEAD', path)
        r = conn.getresponse()
        return r.status == 200
    except ConnectionRefusedError:  # TODO: figure out actual exception raise here and add to catch
        return False
