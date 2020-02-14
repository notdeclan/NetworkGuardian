import os
import webbrowser

from flask import Blueprint, request, redirect

from framework.registry import import_external_plugins, load_plugins
from networkguardian import plugins_directory

"""
    Flask Blueprint class used for handling all API requests
"""

mod = Blueprint('api', __name__)

"""
    Plugins
"""


@mod.route("/api/plugins/refresh")
def refresh_plugins():
    import_external_plugins(plugins_directory)
    load_plugins()
    return redirect(request.headers.get("Referer"))


@mod.route("/api/plugins/directory")
def plugin_directory():
    webbrowser.open(os.path.abspath(plugins_directory))
    return redirect(request.headers.get("Referer"))
