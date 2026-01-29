from flask import jsonify
from werkzeug.exceptions import HTTPException
from ptracker.datasources.base import (
    DataSourceError,
    ProductNotFoundError,
    RateLimitError,
)


def register_error_handlers(app):

    @app.errorhandler(ValueError)
    def handle_value_error(e):
        """Handle ValueError exceptions (validation errors, not found, etc.)"""
        return jsonify({"success": False, "error": str(e)}), 400

    @app.errorhandler(ProductNotFoundError)
    def handle_product_not_found(e):
        """Handle product not found from data sources"""
        return jsonify({"success": False, "error": "Product not found"}), 404

    @app.errorhandler(RateLimitError)
    def handle_rate_limit(e):
        """Handle API rate limit errors"""
        return (
            jsonify(
                {"success": False, "error": "Rate limit exceeded. Try again later."}
            ),
            429,
        )

    @app.errorhandler(DataSourceError)
    def handle_data_source_error(e):
        """Handle general data source errors"""
        return jsonify({"success": False, "error": f"Data source error: {str(e)}"}), 502

    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 Not Found errors"""
        return jsonify({"success": False, "error": "Resource not found"}), 404

    @app.errorhandler(401)
    def handle_unauthorized(e):
        """Handle 401 Unauthorized errors"""
        error_message = e.description if e.description else "Unauthorized"
        return jsonify({"success": False, "error": error_message}), 401

    @app.errorhandler(500)
    def handle_internal_error(e):
        """Handle 500 Internal Server errors"""
        return jsonify({"success": False, "error": "Internal server error"}), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle all other HTTP exceptions"""
        return jsonify({"success": False, "error": e.description}), e.code
