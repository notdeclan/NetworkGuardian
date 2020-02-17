import os
import sys
from random import randint

from flask import Blueprint, render_template, abort

from networkguardian import application_frozen
from networkguardian.framework.registry import registered_plugins, usable_plugins
from networkguardian.framework.report import reports, processing_reports, ReportProcessor
from networkguardian.gui.forms import CreateReportForm

"""
    TODO: Explain this file ... 
    TODO: Flask "flashes" for notification'
"""

if application_frozen:  # if frozen
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')

    mod = Blueprint('panel', __name__, static_folder=static_folder, template_folder=template_folder)
else:  # if not frozen
    mod = Blueprint('panel', __name__, static_folder='../static', template_folder='templates')


@mod.route('/')
def index():
    #  usable_plugins = [p for p in registered_plugins if p.supported]  TODO: easy way to get supported plugins
    return render_template('pages/dashboard.html',
                           plugins=registered_plugins,
                           reports=list(reports.values()))


@mod.route('/reports/create', methods=['GET', 'POST'])
def create_report():
    form = CreateReportForm()
    form.plugins.choices = [(plugin.name, plugin.name) for plugin in usable_plugins()]

    if form.validate_on_submit():
        report_name = form.report_name.data
        selected_plugins = []
        for plugin in form.plugins.data:
            selected_plugins.append(registered_plugins[plugin])

        print(f"Creating report {report_name}, with {selected_plugins}")

        processor = ReportProcessor(report_name, selected_plugins)
        processor.daemon = True
        processor.start()

        rand_thread_id = randint(0, 10000)
        processing_reports[rand_thread_id] = processor

        return process_report(rand_thread_id)

    return render_template('pages/create-report.html', form=form)


@mod.route('/reports/processing/<int:thread_id>')
def process_report(thread_id):
    if thread_id in processing_reports:
        return render_template('pages/processing-report.html', report=processing_reports[thread_id])

    return abort(404)


@mod.route('/reports/')
def view_reports():
    return render_template('pages/reports.html', reports=reports.values())


@mod.route('/plugins/')
def view_plugins():
    return render_template('pages/plugins.html', plugins=registered_plugins.values())


@mod.route('/reports/<report_name>')
def view_report(report_name):
    if report_name in reports:
        return render_template('pages/view-report.html', report=reports[report_name])

    return abort(404)


@mod.route('/plugins/<plugin_name>')
def view_plugin(plugin_name: str):
    if plugin_name in registered_plugins:
        return render_template('pages/view-plugin.html', plugin=registered_plugins[plugin_name])

    return abort(404)


@mod.route('/help/view')
def view_help():
    return render_template('pages/help.html')
