from config.db import db
import uuid


class SeedModel(db.Model):
    __tablename__ = 'seed'

    id = db.Column(db.String(36), primary_key=True, nullable=False, )
    name = db.Column(db.String(36))
    cell_dimension = db.Column(db.String(16))
    esimated_growth_time = db.Column(db.Integer)
    cells = db.relationship("CellModel", back_populates="seed")

    cell_dimensions = ['small', 'large']

    def __init__(self, name, cell_dimension, esimated_growth_time):
        self.id = str(uuid.uuid4())
        self.name = name
        self.cell_dimension = cell_dimension
        self.esimated_growth_time = esimated_growth_time

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'cell_dimension': self.cell_dimension,
            'esimated_growth_time': self.esimated_growth_time,
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def edit_param(self, params):
        try:
            for couple in params:
                for key in couple:
                    value = couple[key]
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

    @classmethod
    def find_all_size(cls, dimension):
        return cls.query.filter_by(cell_dimension=dimension).all()
