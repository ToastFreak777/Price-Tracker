"""Dependency injection setup for services"""

from flask import g


def init_services(app):
    """Initialize service dependency injection via Flask g"""

    @app.before_request
    def setup_services():
        """Create service instances for each request"""
        from ptracker.auth.service import AuthService
        from ptracker.price_tracking.service import PriceTrackerService

        g.auth_service = AuthService()
        g.price_service = PriceTrackerService()
