import os
import webbrowser

import webview
from flask import Blueprint, request, redirect, flash

from framework.registry import import_external_plugins, load_plugins
from networkguardian import plugins_directory

"""
    Flask Blueprint class used for handling all API requests
"""

mod = Blueprint('api', __name__)

"""
    Plugins Page
"""


@mod.route("/api/plugins/refresh")
def refresh_plugins():
    import_external_plugins(plugins_directory)
    load_plugins()
    print(dir(webview.windows[0]))
    flash("Refreshed Plugins")
    flash("Twice as much fun as u need this good year sir")
    return redirect(request.headers.get("Referer"))


@mod.route("/api/plugins/directory")
def plugin_directory():
    webbrowser.open(os.path.abspath(plugins_directory))
    return redirect(request.headers.get("Referer"))
