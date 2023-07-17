from config.db import db


class RentModel(db.Model):
    __tablename__ = 'rent'

    cell_id = db.Column(db.String(36), db.ForeignKey(
        'cell.id'), primary_key=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey(
        'user.id'), primary_key=True, nullable=False)
    leaf_cell_token = db.Column(db.String(20), nullable=False)
    start = db.Column(db.String(36))
    end = db.Column(db.String(36))
    user = db.relationship('UserModel', back_populates="rent")
    cell = db.relationship('CellModel', back_populates="rent")

    def __init__(self, user_id, cell_id, leaf_cell_token, start = None, end = None):
        self.user_id = user_id
        self.cell_id = cell_id
        self.leaf_cell_token = leaf_cell_token
        self.start = start
        self.end = end

    def json(self):
        return {
            'user_id': self.user_id,
            'cell_id': self.cell_id,
            'leaf_cell_token': self.leaf_cell_token,
            'start': self.start,
            'end': self.end,
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
    def find_by_user_id(cls, _id):
        return cls.query.filter_by(user_id=_id).all()
    
    @classmethod
    def find_by_cell_id(cls, _cell_id):
        return cls.query.filter_by(cell_id=_cell_id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_all_user_id(cls, _id):
        return cls.query.filter_by(user_id=_id).all()
