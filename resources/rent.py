from models.rent import RentModel
from shared.common_resources import admin_required
from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
)
from flask_marshmallow import Marshmallow
from marshmallow import fields
ma = Marshmallow()


class RentSchema(ma.Schema):
    user_id = fields.String(required=True)
    cell_id = fields.String(required=True)
    start = fields.String(required=True)
    end = fields.String(required=True)
    leaf_cell_token = fields.String(required=True)


class Rent(Resource):
    @jwt_required()
    def post(self):
        data = RentSchema().load(request.args)
        rent = RentModel(**data)
        rent.save_to_db()
        return rent.json(), 200


class RentsSchema(ma.Schema):
    user_id = fields.String(required=True)


class Rents(Resource):
    @admin_required()
    def get(self):
        rents = RentModel.find_all()
        return  [x.json() for x in rents], 200
    # @jwt_required()
    # def get(self):
    #     data = RentsSchema().load(request.args)
    #     rents = RentModel.find_all_user_id(data['user_id'])

    #     for rent in rents:
    #         print(rent.cell.numeric_id)
    #     return {"rents": [x.json() for x in rents]}, 200
