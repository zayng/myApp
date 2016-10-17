# -*- coding:utf-8 -*-
"""
Created on '2016/5/29'

@author: 'susce'
"""
from flask import Flask
from flask_bootstrap import Bootstrap as Bootstrap
from flask_mail import Mail as Mail
from flask_moment import Moment as Moment
from flask_sqlalchemy import SQLAlchemy as SQLAlchemy
from flask_login import LoginManager as LoginManager
from config import config
from flask_pagedown import PageDown as PageDown
from flask_httpauth import HTTPBasicAuth as HTTPBasicAuth


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
pagedown = PageDown()
hp_auth = HTTPBasicAuth()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    from .api_2_0 import api_bp as api_2_0_blueprint
    app.register_blueprint(api_2_0_blueprint, url_prefix='/api/v2.0')

    return app
