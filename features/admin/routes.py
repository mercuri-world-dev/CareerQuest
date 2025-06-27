from flask import Blueprint, render_template
from util.decorators import role_required

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
 
@admin_bp.route('/')
@role_required(['admin'])
def admin_dashboard():
    return render_template('admin_dashboard.html')
