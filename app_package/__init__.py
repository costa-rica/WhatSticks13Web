from flask import Flask
# from app_package.config import config
from ._common.config import config
import os
import logging
from logging.handlers import RotatingFileHandler
from pytz import timezone
from datetime import datetime
# from ws_models import Base, engine, login_manager
from ws_models import Base, engine
from ._common.utilities import login_manager, custom_logger_init, \
    before_request_custom, teardown_request
from flask_mail import Mail
import secure


if not os.path.exists(os.path.join(os.environ.get('WEB_ROOT'),'logs')):
    os.makedirs(os.path.join(os.environ.get('WEB_ROOT'), 'logs'))

logger_init = custom_logger_init()

logger_init.info(f'--- Starting What Sticks 13 Web---')
TEMPORARILY_DOWN = "ACTIVE" if os.environ.get('TEMPORARILY_DOWN') == "1" else "inactive"
logger_init.info(f"- TEMPORARILY_DOWN: {TEMPORARILY_DOWN}")
logger_init.info(f"- WS_CONFIG_TYPE: {os.environ.get('WS_CONFIG_TYPE')}")


if os.environ.get('WS_CONFIG_TYPE')=='workstation':
    logger_init.info(f"- ! This should not print if not local ! -")
    logger_init.info(f"- SQL_URI_WHAT_STICKS_DB: {config.SQL_URI_WHAT_STICKS_DB}")
    logger_init.info(f"- ! This should not print if not local ! -")


mail = Mail()
secure_headers = secure.Secure()

def create_app(config_for_flask = config):
    app = Flask(__name__)
    # app.teardown_appcontext(teardown_appcontext)
    
    app.before_request(before_request_custom)
    app.teardown_request(teardown_request)
    app.config.from_object(config_for_flask)
    login_manager.init_app(app)
    mail.init_app(app)


    ############################################################################
    ## create folders for PROJECT_RESOURCES
    create_folder(config_for_flask.PROJECT_RESOURCES)
    create_folder(config_for_flask.DIR_LOGS)
    # website files
    create_folder(config_for_flask.WEBSITE_FILES)
    create_folder(config_for_flask.DIR_WEBSITE_UTILITY_IMAGES)
    create_folder(config_for_flask.DIR_WEBSITE_VIDEOS)
    create_folder(config_for_flask.DB_UPLOAD)
    # user files
    create_folder(config_for_flask.USER_FILES)
    create_folder(config_for_flask.DAILY_CSV)
    create_folder(config_for_flask.RAW_FILES_FOR_DAILY_CSV)
    ############################################################################
    # Build MySQL database
    # Base.metadata.create_all(engine)
    logger_init.info(f"- MYSQL_USER: {config_for_flask.MYSQL_USER}")
    logger_init.info(f"- MYSQL_DATABASE_NAME: {config_for_flask.MYSQL_DATABASE_NAME}")

    from app_package.bp_main.routes import bp_main
    from app_package.bp_users.routes import bp_users
    from app_package.bp_admin.routes import bp_admin
    from app_package.bp_error.routes import bp_error
 
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_users)
    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_error)

    return app

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger_init.info(f"created: {folder_path}")