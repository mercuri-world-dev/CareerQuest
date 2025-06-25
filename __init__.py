from flask import Flask, redirect, session, url_for
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, logout_user
import os

from database import db, User, Role, CompanyProfile, Job

from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    # if config_object:
    #     app.config.from_object(config_object)
    # else:
    #     app.config.from_pyfile('config.py', silent=True)

    # Default config (if not set in config.py)
    # app.config.setdefault('SECRET_KEY', 'your-secret-key-change-in-production') # TODO: Change this in production
    # app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite:///careerquest.db')
    # app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    # app.config.setdefault('SESSION_REFRESH_EACH_REQUEST', True)
    # app.config.setdefault('PERMANENT_SESSION_LIFETIME', 3600)
    # app.config.setdefault('SESSION_TYPE', 'filesystem')
    # app.config.setdefault('SESSION_FILE_DIR', os.path.join(os.getcwd(), 'flask_session'))
    # app.config.setdefault('SESSION_USE_SIGNER', True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production'),  # TODO: Change this in production
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///careerquest.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_REFRESH_EACH_REQUEST=True,
        PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
        SESSION_TYPE='filesystem',
        SESSION_FILE_DIR=os.path.join(os.getcwd(), 'flask_session'),
        SESSION_USE_SIGNER=True,
        TESTING_AUTO_LOGIN_USER=False, # TODO: Remove this in production, only for testing purposes
        TESTING_AUTO_LOGIN_COMPANY=False  # TODO: Remove this in production, only for testing purposes
    )

    CORS(app)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @app.before_request
    def auto_login_test_user():
        if app.config.get("TESTING_AUTO_LOGIN_USER", False):
            from flask_login import current_user
            if not current_user.is_authenticated:
                user = User.query.filter_by(username="ARealPerson").first()
                if user:
                    login_user(user)
                    redirect(url_for('users.dashboard'))

    @app.before_request
    def auto_login_test_company():
        if app.config.get("TESTING_AUTO_LOGIN_COMPANY", False):
            from flask_login import current_user
            if not current_user.is_authenticated:
                user = User.query.filter_by(username="arealcompany").first()
                if user:
                    login_user(user)
                    redirect(url_for('company.company_dashboard'))

    @app.before_request
    def clear_session_on_restart():
        """Force logout on server restart"""
        # Check if user is authenticated but session has a different server instance
        server_id = os.environ.get('SERVER_INSTANCE_ID', os.getpid())
        if 'server_id' not in session:
            # New session or server restarted
            session['server_id'] = server_id
            # If user was authenticated, log them out
            if current_user.is_authenticated:
                logout_user()
        elif session.get('server_id') != server_id:
            # Server restarted with existing session
            session['server_id'] = server_id
            if current_user.is_authenticated:
                logout_user()

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user = db.session.get(User, int(user_id))
            if user is None:
                return None
            return user
        except Exception:
            return None

    # Admin views with access control
    class MyAdminIndexView(AdminIndexView):
        @expose('/')
        def index(self):
            from flask_login import current_user
            if not current_user.is_authenticated or not current_user.has_role('admin'):
                from flask import redirect, url_for
                return redirect(url_for('auth.login'))
            return super(MyAdminIndexView, self).index()

    class SecureModelView(ModelView):
        def is_accessible(self):
            from flask_login import current_user
            return current_user.is_authenticated and current_user.has_role('admin')
        def inaccessible_callback(self, name, **kwargs):
            from flask import redirect, url_for
            return redirect(url_for('auth.login'))

    admin = Admin(
        app,
        name='CareerQuest Admin',
        template_mode='bootstrap3',
        index_view=MyAdminIndexView()
    )
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Role, db.session))
    admin.add_view(SecureModelView(CompanyProfile, db.session))
    admin.add_view(SecureModelView(Job, db.session))

    # Register blueprints
    from main.routes import main_bp
    from features.jobs.routes import jobs_bp
    from features.jobs.api import jobs_api_bp
    from features.user.routes import user_bp
    from features.company.routes import company_bp
    from features.auth.routes import auth_bp
    from features.auth.routes import auth_bp
    # from admin.routes import admin_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(jobs_api_bp, url_prefix='/api/')
    app.register_blueprint(user_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(auth_bp)
    # app.register_blueprint(admin_bp)

    return app


