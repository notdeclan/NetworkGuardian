from asyncio import sleep
from http.client import HTTPConnection

from networkguardian import logger
from networkguardian.registry import registered_plugins, load_plugins
from networkguardian.server import start_server


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
        conn.request('GET', path)
        r = conn.getresponse()
        return r.status == 200
    except ConnectionRefusedError:  # TODO: figure out actual exception raise here and add to catch
        return False


if __name__ == '__main__':
    logger.debug('Starting Flask Server')
    host, port = "127.0.0.1", 24982

    start_server(host, port)

    logger.debug('Loading Plugins')
    load_plugins()
    logger.debug(f'Loaded {len(registered_plugins)} plugins')

    logger.debug('Waiting for Server Availability')
    while not is_alive(host, port):  # wait until web server is running and application  is responding
        sleep(1)

    logger.debug('Creating Webview Window')
    # TODO: find cross platform way of calculating screen resolution so window can start in maximised mode=======

    while True:
        pass

    # window = webview.create_window(application_name, f'http://{host}:{port}', width=1500)
    # webview.start(debug=True)