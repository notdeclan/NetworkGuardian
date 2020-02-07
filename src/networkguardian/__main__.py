import sys
from asyncio import sleep
from glob import glob
from http.client import HTTPConnection
from os.path import basename, join

from networkguardian import logger
from networkguardian.framework.registry import registered_plugins, load_plugins
from networkguardian.gui.server import start_server


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


def import_plugins(directory: str):
    # Import all classes in this directory so that classes with @register_plugin are registered.
    sys.path.append(directory)
    for x in glob(join(directory, '*.py')):  # for each file in working directory that have file
        if not x.startswith('__'):  # if not private
            __import__(basename(x)[:-3], globals(), locals())


if __name__ == '__main__':
    logger.debug('Starting Network Guardian')
    logger.debug('Importing Standard Plugins')
    # noinspection PyUnresolvedReferences
    import networkguardian.standard_plugins

    logger.debug('Importing External Plugins')
    import_plugins("../plugins")  # TODO: figure out what the actual path will be when freezing

    logger.debug("Loading Plugins")
    load_plugins()

    logger.debug(f'Loaded {len([p for p in registered_plugins if p.loading_exception is None])} plugins')

    logger.debug('Starting Flask Server')
    host, port = "127.0.0.1", 24982
    start_server(host, port)

    logger.debug('Waiting for Server Availability')
    while not is_alive(host, port):  # wait until web server is running and application  is responding
        sleep(1)

    logger.debug('Creating Webview Window')
    # window = webview.create_window(application_name, f'http://{host}:{port}', width=1500)
    # webview.start(debug=True)

    while True:
        pass
