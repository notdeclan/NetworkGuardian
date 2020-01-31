from flask import Blueprint, render_template

from networkguardian import application_version
from networkguardian.report import Report

"""
    TODO: Explain this file ... 
"""

mod = Blueprint('panel', __name__, static_folder='static', template_folder='templates')


@mod.route('/')
def index():
    plugin_count = 4  # total amount of plugin's loaded
    previous_scans = 10000

    test_report = Report("TEST_PC_DAD", "12:12:40", application_version)
    recent_scans = [test_report]

    return render_template('pages/dashboard.html', plugin_count=plugin_count, previous_scans=previous_scans, recent_scans=recent_scans)


@mod.route('/scans/view')
def another_thing():
    return render_template('pages/another-page.html')