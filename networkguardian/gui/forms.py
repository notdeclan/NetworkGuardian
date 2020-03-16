from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired


class CreateReportForm(FlaskForm):
    """
    Form is used on the Create Report page
    """
    report_name = StringField("Report Name", validators=[DataRequired()])
    plugins = SelectMultipleField("Plugins", validators=[DataRequired()])
    submit = SubmitField("Create Report")


class SettingsForm(FlaskForm):
    """
    Form is used on the Settings page
    """
    report_directory = StringField("Report Directory", validators=[DataRequired()])
    plugin_directory = StringField("Plugin Directory", validators=[DataRequired()])
    report_filename_template = StringField("Report Filename", validators=[DataRequired()])
    threading = BooleanField(label="Multi Threading")

    submit = SubmitField("Update Settings")
