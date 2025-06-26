from flask import Flask
import os

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=True)
    
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production'),  # TODO: Change this in production
        SERVER_NAME=os.environ.get('SERVER_NAME', 'localhost:5001'),
        APPLICATION_ROOT=os.environ.get('APPLICATION_ROOT', '/'),
        PREFERRED_URL_SCHEME=os.environ.get('PREFERRED_URL_SCHEME', 'http'),
    )
    
    # Register blueprints
    from main.routes import main_bp
    from features.jobs.routes import jobs_bp
    # from features.jobs.api import jobs_api_bp
    from features.user.routes import user_bp
    # from features.company.routes import company_bp
    from features.auth.routes import auth_bp
    from features.admin.routes import admin_bp
    from features.cms.routes import cms_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(jobs_bp)
    # app.register_blueprint(jobs_api_bp, url_prefix='/api/jobs')
    app.register_blueprint(user_bp)
    # app.register_blueprint(company_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(cms_bp, url_prefix='/cms')

    return app