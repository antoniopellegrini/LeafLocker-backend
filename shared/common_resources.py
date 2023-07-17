from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
import os

unauthorized_error = {"type": "unauthorized", "message": "Unauthorized"}, 403


def admin_required(acceptsAdminToken=False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if acceptsAdminToken:
                verify_jwt_in_request(optional=True)
                if request.headers.get('admintoken') == os.environ.get("ADMIN_TOKEN"):
                    return fn(*args, **kwargs)
                else:
                    return unauthorized_error
            else:
                verify_jwt_in_request(fresh=True)
                claims = get_jwt()
                if 'role' in claims:
                    if claims['role'] == 'admin':
                        return fn(*args, **kwargs)
                return unauthorized_error

        return decorator
    return wrapper


def permission_required(permissionList):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request(fresh=True)
            claims = get_jwt()
            if 'role' in claims:
                for permission in permissionList:
                    if permission == claims['role']:
                        return fn(*args, **kwargs)
            return unauthorized_error
        return decorator
    return wrapper
