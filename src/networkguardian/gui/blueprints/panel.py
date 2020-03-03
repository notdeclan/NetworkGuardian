import os
import sys

import webview
from flask import Blueprint, render_template, abort, redirect, url_for, jsonify, flash

from networkguardian import application_frozen, plugins_directory, reports_directory, window, logger
from networkguardian.framework.registry import registered_plugins, usable_plugins
from networkguardian.framework.report import reports, processing_reports, report_filename_template, \
    report_extension, start_report, export_report_as_html, generate_report_filename
from networkguardian.gui.forms import CreateReportForm, SettingsForm

"""
    TODO: Explain this file ... 
"""

if application_frozen:  # if frozen
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')

    mod = Blueprint('panel', __name__, url_prefix="/", static_folder=static_folder, template_folder=template_folder)
else:  # if not frozen
    mod = Blueprint('panel', __name__, url_prefix="/", static_folder='../static', template_folder='templates')


@mod.errorhandler(404)
def page_not_found():
    # TODO: Fix, maybe add to server mod instead of panel.mod
    return render_template('pages/404.html'), 404


@mod.route('/')
def index():
    return render_template('pages/dashboard.html',
                           plugins=registered_plugins,
                           reports=reports)


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

    return render_template("pages/settings.html", form=form, report_extension=report_extension)


@mod.route('/plugins/')
def view_plugins():
    return render_template('pages/plugins.html', plugins=registered_plugins.values())


@mod.route('/plugins/<plugin_name>')
def view_plugin(plugin_name: str):
    if plugin_name in registered_plugins:
        return render_template('pages/view-plugin.html', plugin=registered_plugins[plugin_name])

    return abort(404)


@mod.route('/reports/create', methods=['GET', 'POST'])
def create_report():
    form = CreateReportForm()
    form.plugins.choices = [(plugin.name, plugin.name) for plugin in usable_plugins()]

    if form.validate_on_submit():
        report_name = form.report_name.data
        selected_plugins = [registered_plugins[plugin] for plugin in form.plugins.data]
        logger.info(f"Creating report {report_name}, with {selected_plugins}")

        thread_id = start_report(report_name, selected_plugins)

        return redirect(url_for("panel.process_report", thread_id=thread_id))

    return render_template('pages/create-report.html', form=form)


@mod.route('/reports/create/quick')
def quick_report():
    thread_id = start_report("Quick Scan", usable_plugins())
    return redirect(url_for("panel.process_report", thread_id=thread_id))


@mod.route('/reports/processing/<int:thread_id>')
def process_report(thread_id):
    if thread_id in processing_reports:
        report_processor = processing_reports[thread_id]
        if report_processor.progress >= 100 and not report_processor.isAlive():
            flash("Report completed")
            return redirect(url_for("panel.view_report", report_id=report_processor.report_id))

        return render_template('pages/processing-report.html', report=report_processor)

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
    return render_template('pages/reports.html', reports=reports)


@mod.route('/reports/<int:report_id>')
def view_report(report_id: int):
    try:
        return render_template('pages/view-report.html', report=reports[report_id], report_id=report_id)
    except IndexError:
        return abort(404)


@mod.route('/reports/export/<int:report_id>')
def export_report(report_id: int):
    try:
        report = reports[report_id]
        report_filename = generate_report_filename(report, "html")

        save_path = window.create_file_dialog(webview.SAVE_DIALOG, directory='/', save_filename=report_filename)

        if save_path is not None:
            export_report_as_html(report, save_path[0])
            flash(f"Exported {report.name} to {save_path}")

    except IndexError:
        return abort(404)
    except IOError:
        flash("Exporting report failed")

    return render_template('pages/view-report.html', report=reports[report_id], report_id=report_id)


@mod.route("/reports/delete/<int:report_id>")
def delete_report(report_id: int):
    try:
        report = reports[report_id]
        os.remove(report.path)  # remove file
        reports.remove(report)  # remove from list
        flash(f"Removed report {report.name}")

        return redirect(url_for("panel.view_reports"))
    except IndexError:
        return abort(404)
    except IOError:
        flash("Error occurred while attempting to delete report file")
        return render_template('pages/view-report.html', report=reports[report_id], report_id=report_id)


@mod.route('/help/view')
def view_help():
    return render_template('pages/help.html')
