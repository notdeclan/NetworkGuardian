import logging
import sys
from threading import Thread

from flask import Flask

from networkguardian.gui.blueprints.api import mod as api
from networkguardian.gui.blueprints.panel import mod as panel

# DISABLE FLASK MESSAGE
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# LOWER FLASK LOGGING LEVEL
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# FLASK CONFIGURATION
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
app.register_blueprint(panel)
app.register_blueprint(api)


@app.after_request
def add_header(response):
    """
    Event listener function is required to prevent browsers from caching page content stopping them from being able to
    update automatically.
    """
    response.headers['Cache-Control'] = 'no-store'  # disable caching
    return response


def start_server(host, port):
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