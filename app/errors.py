from flask import jsonify
from werkzeug.exceptions import HTTPException


def handle_exception(e):
    """Global error handler for the Flask application."""
    response = {"error": str(e)}
    status_code = 500
    if isinstance(e, HTTPException):
        # Use the HTTP status code defined by the Flask error
        status_code = e.code
        response["error"] = e.description
    return jsonify(response), status_code
