# -*- encoding: utf-8 -*-

from flask import Flask
from app.extensions import db, login_manager, migrate, bcrypt, socketio, mail, csrf
from importlib import import_module
import os
from app.utils.decorator.time import humanize_date

api_meteo = "d07586380ddddf89d032e74098364b8d"

# --- CORRECTION DÉBUT ---
# Vercel utilise un système de fichiers en lecture seule, sauf pour /tmp
if os.environ.get('VERCEL'):
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
# --- CORRECTION FIN ---

# Limiter la taille max des fichiers (100 Mo)
MAX_CONTENT_LENGTH = 100 * 1024 * 1024 

def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth_blueprint.login"
    login_manager.login_message_category = 'info'

def register_blueprints(app):
    for module_name in ('authentication', 'home', 'admin'):
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def register_custom_filters(app: Flask):
    app.jinja_env.filters['humanize_date'] = humanize_date

def create_app(config="app.config.Config"):
    app = Flask(__name__)

    @app.after_request
    def apply_security_headers(response):
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        response.headers["Content-Security-Policy"] = "default-src *"
        return response
        
    app.config.from_object(config)
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Utile pour récupérer le chemin dans vos routes

    register_extensions(app)
    register_blueprints(app)
    register_custom_filters(app)

    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(user_id):
        from app.utils.authentication.models import User
        return User.query.get(int(user_id))

    return app