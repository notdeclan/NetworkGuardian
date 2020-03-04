import socket
from contextlib import closing

import webview
from flask import Flask

from networkguardian import application_name, find_resource


def get_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


server_host, server_port = "127.0.0.1", get_free_port()

app = Flask(__name__, static_folder=find_resource('gui/static'), template_folder=find_resource('gui/templates'))
window = webview.create_window(application_name, f"http://{server_host}:{server_port}", width=1000, confirm_close=True)

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = b'\xad\xd5M]\x14\xf9@\xad\xb6\x1cL)Pu\xaf\xc9\xe3\xf4\xfbeN\xae\x83\xcc'

# Circular Imports are bad, but blueprint's add other complications
from networkguardian.gui import routes
