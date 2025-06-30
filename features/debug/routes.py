from flask import Blueprint, render_template

debug_bp = Blueprint('debug', __name__, template_folder='templates', static_folder='static')

@debug_bp.route('/job-card')
def job_card():
    return render_template('jobCard.html')