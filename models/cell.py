from config.db import db
import uuid

class CellModel(db.Model):
    __tablename__ = 'cell'

    id = db.Column(db.String(36), primary_key=True, nullable=False)
    numeric_id = db.Column(db.Integer, nullable=False)
    locker_id = db.Column(db.String(36), db.ForeignKey('locker.id'))
    dimension = db.Column(db.String(16))
    seed_id = db.Column(db.String(36), db.ForeignKey('seed.id'))
    status = db.Column(db.String(16))
    leaf_device_id = db.Column(db.String(36))
    rent = db.relationship("RentModel", back_populates="cell")
    seed = db.relationship("SeedModel")
    dimensions = ['small','large']
    statuses = ['empty', 'in_use']

    def __init__(self, locker_id, dimension, numeric_id, leaf_device_id = None, seed_id=None, status = 'empty'):
        self.id = str(uuid.uuid4())
        self.numeric_id = numeric_id
        self.locker_id = locker_id
        self.dimension = dimension
        self.status = status
        self.seed_id = seed_id
        self.leaf_device_id = leaf_device_id

    def json(self):
        return {
            'id': self.id,
            'numeric_id': self.numeric_id,
            'locker_id': self.locker_id,
            'seed_id': self.seed_id,
            'status': self.status,
            'dimension': self.dimension,
            'leaf_device_id': self.leaf_device_id
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def edit_param(self, param):
        try:
            for couple in param:
                for key in couple:
                    value = couple[key]
                    self.query.filter_by(id=self.id).update({key: value})

        except Exception as e:
            print("Exception:", e)
        db.session.commit()

    def edit_params(self, params):
        try:
            for key in params:
                value = params[key]
                self.query.filter_by(id=self.id).update({key: value})

        except Exception as e:
            print("Exception:", e)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()
