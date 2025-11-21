# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import random
import string
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
load_dotenv()


cloudinary.config(
    cloud_name="dgoijy4ae",
    api_key="736696519882341",
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

class Config(object):
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static')  

    # Secret Key
    SECRET_KEY = os.getenv('SECRET_KEY', "Chr!s@re20025folio")
    if not SECRET_KEY:
        SECRET_KEY = ''.join(random.choice(string.ascii_lowercase) for i in range(32))     

    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Base de données Railway (PostgreSQL) ou fallback SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    )

class ProductionConfig(Config):
    DEBUG = False

    # Sécurité
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600

class DebugConfig(Config):
    DEBUG = True

# Dictionnaire des configurations
config_dict = {
    'Production': ProductionConfig,
    'Debug': DebugConfig
}
