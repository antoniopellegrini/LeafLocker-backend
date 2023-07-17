from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
    decode_token
)
from shared.common_resources import admin_required
from shared.blacklist import BLACKLIST
from models.user import UserModel
from marshmallow import fields, validate
from flask_marshmallow import Marshmallow
from shared.helpers import parse_json_body, validate_email_regex

ma = Marshmallow()

class RegisterSchema(ma.Schema):
    role = fields.String(required=True, validate=[validate.OneOf(UserModel.roles)])
    email = fields.String(required=True, validate=[validate.Email()])
    password = fields.String(required=True, validate=[validate.Length(min=2)])
    firstname = fields.String(required=True, validate=[
                              validate.Length(min=2)])
    lastname = fields.String(required=True, validate=[validate.Length(min=2)])
    phone = fields.Integer(required=False)


class Register(Resource):
    def post(self):
   
        register_schema = RegisterSchema()
        data = parse_json_body(register_schema,request)

        role = data.get('role')
        if role == 'operator' or role == 'admin':
            return {"type": "unauthorized", "message": "Unauthorized"}, 403

        if UserModel.find_by_email(data.get('email')):
            return {"type": "unauthorized", "message": "The email is alredy connected to an account"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return 200



class AdminRegister(Resource):
    @admin_required(acceptsAdminToken=True)
    def post(self):

        register_schema = RegisterSchema()
        data = parse_json_body(register_schema,request)

        if UserModel.find_by_email(data.get('email')):
            return {"type": "unauthorized", "message": "The email is alredy connected to an account"}, 400

        user = UserModel(**data)
        user.save_to_db()

        return 200


class LoginSchema(ma.Schema):
    email = fields.String(required=True, validate=[validate.Regexp(validate_email_regex,
                                                                   error="Email is not valid")])
    password = fields.String(required=True, validate=[validate.Length(min=2)])


class Login(Resource):
    def post(self):

        login_schema = LoginSchema()
        data = parse_json_body(login_schema,request)
        
        user = UserModel.find_by_email(data.get('email'))

        if user and user.verify_password(data.get('password')):
            claims = { 'role': user.role }

            refresh_token = create_refresh_token(
                user.id, additional_claims=claims)

            #add refresh_token jti into access_token, so at logout we can revoke the two tokens
            claims['rjti'] = decode_token(refresh_token)['jti']

            access_token = create_access_token(
                identity=user.id, fresh=True, additional_claims=claims)

            return {
                'id': user.id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'role': user.role
            }, 200

        return {"type": "invalid_credentials", "message": "Invalid Credentials!"}, 401


class Logout(Resource):
    @jwt_required(fresh=True)
    def post(self):
        jwt = get_jwt()
        jti = jwt['jti']
        rjti = jwt['rjti']
        if jti:
            BLACKLIST.add(jti)
            BLACKLIST.add(rjti)
            return 200
        else:
            return {"type": "identity_not_verified", "message": "Identity not verified"}, 401


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.

        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        _identity = get_jwt_identity()
        user = UserModel.find_by_id(_identity)
        if user:
            new_token = create_access_token(
                identity=user.id, fresh=False, additional_claims = { 'role' : user.role })
            return {'access_token': new_token}, 200 
        else:
            return {"type": "identity_not_verified", "message": "Identity not verified"}, 401
