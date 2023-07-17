from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
    get_jwt,
)
from shared.common_resources import admin_required
from models.cell import CellModel
from models.locker import LockerModel
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, pre_load, validate
from shared.helpers import parse_json_body, parse_query_params, validate_email_regex
from models.rent import RentModel
from models.user import UserModel
ma = Marshmallow()


class LockerSchema(ma.Schema):
    user_id = fields.String(required=False)
    location = fields.String(required=True)
    ownership = fields.String(required=True,validate=[validate.OneOf(LockerModel.ownerships)])

class LockerSchemaPut(ma.Schema):
    user_id = fields.String(required=False)
    location = fields.String(required=False)
    ownership = fields.String(required=False,validate=[validate.OneOf(LockerModel.ownerships)])

class CreateLocker(Resource):
    @admin_required()
    def post(self):
        data = parse_json_body(LockerSchema(), request)

        if data.get('user_id'):
            if UserModel.find_by_id(data.get('user_id')) == None:
                return {"error": "user_not_found", "message": "User not found!"}, 404
       
        locker = LockerModel(**data)
        locker.save_to_db()
        return locker.json(), 200


class Locker(Resource):
    @admin_required()
    def put(self,id):
        locker = LockerModel.find_by_id(id)
       
        if locker:
            data = parse_json_body(LockerSchemaPut(), request)
            for key in data:
                locker.edit_param([{key: data[key]}])
            return locker.json(), 200
        else:
            return {"error": "not_found", "message": "Locker not found!"}, 404
        
    @admin_required()   
    def delete(self,id):
        locker = LockerModel.find_by_id(id)
       
        if locker:
            locker.delete_from_db()
            return 200
        else:
            return {"error": "not_found", "message": "Locker not found!"}, 404


class LockersSchema(ma.Schema):
    free = fields.Bool(required=False)

class Lockers(Resource):
    @jwt_required()
    def get(self):
    
        data = parse_query_params(LockersSchema(),request)
        if data.get('free'):
            free_lockers = []
            lockers = LockerModel.find_all()
            rented_cells = [r.cell for r in RentModel.find_all()]

            for locker in lockers:
                n_of_free_cells = 0
                for cell in locker.cells:
                    if cell not in rented_cells:
                        n_of_free_cells += 1

                if n_of_free_cells > 0:
                    free_lockers.append(
                        {'locker': locker.json(), 'n_free_cells': n_of_free_cells})

            return free_lockers, 200

        return  [x.json() for x in LockerModel.find_all()], 200


class LockerCellsSchema(ma.Schema):
    free = fields.Boolean(required=False)


class LockerCells(Resource):
    @jwt_required()
    def get(self,id_locker):

        locker = LockerModel.find_by_id(id_locker)

        if locker:
            data = parse_query_params(LockerCellsSchema(),request)
            if data.get('free'):
                rented_cells = [r.cell for r in RentModel.find_all()]
                free_cells = []

                for cell in locker.cells:
                    if cell not in rented_cells:
                        free_cells.append(cell.json())

                return free_cells, 200
            
            else:
                return [x.json() for x in locker.cells], 200
        
        return {"error": "not_found", "message": "Locker not found!"}, 404
    
class LockerCellSchema(ma.Schema):
    dimension = fields.String(required=True,validate=[validate.OneOf(CellModel.dimensions)])
    numeric_id = fields.Integer(required=True)
    leaf_device_id = fields.String(required=True, allow_none=True)
    seed_id = fields.String(required=False, allow_none=True)
    status = fields.String(required=False,validate=[validate.OneOf(CellModel.statuses)])

class CreateLockerCell(Resource):
    @admin_required()
    def post(self,id_locker):

        locker = LockerModel.find_by_id(id_locker)

        if locker:
            data = parse_json_body(LockerCellSchema(),request)
            #check if numeric iD exists
            cell = CellModel(id_locker, data.get('dimension'),data.get('numeric_id'), data.get('leaf_device_id'))
            cell.save_to_db()
            return cell.json(), 200
    
        return {"error": "not_found", "message": "Locker not found!"}, 404
    

class LockerCell(Resource):
    @admin_required()
    def delete(self,id_locker,id_cell):
        locker = LockerModel.find_by_id(id_locker)

        if locker:
            cell = CellModel.find_by_id(id_cell)
            if cell:
                cell.delete_from_db()
                return 200

            return {"error": "not_found", "message": "Locker not found!"}, 404
        
        return {"error": "not_found", "message": "Locker not found!"}, 404

    @admin_required()
    def put(self,id_locker,id_cell):
        locker = LockerModel.find_by_id(id_locker)

        if locker:
            cell = CellModel.find_by_id(id_cell)
           

            if cell:      
                data = parse_json_body(LockerCellSchema(),request)         
                cell.edit_params(data)
                return cell.json(), 200

            return {"error": "not_found", "message": "Cell not found!"}, 404
        
        return {"error": "not_found", "message": "Locker not found!"}, 404
    
    @admin_required()
    def get(self,id_locker,id_cell):
        locker = LockerModel.find_by_id(id_locker)

        if locker:
            cell = CellModel.find_by_id(id_cell)
            if cell:
                
                return cell.json(), 200

            return {"error": "not_found", "message": "Cell not found!"}, 404
        
        return {"error": "not_found", "message": "Locker not found!"}, 404