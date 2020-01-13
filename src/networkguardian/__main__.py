from asyncio import sleep
from http.client import HTTPConnection
from threading import Thread

import webview

from networkguardian import log, application_name
from networkguardian.plugin import ExamplePlugin, Platform, SystemInformationPlugin
from networkguardian.server import run_server


def url_ok(url, port):
    try:
        conn = HTTPConnection(url, port)
        conn.request('HEAD', '/')
        r = conn.getresponse()
        return r.status == 200
    except:
        log.exception('Server not started')
        return False


def start_server():
    log.debug('Starting server')
    t = Thread(target=run_server)
    t.daemon = True
    t.start()


if __name__ == '__main__':
    platform = Platform.detect()

    plugins = [ExamplePlugin(), SystemInformationPlugin()]

    for p in plugins:
        p.load(platform)

    for p in plugins:
        if p.supported:
            print(f'Scanning with {p.name}')
            print(p.template.render(p.execute()))


    start_server()

    log.debug('Checking server')
    while not url_ok('127.0.0.1', 23948): # wait until web server is running and application  is responding
        sleep(1)

    log.debug('Server started')
    window = webview.create_window(application_name, 'http://127.0.0.1:23948')
    webview.start(debug=True)
