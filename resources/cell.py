from flask import request
import requests
from shared.common_resources import admin_required
from flask_restful import Resource
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from shared.helpers import parse_json_body
from models.cell import CellModel
from models.rent import RentModel
from flask_marshmallow import Marshmallow
from marshmallow import fields
from models.seed import SeedModel
from resources.rent import RentSchema
from resources.seed import SeedSchema
ma = Marshmallow()

class Cells(Resource):
    @admin_required()
    def get(self):
        return [cell.json() for cell in CellModel.find_all()],200


class CellSeeds(Resource):
    @jwt_required()
    def get(self,id_cell):
    
        cell = CellModel.find_by_id(id_cell)
        if cell:
            seeds = SeedModel.find_all_size(cell.dimension)
            return [seed.json() for seed in seeds], 200
            
        return {"type": "not_found", "message": "Cell not found!"}, 404



class CellOpen(Resource):
    @jwt_required()
    def post(self,id_cell):
    
        cell = CellModel.find_by_id(id_cell)
        if not cell:
            return {"type": "not_found", "message": "Cell not found!"}, 404
        
        rent = RentModel.find_by_cell_id(id_cell)

        if rent.cell_id == id_cell and rent.user_id == get_jwt_identity():
            #send fake request to locker server to unlock the cell
            return 200
        return  {"type":"unhautorized", "message":"Can't unlock this cell"}, 403
      


class CellRentSchema(ma.Schema):
    start = fields.String(required=True)
    days = fields.String(required=True)   
        
class CellRent(Resource):
    @jwt_required()
    def post(self,id_cell):
     
        cell = CellModel.find_by_id(id_cell)
        if cell:
            #check if cell not rented
            if not RentModel.find_by_cell_id(id_cell):

                user_id = get_jwt_identity()
                data = parse_json_body(CellRentSchema(),request)

                #calculate end timestamp
                #end = int(data['start']) + int(data['days'])*86400000
                #send request to leaf that returns the access_token
                leaf_cell_token = requests.post(url=f'http://localhost:5001/cell/{id_cell}/rent')
                print("response",leaf_cell_token.content)

                rent = RentModel(user_id=user_id, cell_id=id_cell, leaf_cell_token=leaf_cell_token.text, start=data['start'])
                rent.save_to_db()

                return rent.json(), 200
            else:
                return {"type": "cant_rent", "message": "Can't rent this cell"}, 400
                
        return {"type": "not_found", "message": "Cell not found!"}, 404


        
class CellStopRent(Resource):
    @jwt_required()
    def post(self,id_cell):
     
        cell = CellModel.find_by_id(id_cell)
        if not cell:
            return {"type": "not_found", "message": "Cell not found!"}, 404
        
        rent = RentModel.find_by_cell_id(id_cell)

        if not rent or  rent.user_id != get_jwt_identity():
            return  {"type":"unhautorized", "message":"Can't access this cell!"}, 403
 
        rent.delete_from_db()

        return 200

class CellStartCultivationSchema(ma.Schema):
    seed_id = fields.String(required=True)

class CellStartCultivation(Resource):
    @jwt_required()
    def post(self,id_cell):
        data = parse_json_body(CellStartCultivationSchema(),request)
        
        seed = SeedModel.find_by_id(data.get('seed_id'))
        if not seed:
            return {"type": "not_found", "message": "Cell not found!"}, 404

        cell = CellModel.find_by_id(id_cell)
        if not cell:
            return {"type": "not_found", "message": "Cell not found!"}, 404
        
        rent = RentModel.find_by_cell_id(id_cell)
        if not rent:
            return  {"type":"unhautorized", "message":"Can't access this cell!"}, 403


        if rent.cell_id == id_cell and rent.user_id == get_jwt_identity():  
            if cell.status != 'in_use':
                cell.edit_param([{'status': 'in_use', 'seed_id':seed.id}])
                #send fake request to LEAF to activate

                cell_dump = CellSchema().dump(cell)
            

                return cell_dump, 200
            else:
                return {"type":"bad_request", "message":"Cell cultivation alredy started!"},400  
        return  {"type":"unhautorized", "message":"Can't access this cell!"}, 403
        
    
class CellEndCultivation(Resource):
    @jwt_required()
    def post(self,id_cell):
        cell = CellModel.find_by_id(id_cell)
        if cell:
            rent = RentModel.find_by_cell_id(id_cell)
            if rent.cell_id == id_cell and rent.user_id == get_jwt_identity():
                        
                if cell.status != 'empty':
                    cell.edit_param([{'status': 'empty'}])
                    return 200
                else:
                    return {"type":"bad_request", "message":"Cell cultivation alredy ended!"},400

            return  {"type":"unhautorized", "message":"Can't access this cell!"}, 403
        return {"type": "not_found", "message": "Cell not found!"}, 404

class CellSchema(ma.Schema):
    id = fields.String()
    numeric_id = fields.String()  
    locker_id= fields.String()  
    dimension = fields.String()
    leaf_device_id = fields.String()
    seed_id = fields.String()
    status = fields.String()
    rent = fields.Nested(RentSchema(only=("start","end","leaf_cell_token"),many=True))
    seed = fields.Nested(SeedSchema(),)
    #locker = fields.Nested(LockerSchema(only=("location",)))

class CellInfo(Resource):
    @jwt_required()
    def get(self,id_cell):

        cell = CellModel.find_by_id(id_cell)
        if not cell:
            return {"type": "not_found", "message": "Cell not found!"}, 404

        rent = RentModel.find_by_cell_id(id_cell)
        if not rent:
            return  {"type":"unhautorized", "message":"Can't access this cell!"}, 403

        if rent.cell_id == id_cell and rent.user_id == get_jwt_identity():
            
            # if rent.end:
            #     if int(rent.end) <  milliseconds_since_epoch():
            #         rent.delete_from_db()
            #         return  {"type":"unhautorized", "message":"Can't access this cell!"}, 403

            cell_dump = CellSchema().dump(cell)
            seeds = SeedModel.find_all_size(cell.dimension)

            return {'cell':cell_dump, 'seeds':[seed.json() for seed in seeds]},200

        return {"type":"unhautorized", "message":"Can't access this cell!"}, 403
    
