import os
import sys
from asyncio import sleep

import psutil
import webview

from networkguardian import logger, application_frozen, application_directory, plugins_directory, reports_directory, \
    config_path, config, host, port, window
from networkguardian.framework.registry import registered_plugins, load_plugins, import_external_plugins
from networkguardian.framework.report import reports, store_report, load_reports
from networkguardian.gui.server import start, is_alive


def save_config():
    with open(config_path, 'w') as config_file:
        config.write(config_file)


def initialize_config():
    save_config()


def load_config():
    config.read(config_path)


def config_exists():
    return os.path.isfile(config_path)


def create_directories():
    if not os.path.exists(application_directory):
        logger.debug("Working folder not found, creating directories.")
        os.mkdir(application_directory)  #
        os.mkdir(plugins_directory)
        os.mkdir(reports_directory)


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


def on_closing():
    """
    Function is triggered when web view window close is initiated
    """
    # TODO: save config and do closing down procedures here...
    logger.debug('Close initiated by user')
    logger.debug('Saving Config')
    save_config()
    for report in reports.values():
        store_report(reports_directory, report)


def run():
    """
    """
    """
        STARTUP CONFIGURATIONS:
            - run () - Starts everything
            - quick_scan(config) - Just launches scan
            - browser mode
                 
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

    # if not config_exists():  # if config doesnt exist
    #     initialize_config()
    # else:
    #     load_config()

    create_directories()

    if application_frozen:
        detect_siblings()

    logger.debug('Starting Network Guardian')

    logger.debug('Importing Standard Plugins')
    #
    # # noinspection PyUnresolvedReferences
    # import networkguardian.standard_plugins

    logger.debug('Importing External Plugins')
    import_external_plugins(plugins_directory)

    logger.debug("Loading Plugins")
    load_plugins()

    total = len(registered_plugins)
    loaded = len([p for p in registered_plugins.values() if p.loaded])
    failed = total - loaded
    logger.debug(f'Loaded {total} plugins ({loaded} successfully, {failed} failed)')

    logger.debug('Importing Reports')
    load_reports()

    logger.debug('Starting Flask Server')
    start(host, port)

    logger.debug('Waiting for Server Availability')
    while not is_alive(host, port):  # wait until web server is running and application  is responding
        sleep(1)

    logger.debug('Creating Webview Window')

    # PYWEBVIEW WINDOW COD
    window.closing += on_closing
    webview.start(debug=False, gui='qt')

    # TEST REPORT AND PROCESS PLUGIN
    # results = process_plugins([p for p in registered_plugins if p.loaded])
    # report = Report("test_report")
    # report.add_results(results)
    # report.store('test.report')
