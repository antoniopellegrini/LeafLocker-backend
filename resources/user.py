from flask import request
import json
from flask_restful import Resource
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt,
)
from resources.seed import SeedSchema
from shared.common_resources import admin_required
from models.locker import LockerModel
from models.rent import RentModel
from models.user import UserModel
from marshmallow import fields
from flask_marshmallow import Marshmallow

from resources.rent import RentSchema
ma = Marshmallow()

class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    @jwt_required(refresh=False)
    def get(self):
        data = request.args
        claim_list = get_jwt()
        if not claim_list['is_admin']:
            return {"error":"unhautorized", "message":"No privileges"}, 403
        user = UserModel.find_by_id(data.get('id'))
        if not user:
            return {"error": "user_not_found", "message": "User not found!"}, 404
        return user.json(), 200

    @jwt_required()
    def get(self):
        identity = get_jwt_identity()
        utente = UserModel.find_by_id(identity)
        if utente:
            return utente.json(), 200
        else:
            return {"error": "user_not_found", "message": "User not found!"}, 404

    @admin_required()
    def delete(self):
        data = request.args
        utente = UserModel.find_by_id(data.get('id'))
        if not utente:
            return {"error": "user_not_found", "message": "User not found!"}, 404
        else:
            utente.delete_from_db()
            return 200

    @admin_required()
    def patch(self):
        try:
            args = request.get_json()
            data = json.loads(args['data'])
            user = UserModel.find_by_id(id)
            if user:
                for key in data:
                    user.edit_param([{key: data[key]}])
                return 200
            else:
                return {"error": "not_found", "message": "User not found!"}, 404
        except Exception as e:
            return {'message': f"[Exception] Errore modifica utente: {e}"}, 402


class Users(Resource):
    @admin_required()
    def get(self):
        return [x.json() for x in UserModel.find_all()], 200


''' TODO: maybe delete this. This endpoint return user owned identity lockers'''
class UserLockers(Resource):
    @jwt_required()
    def get(self):
        id = get_jwt_identity()

        lockers = LockerModel.find_all_by_user_id(id)
        return [x.json() for x in lockers], 200


class LockersWithRentedCellsSchema(ma.Schema):
    id = fields.Str()
    location = fields.Str()
    user_id = fields.Str()
    ownership = fields.Str()
    cells = fields.Nested('RentedCellSchema',many=True)

class RentedCellSchema(ma.Schema):
    id = fields.Str()
    numeric_id = fields.Str()
    locker_id = fields.Str()
    seed_id = fields.Str()
    status = fields.Str()
    dimension = fields.Str()
    leaf_device_id = fields.Str()
    rent = fields.Nested(RentSchema(only=("start","end"),many=True))
    seed = fields.Nested(SeedSchema(),)

class UserRentedCells(Resource):
    @jwt_required()
    def get(self):
        id = get_jwt_identity()

        lock = LockerModel.find_all_by_user_id(id)
        if not lock:
            return [],200
        
        rents = RentModel.find_by_user_id(id)

        filtered_list = []
        if rents:
            rented_cells = [RentedCellSchema.dump(RentedCellSchema(), rent.cell) for rent in rents]
            lockers = [LockersWithRentedCellsSchema.dump(LockersWithRentedCellsSchema(), locker) for locker in LockerModel.find_all()]

            filtered_list = filter_cells(rented_cells, lockers)
            return filtered_list, 200
        return filtered_list, 200


def filter_cells(cell_list, dictionary_list):
    result = []
    cell_ids = [cell['id'] for cell in cell_list]
    
    for dictionary in dictionary_list:
        filtered_cells = [cell for cell in dictionary['cells'] if cell['id'] in cell_ids]
        if filtered_cells:
            dictionary['cells'] = filtered_cells
            result.append(dictionary)
    return result    
    
def debugList(message, list):
    print(message)
    for item in list:
        print(item)

def remove_cell(list,locker,cell):
    for lock in list:
        if lock is locker:
            for cel in lock.cells:
                if cel is cell:
                    lock.cells.remove(cel)