import os

from flask import Flask

from flask_jwt_extended import JWTManager


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'task_manager.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    from . import db
    db.init_app(app)

    from . import task
    app.register_blueprint(task.bp)

    from . import auth
    app.register_blueprint(auth.bp)

    # setup the Flask-JWT-Extended extension
    app.config["JWT_SECRET_KEY"] = "secret-lksfi35it3ioakaer87743egksl&*#"
    jwt = JWTManager(app)

    return app
