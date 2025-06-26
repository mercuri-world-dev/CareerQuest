from flask import Blueprint, render_template, redirect, url_for, flash, request
from util.decorators import role_required
from main.supabase_client import get_supabase

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
 
@admin_bp.route('/')
@role_required(['admin'])
def admin_dashboard():
    return render_template('admin_dashboard.html')
