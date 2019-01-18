from app import app
from flask import render_template


class ResponseException(Exception):
    pass


class MissingValueException(ValueError):
    pass


class EventLocatorException(Exception):
    pass


@app.errorhandler(404)
def page_not_found(error):
    if error is None:
        error = "Page not found"
    return default_error_view(error), 404


@app.errorhandler(401)
def authentication_error(error):
    if error is None:
        error = "401 Unauthorised request"
    return default_error_view(error), 401


@app.errorhandler(500)
def internal_server_error(error):
    if error is None:
        error = "The server encountered an internal error."
    return default_error_view(error), 500


@app.errorhandler(MissingValueException)
def massing_value_handler(error):
    return default_error_view(error)


@app.errorhandler(ResponseException)
def response_exception_handler(code_message):
    return default_error_view(code_message)


@app.errorhandler(EventLocatorException)
def call_exception_handler(error):
    return default_error_view(error)


def default_error_view(error):
    return render_template("error_page.html", error=error)