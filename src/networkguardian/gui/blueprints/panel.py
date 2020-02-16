import os
import sys

from flask import Blueprint, render_template, abort

from networkguardian import is_frozen
from networkguardian.framework.registry import registered_plugins
from networkguardian.framework.report import Report

"""
    TODO: Explain this file ... 
    TODO: Flask "flashes" for notification'
"""

if is_frozen:  # if frozen
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')

    mod = Blueprint('panel', __name__, static_folder=static_folder, template_folder=template_folder)
else:  # if not frozen
    mod = Blueprint('panel', __name__, static_folder='../static', template_folder='templates')


@mod.route('/')
def index():
    test_report = Report("LOL")
    another_report = Report("ANOTHER")
    most_recent_report = Report("i should be at tjhe top")
    recent_reports = [test_report, another_report, another_report, another_report, another_report, test_report,
                      most_recent_report]

    #  usable_plugins = [p for p in registered_plugins if p.supported]  TODO: easy way to get supported plugins

    return render_template('pages/dashboard.html',
                           plugins=registered_plugins,
                           reports=recent_reports)


@mod.route('/reports/create')
def create_report():
    return render_template('pages/view-report.html',
                           plugins=registered_plugins)


@mod.route('/reports/')
def view_reports():
    test_report = Report("LOL")
    another_report = Report("ANOTHER")
    most_recent_report = Report("i should be at tjhe top")
    recent_reports = [test_report, another_report, another_report, another_report, another_report, test_report,
                      most_recent_report]

    return render_template('pages/reports.html', reports=recent_reports)


@mod.route('/plugins/')
def view_plugins():
    return render_template('pages/plugins.html', plugins=registered_plugins.values())


@mod.route('/plugins/<plugin_name>')
def view_plugin(plugin_name: str):
    if plugin_name in registered_plugins:
        return render_template('pages/view-plugin.html', plugin=registered_plugins[plugin_name])

    return abort(404)


@mod.route('/help/view')
def view_help():
    return render_template('pages/help.html')
