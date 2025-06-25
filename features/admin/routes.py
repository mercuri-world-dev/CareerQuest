from flask import Blueprint, render_template, redirect, url_for, flash, request
from util.decorators import role_required
from main.supabase_client import get_supabase

admin_bp = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

@admin_bp.route('/')
@role_required('admin')
def admin_dashboard():
    supabase = get_supabase()
    users_resp = supabase.table('users').select('*').execute()
    roles_resp = supabase.table('roles').select('*').execute()
    user_roles_resp = supabase.table('user_roles').select('*').execute()
    users = users_resp.data or []
    roles = roles_resp.data or []
    user_roles = user_roles_resp.data or []
    user_id_to_roles = {}
    for ur in user_roles:
        user_id_to_roles.setdefault(ur['user_id'], []).append(ur['role_id'])
    for user in users:
        user['roles'] = [role for role in roles if role['id'] in user_id_to_roles.get(user['id'], [])]
    return render_template('admin_dashboard.html', users=users, roles=roles)

@admin_bp.route('/user/<int:user_id>/add_role', methods=['POST'])
@role_required('admin')
def add_role_to_user(user_id):
    supabase = get_supabase()
    role_id = request.form.get('role_id')
    if role_id:
        # Check if already exists
        exists = supabase.table('user_roles').select('*').eq('user_id', user_id).eq('role_id', role_id).execute()
        if not exists.data:
            supabase.table('user_roles').insert({'user_id': user_id, 'role_id': role_id}).execute()
            flash('Role added to user.', 'success')
        else:
            flash('User already has this role.', 'warning')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/user/<int:user_id>/remove_role', methods=['POST'])
@role_required('admin')
def remove_role_from_user(user_id):
    supabase = get_supabase()
    role_id = request.form.get('role_id')
    if role_id:
        supabase.table('user_roles').delete().eq('user_id', user_id).eq('role_id', role_id).execute()
        flash('Role removed from user.', 'success')
    return redirect(url_for('admin.admin_dashboard'))
