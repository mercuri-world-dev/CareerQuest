from flask import Flask
import os

from services.supabase.supabase_client import get_supabase
from util.auth import get_access_token

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SERVER_NAME=os.environ.get('SERVER_NAME', 'localhost:5001'),
        APPLICATION_ROOT=os.environ.get('APPLICATION_ROOT', '/'),
        PREFERRED_URL_SCHEME=os.environ.get('PREFERRED_URL_SCHEME', 'http'),
    )

    @app.before_request
    def set_supabase_auth():
        access_token = get_access_token()
        supabase = get_supabase()
        if access_token:
            supabase.postgrest.auth(access_token)
    
    from routes import main_bp
    # from features.jobs.routes import jobs_bp
    # from features.jobs.api import jobs_api_bp
    from features.user.routes import user_bp
    from features.auth.routes import auth_bp
    from features.admin.routes import admin_bp
    from features.cms.routes import cms_bp
    if (os.environ.get('FLASK_ENV') == 'development'):
        from debug.routes import debug_bp
        app.register_blueprint(debug_bp, url_prefix='/debug')
    if (os.environ.get('ENABLE_PREVIEW_FEATURES') == 'True'):
        from features.preview.routes import preview_bp
        app.register_blueprint(preview_bp, url_prefix='/preview')
    app.register_blueprint(main_bp)
    # app.register_blueprint(jobs_bp)
    # app.register_blueprint(jobs_api_bp, url_prefix='/api')
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cms_bp, url_prefix='/cms')

    return app