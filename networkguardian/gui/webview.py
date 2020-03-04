import webview

from networkguardian import logger
from networkguardian.gui import window


def on_closing():
    """
    Function is triggered when web view window close is initiated
    """
    # TODO: save config and do closing down procedures here...
    logger.debug('Close initiated by user')


def open_window():
    window.closing += on_closing
    webview.start(debug=False, gui='qt')
