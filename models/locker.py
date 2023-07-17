from config.db import db
import uuid


class LockerModel(db.Model):
    __tablename__ = 'locker'

    id = db.Column(db.String(36), primary_key=True, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    location = db.Column(db.String(36))
    ownership = db.Column(db.String(100))
    cells = db.relationship('CellModel')
    user = db.relationship('UserModel', back_populates="locker")

    ownerships = ["public", "private"]

    def __init__(self, location, user_id, ownership="public"):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.location = location
        self.ownership = ownership

    def json(self):
        return {
            'id': self.id,
            'location': self.location,
            'user_id': self.user_id,
            'ownership': self.ownership,
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
    def find_all_by_user_id(cls, _user_id):
        return cls.query.filter_by(user_id=_user_id).all()

    @classmethod
    def find_all(cls):
        return cls.query.all()
