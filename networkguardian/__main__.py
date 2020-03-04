import logging
import os
import sys
from asyncio import sleep

import click
import psutil

from networkguardian import logger, application_frozen, application_directory, plugins_directory, reports_directory
from networkguardian.framework.registry import registered_plugins, load_plugins, import_external_plugins
from networkguardian.framework.report import load_reports, processing_reports, start_quick_report
from networkguardian.gui.server import start_server, is_alive
from networkguardian.gui.webview import open_window


@click.group(invoke_without_command=True)
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    enable_debugging(debug)

    logger.debug('Starting Network Guardian')

    create_directories()

    # Die if other instances running
    if application_frozen:
        detect_siblings()

    # Import Plugins from directory
    logger.debug('Importing External Plugins')
    import_external_plugins(plugins_directory)

    # Load Plugins
    logger.debug("Loading Plugins")
    load_plugins()

    total_plugins = len(registered_plugins)
    total_loaded = len([p for p in registered_plugins.values() if p.loaded])
    total_failed = total_plugins - total_loaded

    logger.debug(f'Loaded {total_plugins} plugins ({total_loaded} successfully, {total_failed} failed)')

    # Start GUI if no command specified
    if ctx.invoked_subcommand is None:
        gui()


@cli.command()
def quick_report():
    print("Starting Report")
    thread_id = start_quick_report()
    thread = processing_reports[thread_id]

    progress = 0
    with click.progressbar(length=100, label='Creating report', show_eta=False) as bar:
        while thread.progress < 100:
            if thread.progress > progress:
                bar.update(thread.progress - progress)
                progress = thread.progress

    print("Finished Report")


@cli.command()
@click.option('--debug/--no-debug', default=False)
def gui(debug):
    enable_debugging(debug)

    logger.debug('Importing Reports')
    load_reports()

    logger.debug('Starting Flask Server')
    start_server()

    logger.debug('Waiting for Server Availability')
    while not is_alive():  # wait until web server is running and application  is responding
        sleep(1)

    logger.debug('Creating Webview Window')

    open_window()


@cli.command()
@click.option('--debug/--no-debug', default=False)
@click.argument('host')
@click.argument('port')
def server(debug, host, port):
    enable_debugging(debug)

    logger.debug('Importing Reports')
    load_reports()

    logger.debug('Starting Flask Server')
    start_server(host, port)

    logger.debug('Waiting for Server Availability')
    while not is_alive():  # wait until web server is running and application  is responding
        sleep(1)

    logger.info(f'Server running at {host}:{port}')
    while True:
        pass


def create_directories():
    if not os.path.exists(application_directory):
        logger.debug("Working folder not found, creating directories.")
        os.mkdir(application_directory)
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


def enable_debugging(debug):
    if debug:
        logger.setLevel(logging.DEBUG)
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG)
