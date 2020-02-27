import os
import sys
from random import randint

from flask import Blueprint, render_template, abort, redirect, url_for, jsonify, flash

from networkguardian import application_frozen, plugins_directory, reports_directory
from networkguardian.framework.registry import registered_plugins, usable_plugins
from networkguardian.framework.report import reports, processing_reports, ReportProcessor, report_filename_template
from networkguardian.gui.forms import CreateReportForm, SettingsForm

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


@mod.errorhandler(404)
def page_not_found():
    # TODO: Fix, maybe add to server mod instead of panel.mod
    return render_template('pages/404.html')


@mod.route('/')
def index():
    #  usable_plugins = [p for p in registered_plugins if p.supported]  TODO: easy way to get supported plugins
    return render_template('pages/dashboard.html',
                           plugins=registered_plugins,
                           reports=list(reports.values()))


@mod.route('/settings/', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        plugin_directory = form.plugin_directory
        report_directory = form.report_directory
        n_report_filename_template = form.report_filename_template
        threading = form.threading
    else:
        form.plugin_directory.data = plugins_directory
        form.report_directory.data = reports_directory
        form.report_filename_template.data = report_filename_template
        form.threading.data = True

    return render_template("pages/settings.html", form=form)


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

        return redirect(url_for("panel.process_report", thread_id=rand_thread_id))

    return render_template('pages/create-report.html', form=form)


@mod.route('/reports/create/quick')
def quick_report():
    processor = ReportProcessor("Quick Report", usable_plugins())
    processor.daemon = True
    processor.start()

    rand_thread_id = randint(0, 10000)
    processing_reports[rand_thread_id] = processor

    return redirect(url_for("panel.process_report", thread_id=rand_thread_id))


@mod.route('/reports/processing/<int:thread_id>')
def process_report(thread_id):
    if thread_id in processing_reports:
        report = processing_reports[thread_id]
        if report.progress >= 100:
            flash("Report completed")
            return redirect(url_for("panel.view_report", report_name=report.report_name))

        return render_template('pages/processing-report.html', report=report)

    return abort(404)


@mod.route('/reports/progress/<int:thread_id>')
def report_progress(thread_id):
    if thread_id in processing_reports:
        return jsonify({"progress": processing_reports[thread_id].progress})

    # TODO: Use this rather than refreshing whole page
    # TODO: add to api probs

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
