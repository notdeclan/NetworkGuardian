from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired


class CreateReportForm(FlaskForm):
    report_name = StringField("Report Name", validators=[DataRequired()])
    plugins = SelectMultipleField("Plugins", validators=[DataRequired()])
    submit = SubmitField("Create Report")
