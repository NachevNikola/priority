from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException
from flask import Blueprint, jsonify, current_app

errors = Blueprint("errors", __name__)

def error_response(status_code, description=None):
    payload = {
        'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error'),
        'status': status_code,
    }
    if description:
        payload['description'] = description
    return jsonify(payload), status_code

def bad_request(message):
    return error_response(400, message)

@errors.app_errorhandler(HTTPException)
def handle_exception(e):
    current_app.logger.info(e)
    return error_response(e.code, description=e.description)
