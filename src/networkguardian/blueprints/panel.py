from flask import Blueprint, render_template

"""
    
"""

mod = Blueprint('panel', __name__, static_folder='static', template_folder='templates')


@mod.route('/')
def index():
    things = [1,2,3,4,5,6]
    return render_template('pages/dashboard.html', title="Test title", things = things)


@mod.route('/another-thing')
def another_thing():
    return render_template('pages/another-page.html')