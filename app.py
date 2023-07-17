from flask import Flask
from config.extensions import cors, jwt, migrate, http_exception_handler
from config.api import api
from config.db import db
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object("config.config")
    api.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    http_exception_handler.init_app(app)

    with app.app_context():
        db.create_all()
        
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)