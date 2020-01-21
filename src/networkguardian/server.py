from threading import Thread

from flask import Flask

from networkguardian import flask_configuration
from networkguardian.blueprints.api import mod as api
from networkguardian.blueprints.panel import mod as panel

server = Flask(__name__)
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
server.register_blueprint(panel)
server.register_blueprint(api)


@server.after_request
def add_header(response):
    """
    Event listener function is required to prevent browsers from caching page content stopping them from being able to
    update automatically.
    """
    response.headers['Cache-Control'] = 'no-store'  # disable caching
    return response


def _run_flask():
    host, port = flask_configuration
    server.run(host=host, port=port, threaded=True)


def start_server():
    t = Thread(target=_run_flask)  # create new thread and run flask inside of it
    t.daemon = True # make thread non blocking
    t.start()
