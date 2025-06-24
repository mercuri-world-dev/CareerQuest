# from gotrue import SyncSupportedStorage
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from database import Role, User, db

auth_bp = Blueprint('auth', __name__, template_folder='templates', static_folder='static', static_url_path='/static/auth')

print("AUTH STATIC FOLDER:", auth_bp.static_folder)                
# @auth_bp.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         if not email or not password:
#             flash('Email and password are required', 'warning')
#             return redirect(url_for('auth.login'))
        
#         res = supabase.auth.sign_in_with_password(email=email, password=password)
#         if res.error:
#             flash('Login failed: ' + res.error.message, 'error')
#             return redirect(url_for('auth.login'))
        
#         return redirect(url_for('main.index'))
#     return render_template('auth/login.html')

# @auth_bp.route('/register')
# def register():
#     return render_template('auth/register.html')

# @auth_bp.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('main.index')) # TODO: import index route')

# @auth_bp.route('/login/callback')
# def callback():
#     code = request.args.get('code')
#     if not code:
#         return redirect(url_for('auth.login'))
#     next = request.args.get('next', url_for('main.index'))
#     res = supabase.auth.exchange_code_for_session(code, redirect_to=next)
#     if res.error:
#         flash('Login failed: ' + res.error.message, 'error')
#         return redirect(url_for('auth.login'))
#     return redirect(next)

# @auth_bp.route('/login/google')
# def google_login():
#     res = supabase.auth.sign_in_with_oauth(
#         {
#             'provider': 'google',
#             'options': {
#                 'redirect_to': url_for('auth.callback')
#             }
#         }
#     )
#     return redirect(res.url)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any potentially stale session data
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        logout_user()
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            
            # Redirect to appropriate dashboard based on role
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.index'))
                
        flash('Invalid username or password')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    # After logout, explicitly redirect to the landing page
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Clear any potentially stale session data
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        logout_user()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        account_type = request.form.get('account_type', 'user')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))
            
        user = User(username=username, email=email)
        user.set_password(password)
        
        # Assign role based on account type
        role = Role.query.filter_by(name=account_type).first()
        if role:
            user.roles.append(role)
            print(f"Assigned role {role.name} to user {username}")
        else:
            print(f"Role {account_type} not found")
            
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'message')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')


