from flask import Flask
from .start.routes import start
from .extensions import db

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(start)
    return app

cruciblefit = create_app()

if __name__ == '__main__':
    cruciblefit.run(debug=True)