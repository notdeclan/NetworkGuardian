from asyncio import sleep
from http.client import HTTPConnection

import webview

from networkguardian import log, application_name, flask_configuration
from networkguardian.server import start_server


def is_alive(host, port):
    try:
        conn = HTTPConnection(host, port)
        conn.request('HEAD', '/')
        r = conn.getresponse()
        return r.status == 200
    except:  # TODO: figure out actual exception raise here and add to catch
        log.exception('Server not started')
        return False


if __name__ == '__main__':
    host, port = flask_configuration
    url = f'http://{host}:{port}'

    log.debug('Starting Flask Server')
    start_server()

    log.debug('Waiting for Server Availability')
    while not is_alive(host, port):  # wait until web server is running and application  is responding
        sleep(1)

    log.debug('Creating Webview Window')

    # TODO: find cross platform way of calculating screen resolution so window can start in maximised mode
    window = webview.create_window(application_name, url, width=1500)
    webview.start(debug=True)
