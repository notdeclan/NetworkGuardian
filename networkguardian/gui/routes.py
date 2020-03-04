import os
import webbrowser

import webview
from flask import render_template, flash, redirect, url_for, abort, jsonify, request

from networkguardian import reports_directory, plugins_directory, logger, application_name, application_version
from networkguardian.framework.plugin import SystemPlatform
from networkguardian.framework.registry import registered_plugins, usable_plugins, import_external_plugins, load_plugins
from networkguardian.framework.report import reports, processing_reports, start_report, export_report_as_html, \
    generate_report_filename, report_extension, report_filename_template
from networkguardian.gui import app, window
from networkguardian.gui.forms import SettingsForm, CreateReportForm


@app.errorhandler(404)
def page_not_found(e):
    return render_template('pages/404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    flash("An unexpected error occurred, see the Log for more information.")
    return render_template('pages/dashboard.html'), 500


@app.after_request
def add_header(response):
    """
    Event listener function is required to prevent browsers from caching page content stopping them from being able to
    update automatically.
    """
    response.headers['Cache-Control'] = 'no-store'  # disable caching
    return response


@app.context_processor
def template_injector():
    return {
        "application_name": application_name,
        "application_version": application_version
    }


@app.route('/')
def index():
    return render_template('pages/dashboard.html',
                           plugins=registered_plugins,
                           reports=reports)


@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()

    if form.validate_on_submit():
        plugin_directory = form.plugin_directory
        report_directory = form.report_directory
        n_report_filename_template = form.report_filename_template
        threading = form.threading

        # TODO: Save this to config
        flash("Updated settings")
    else:
        form.plugin_directory.data = plugins_directory
        form.report_directory.data = reports_directory
        form.report_filename_template.data = report_filename_template
        form.threading.data = True

    return render_template("pages/settings.html", form=form, report_extension=report_extension)


@app.route('/plugins/')
def view_plugins():
    return render_template('pages/plugins.html', plugins=registered_plugins.values())


@app.route('/plugins/<plugin_name>')
def view_plugin(plugin_name: str):
    if plugin_name in registered_plugins:
        return render_template('pages/view-plugin.html', plugin=registered_plugins[plugin_name])

    return abort(404)


@app.route('/reports/create', methods=['GET', 'POST'])
def create_report():
    form = CreateReportForm()
    form.plugins.choices = [(plugin.name, plugin.name) for plugin in usable_plugins()]

    if form.validate_on_submit():
        report_name = form.report_name.data
        selected_plugins = [registered_plugins[plugin] for plugin in form.plugins.data]
        logger.info(f"Creating report {report_name}, with {selected_plugins}")

        thread_id = start_report(report_name, selected_plugins)

        return redirect(url_for("process_report", thread_id=thread_id))

    return render_template('pages/create-report.html', form=form)


@app.route('/reports/create/quick')
def quick_report():
    thread_id = start_report("Quick Scan", usable_plugins())
    return redirect(url_for("process_report", thread_id=thread_id))


@app.route('/reports/processing/<int:thread_id>')
def process_report(thread_id):
    if thread_id in processing_reports:
        report_processor = processing_reports[thread_id]
        if report_processor.progress >= 100 and not report_processor.isAlive():
            flash("Report completed")

            return redirect(url_for("view_report", report_id=report_processor.report_id))

        return render_template('pages/processing-report.html', report=report_processor)

    return abort(404)


@app.route('/reports/progress/<int:thread_id>')
def report_progress(thread_id):
    if thread_id in processing_reports:
        return jsonify({
            "progress": processing_reports[thread_id].progress
        })

    # TODO: Use this rather than refreshing whole page
    # TODO: add to api probs
    return abort(404)


@app.route('/reports/')
def view_reports():
    return render_template('pages/reports.html', reports=reports)


@app.route('/reports/<int:report_id>')
def view_report(report_id: int):
    try:
        return render_template('pages/view-report.html', report=reports[report_id], report_id=report_id)
    except IndexError:
        return abort(404)


@app.route('/reports/export/<int:report_id>')
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


@app.route("/reports/delete/<int:report_id>")
def delete_report(report_id: int):
    try:
        report = reports[report_id]
        os.remove(report.path)  # remove file
        reports.remove(report)  # remove from list
        flash(f"Removed report {report.name}")

        return redirect(url_for("view_reports"))
    except IndexError:
        return abort(404)
    except IOError:
        flash("Error occurred while attempting to delete report file")
        return render_template('pages/view-report.html', report=reports[report_id], report_id=report_id)


@app.route('/help/view')
def view_help():
    return render_template('pages/help.html')


@app.route("/api/plugins/refresh")
def refresh_plugins():
    import_external_plugins(plugins_directory)
    load_plugins()

    flash("Refreshed Plugins")

    return redirect(request.headers.get("Referer"))


@app.route("/api/plugins/directory")
def plugin_directory():
    open_directory(plugins_directory)
    return redirect(request.headers.get("Referer"))


@app.route("/api/reports/directory")
def report_directory():
    open_directory(reports_directory)
    return redirect(request.headers.get("Referer"))


def open_directory(directory):
    if SystemPlatform.detect() == SystemPlatform.MAC_OS:
        directory = os.path.join("file://", directory)

    webbrowser.open(directory)
