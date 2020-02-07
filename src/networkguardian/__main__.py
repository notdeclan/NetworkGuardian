from asyncio import sleep

from networkguardian import logger
from networkguardian.framework.registry import registered_plugins, load_plugins, import_plugins, process_plugins
from networkguardian.framework.report import Report
from networkguardian.gui.server import start_server, is_alive

if __name__ == '__main__':
    logger.debug('Starting Network Guardian')

    logger.debug('Importing Standard Plugins')
    # noinspection PyUnresolvedReferences
    import networkguardian.standard_plugins

    logger.debug('Importing External Plugins')
    import_plugins("../plugins")  # TODO: figure out what the actual path will be when freezing

    logger.debug("Loading Plugins")
    load_plugins()
    logger.debug(f'Loaded {len([p for p in registered_plugins if p.loaded])} plugins')

    logger.debug('Importing Reports')

    logger.debug('Starting Flask Server')
    host, port = "127.0.0.1", 24982
    start_server(host, port)

    logger.debug('Waiting for Server Availability')
    while not is_alive(host, port):  # wait until web server is running and application  is responding
        sleep(1)

    logger.debug('Creating Webview Window')
    # window = webview.create_window(application_name, f'http://{host}:{port}', width=1500)
    # webview.start(debug=True)

    results = process_plugins([p for p in registered_plugins if p.loaded])

    report = Report("test_report")
    report.add_results(results)
    report.store('test.report')

    #
    # for p in registered_plugins:
    #     if p.loaded:
    #         print("Processing", p.name)
    #         data, template = p.process()
    #         print(template.render(data))

    print("finished")
    while True:
        pass
