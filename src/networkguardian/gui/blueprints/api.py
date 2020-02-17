import os
import webbrowser

from flask import Blueprint, request, redirect, flash

from networkguardian import plugins_directory, reports_directory
from networkguardian.framework.plugin import SystemPlatform
from networkguardian.framework.registry import import_external_plugins, load_plugins

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

    flash("Refreshed Plugins")

    return redirect(request.headers.get("Referer"))


@mod.route("/api/plugins/directory")
def plugin_directory():
    open_directory(plugins_directory)
    return redirect(request.headers.get("Referer"))


@mod.route("/api/reports/directory")
def report_directory():
    open_directory(reports_directory)
    return redirect(request.headers.get("Referer"))


def open_directory(directory):
    if SystemPlatform.detect() == SystemPlatform.MAC_OS:
        directory = os.path.join("file://", directory)

    webbrowser.open(directory)
