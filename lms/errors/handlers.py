from flask import render_template
from flask_wtf.csrf import CSRFError
from lms import db


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_error(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        try:
            db.session.rollback()
        except:
            pass
        return render_template("errors/500.html"), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template("errors/csrf_error.html", reason=e.description), 400
