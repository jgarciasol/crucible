from flask import Flask
from .start.routes import start
from .auth import auth
from .extensions import db
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crucible_data.db'

    db.init_app(app)

    app.register_blueprint(start)
    app.register_blueprint(auth)

    from . import models    #do not delete or move this, it is needed for the database to load properly

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    return app
