from flask_restful import Api
from resources.auth import Login, Logout, Register, AdminRegister, TokenRefresh
from resources.user import UserLockers, UserRentedCells, Users, User
from resources.root import Root
from resources.locker import CreateLocker, CreateLockerCell, Locker, LockerCell, LockerCells, Lockers
from resources.cell import CellEndCultivation, CellInfo, CellOpen, CellRent, CellSeeds, CellStartCultivation, CellStopRent, Cells
from resources.seed import Seed, Seeds
from resources.rent import Rent, Rents

api = Api()

api.add_resource(Root, '/')
api.add_resource(Register, '/register')
api.add_resource(AdminRegister, '/register/admin')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(User, '/user')
api.add_resource(Users, '/users')
api.add_resource(UserLockers,'/user/lockers')
api.add_resource(UserRentedCells,'/user/rentedLockersCells')

api.add_resource(Cells,'/cells')
api.add_resource(CellSeeds,'/cell/<string:id_cell>/seeds')
api.add_resource(CellInfo, '/cell/<string:id_cell>/info')
api.add_resource(CellRent, '/cell/<string:id_cell>/rent/start')
api.add_resource(CellStopRent, '/cell/<string:id_cell>/rent/stop')
api.add_resource(CellOpen,'/cell/<string:id_cell>/open')
api.add_resource(CellStartCultivation,'/cell/<string:id_cell>/cultivation/start')
api.add_resource(CellEndCultivation,'/cell/<string:id_cell>/cultivation/end')

api.add_resource(Lockers, '/lockers')
api.add_resource(LockerCells, '/locker/<string:id_locker>/cells')

api.add_resource(CreateLocker,'/locker')
api.add_resource(Locker,'/locker/<string:id>')

api.add_resource(CreateLockerCell, '/locker/<string:id_locker>/cell')
api.add_resource(LockerCell, '/locker/<string:id_locker>/cell/<string:id_cell>')

api.add_resource(Seed, '/seed','/seed/<string:id>')

api.add_resource(Seeds, '/seeds')

api.add_resource(Rent, '/rent')
api.add_resource(Rents, '/rents')