import sys
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template, jsonify

from app import models
import config as cf


def create_tmp_dir(static_folder):
    tmp_dir = os.path.join(static_folder, cf.TMPDIR)
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)


def file_logging():
    log_file = os.path.join(cf.db_path, 'sqa.log')
    file_handler = RotatingFileHandler(log_file, 'a', 10 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    return file_handler


def internal_server_error(err):
    return render_template('500.html', error=err.description), 500


def page_not_found(e):
    return render_template('404.html'), 404


def method_not_allowed(err):
    return render_template('405.html', err=err), 405


def create_web_app(config):

    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'static')
        app = Flask(__name__, template_folder=template_folder,
                    static_folder=static_folder)
    else:
        app = Flask(__name__)

    app.config.from_object(config)
    models.db_wrapper.init_app(app)

    from app.views.problems import pbp
    #from app.views.organisations import org_bp
    from app.views.components import component_bp
    from app.views.car_models import carmodel_bp
    from app.views.common import common_bp
    
    app.register_blueprint(pbp)
    #app.register_blueprint(org_bp)
    app.register_blueprint(component_bp)
    app.register_blueprint(carmodel_bp)
    app.register_blueprint(common_bp)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)
    app.register_error_handler(405, method_not_allowed)
    
    create_tmp_dir(app.static_folder)
    
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_logging())
    app.logger.info('SQA startup')
    
    return app
