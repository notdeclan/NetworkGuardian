import os
import sys
from asyncio import sleep
from pathlib import Path

import psutil

from networkguardian import logger, is_frozen
from networkguardian.framework.registry import registered_plugins, load_plugins, import_external_plugins
from networkguardian.gui.server import start, is_alive


def create_directories():
    home = str(Path.home())
    ng_directory = os.path.join(home, "Network Guardian")
    sub_folders = ['plugins', 'reports']
    if not os.path.exists(ng_directory):
        os.makedirs(ng_directory)
        for sub_folder_name in sub_folders:
            os.makedirs(os.path.join(ng_directory, sub_folder_name))


def detect_siblings():
    """
        Function detects if another Network Guardian instance is running and then exits
    """
    pid = os.getpid()  # get the current PID
    process_name = psutil.Process(pid).name()  # convert the PID to name

    # if there's multiple processes with same name
    if len([p for p in psutil.process_iter() if process_name in p.name()]) > 2:
        logger.critical("Another process running, exiting ... ")  # exit
        sys.exit(1)


def run():
    """
    """
    """
        STARTUP CONFIGURATIONS:
            - run () - Starts everything
            - quick_scan(config) - Just launches scan
            
        psuedo code for startup
        if find config
            if reports and plugins dir exists
                load plugins
                # get disabled plugins from config
                for plugin in plugins:
                    if plugin.name in config[disabled_plugins]:
                        plugin.disabled = True
                        
                load reports
            else
                create them
        else if cli saying just scan(report_dir=, external_plugin_dir=, config)
            launch scan
        else
            launch setup
    """
    """
        USB Scan Config:
            report_dir
                            
    """
    if is_frozen:
        detect_siblings()

    logger.debug('Starting Network Guardian')

    logger.debug('Importing Standard Plugins')

    # noinspection PyUnresolvedReferences
    import networkguardian.standard_plugins

    logger.debug('Importing External Plugins')
    import_external_plugins("../plugins")  # TODO: figure out what the actual path will be when freezing  i.e config

    logger.debug("Loading Plugins")
    load_plugins()
    logger.debug(f'Loaded {len([p for p in registered_plugins if p.loaded])} plugins')

    logger.debug('Importing Reports')

    logger.debug('Starting Flask Server')
    host, port = "127.0.0.1", 24982
    start(host, port)

    logger.debug('Waiting for Server Availability')
    while not is_alive(host, port):  # wait until web server is running and application  is responding
        sleep(1)

    logger.debug('Creating Webview Window')

    # PYWEBVIEW WINDOW CODE
    # window = webview.create_window(application_name, f'http://{host}:{port}', width=1500)
    # webview.start(debug=True)

    # TEST REPORT AND PROCESS PLUGIN
    # results = process_plugins([p for p in registered_plugins if p.loaded])
    # report = Report("test_report")
    # report.add_results(results)
    # report.store('test.report')

    # TODO: add keyboard interrupt / other interrupt catch case for safely shutting down e.t.c...
    while True:
        pass
