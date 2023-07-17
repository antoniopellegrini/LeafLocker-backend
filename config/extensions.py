
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config.exceptions import ValidationException
from shared.blacklist import BLACKLIST

class HttpExceptionHandler:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        @app.errorhandler(404)
        def page_not_found(e):
            return ({"type": "page_not_found","message": "Endpoint doesn't exist"},
                    e.code) 

        @app.errorhandler(ValidationException)
        def handle_validation_exception(exception):
            if exception.errors:
                return ({ "type": "validation_exception","message": exception.message, "errors":exception.errors},
                    exception.code)
            else:
                return  ({"type": "validation_exception","message": exception.message},
                    exception.code) 
            

cors = CORS()
jwt = JWTManager()
migrate = Migrate()
http_exception_handler = HttpExceptionHandler()



"""
`claims` are data we choose to attach to each jwt payload
and for each jwt protected endpoint, we can retrieve these claims via `get_jwt_claims()`
one possible use case for claims are access level control, which is shown below.
"""

# This method will check if a token is blacklisted, and will be called automatically when blacklist is enabled


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    # Here we blacklist particular JWTs that have been created in the past.
    return jwt_payload["jti"] in BLACKLIST


# The following callbacks are used for customizing jwt response/error messages.
# The original ones may not be in a very pretty format (opinionated)
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    return jsonify({
        'message': 'The token has expired.',
        'type': 'token_expired'
    }), 401 if jwt_data['type'] == 'access' else 403  # returns 401 when access_token is expired, 403 when refresh_token is expired


@jwt.invalid_token_loader
# we have to keep the argument here, since it's passed in by the caller internally
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'type': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'type': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback(jwt_header, jwt_payload):
    return jsonify({
        "description": "The token is not fresh.",
        'type': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return jsonify({
        "description": "The token has been revoked.",
        'type': 'token_revoked'
    }), 401

