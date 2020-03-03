import logging
import sys
from http.client import HTTPConnection
from threading import Thread

from flask import Flask, render_template, flash

from networkguardian import application_frozen, application_name, application_version, logger
from networkguardian.gui.blueprints import api, panel

# FLASK CONFIGURATION
app = Flask(__name__, static_folder=None)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
app.register_blueprint(panel.mod)
app.register_blueprint(api.mod)
app.secret_key = 'super secret key'  # TODO: something secret loL
app.config['SESSION_TYPE'] = 'filesystem'

if not application_frozen:  # cache when in production to improve loading speed otherwise don't
    # TODO: check if this is actually needed

    @app.after_request
    def add_header(response):
        """
        Event listener function is required to prevent browsers from caching page content stopping them from being able to
        update automatically.
        """
        response.headers['Cache-Control'] = 'no-store'  # disable caching
        return response


@app.errorhandler(404)
def page_not_found():
    return render_template('pages/404.html'), 404


@app.errorhandler(500)
def internal_server_error():
    flash("An unexpected error occurred, see the Log for more information.")
    return render_template('pages/dashboard.html'), 500


@app.context_processor
def template_injector():
    return {
        "application_name": application_name,
        "application_version": application_version
    }


def disable_flask_logging():
    # DISABLE FLASK MESSAGE
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    # LOWER FLASK LOGGING LEVEL
    logging.getLogger('werkzeug').setLevel(logging.ERROR)


def start(host, port):
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
