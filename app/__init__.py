from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from celery import Celery
import os

db = SQLAlchemy()
migrate = Migrate()
celery = Celery(__name__, broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))


def create_app(config_name='default'):
    from app.config import config

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    celery.conf.update(app.config)

    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.models import User, Subscription, EmailAccount, EmailMessage, AIRequest

    with app.app_context():
        db.create_all()

    return app