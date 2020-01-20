from flask import Blueprint, render_template

mod = Blueprint('panel', __name__, static_folder='static', template_folder='templates')


@mod.route('/')
def index():
    return render_template('pages/dashboard.html', title="Dashboard")
