from threading import Thread

from flask import Flask

from networkguardian.blueprints.api import mod as api
from networkguardian.blueprints.panel import mod as panel

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