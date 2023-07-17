from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required,
)
from shared.helpers import parse_json_body
from shared.common_resources import admin_required
from models.seed import SeedModel
from flask_marshmallow import Marshmallow
from marshmallow import fields
ma = Marshmallow()


class SeedSchema(ma.Schema):
    name = fields.String(required=True)
    cell_dimension = fields.String(required=True)
    esimated_growth_time = fields.Integer(required=True)


class Seed(Resource):
    @admin_required()
    def post(self):
        data = parse_json_body(SeedSchema(),request)
        seed = SeedModel(**data)
        seed.save_to_db()
        return seed.json(), 200
    
    @admin_required()
    def delete(self,id):
        seed = SeedModel.find_by_id(id)
       
        if not seed:
            return {"error": "not_found", "message": "Seed not found!"}, 404

        seed.remove_from_db()
        return 200
    

class Seeds(Resource):
    @jwt_required()
    def get(self):
        return [x.json() for x in SeedModel.find_all()], 200