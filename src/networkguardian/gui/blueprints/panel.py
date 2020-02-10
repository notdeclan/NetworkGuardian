import os
import sys

from flask import Blueprint, render_template

from networkguardian import is_frozen
from networkguardian.framework.registry import registered_plugins
from networkguardian.framework.report import Report

"""
    TODO: Explain this file ... 
"""

if is_frozen:  # if frozen
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')

    mod = Blueprint('panel', __name__, static_folder=static_folder, template_folder=template_folder)
else:  # if not frozen
    mod = Blueprint('panel', __name__, static_folder='../static', template_folder='templates')


@mod.route('/')
def index():
    plugin_count = len(registered_plugins)  # total amount of plugin's loaded
    previous_scans = 10000

    test_report = Report("LOL")
    recent_scans = [test_report]

    #  usable_plugins = [p for p in registered_plugins if p.supported]  TODO: easy way to get supported plugins

    return render_template('pages/dashboard.html',
                           plugin_count=plugin_count,
                           previous_scans=previous_scans,
                           recent_scans=recent_scans[-3:])


@mod.route('/scans/view')
def another_thing():
    return render_template('pages/another-page.html')
