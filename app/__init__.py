from flask import Flask

from .extensions import db, migrate
from .config import Config
from .errors import handle_exception


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import bp as sales_bp

    app.register_blueprint(sales_bp)

    app.register_error_handler(Exception, handle_exception)

    return app
