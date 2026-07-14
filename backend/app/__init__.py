import os

from flask import Flask, jsonify
from flask_security import SQLAlchemyUserDatastore

from .config import Config
from .extensions import cors, db, migrate, security


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        instance_relative_config=True,
    )

    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize database extensions.
    db.init_app(app)
    migrate.init_app(app, db)

    # Configure CORS for the future Vue frontend.
    cors.init_app(
        app,
        resources={
            r"/*": {
                "origins": app.config.get(
                    "CORS_ORIGINS",
                    [
                        "http://localhost:5173",
                        "http://127.0.0.1:5173",
                    ],
                ),
            }
        },
        supports_credentials=False,
    )

    # Models must be imported before initializing Flask-Security.
    from .models import Role, User

    user_datastore = SQLAlchemyUserDatastore(
        db,
        User,
        Role,
    )

    security.init_app(
        app,
        user_datastore,
        register_blueprint=False,
    )

    # Force failed authentication responses to use JSON.
    @security.unauthn_handler
    def handle_unauthenticated(mechanisms=None, headers=None):
        response = jsonify(
            {
                "success": False,
                "message": "Authentication is required.",
                "errors": {
                    "authentication": [
                        "Provide a valid authentication token."
                    ],
                },
            }
        )

        if headers:
            for header_name, header_value in headers.items():
                response.headers[header_name] = header_value

        return response, 401

    # Force failed role/permission checks to use JSON.
    @security.unauthz_handler
    def handle_unauthorized(function_name, parameters):
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "You are not authorized to access this resource."
                    ),
                    "errors": {
                        "authorization": [
                            "The account does not have the required access."
                        ],
                    },
                }
            ),
            403,
        )

    from .auth_routes import auth_bp

    app.register_blueprint(auth_bp)

    @app.get("/")
    def index():
        return (
            jsonify(
                {
                    "success": True,
                    "message": (
                        "Coding Performance Analytics Dashboard API"
                    ),
                    "data": {
                        "version": "1.0.0",
                    },
                }
            ),
            200,
        )

    @app.get("/api/health")
    def health_check():
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Backend is running.",
                    "data": {
                        "status": "healthy",
                    },
                }
            ),
            200,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "The requested resource was not found.",
                    "errors": {
                        "resource": [
                            "No API endpoint exists at this URL."
                        ],
                    },
                }
            ),
            404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "The requested HTTP method is not allowed."
                    ),
                    "errors": {
                        "method": [
                            "Use the HTTP method defined for this endpoint."
                        ],
                    },
                }
            ),
            405,
        )

    @app.errorhandler(500)
    def handle_internal_server_error(_error):
        db.session.rollback()

        return (
            jsonify(
                {
                    "success": False,
                    "message": "An internal server error occurred.",
                    "errors": {
                        "server": [
                            "The server could not complete the request."
                        ],
                    },
                }
            ),
            500,
        )

    return app