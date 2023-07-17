from config.db import db
from passlib.hash import bcrypt
import uuid


class UserModel(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.String(36), primary_key=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(320), nullable=False)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    phone = db.Column(db.String(15))

    locker = db.relationship(
        "LockerModel", uselist=False, back_populates="user")
    rent = db.relationship("RentModel", back_populates="user")

    roles = ["admin", "user", "operator"]

    def __init__(self, password, role, firstname, lastname, email="", phone=""):
        self.password = bcrypt.hash(password)
        self.role = role
        self.firstname = firstname
        self.lastname = lastname
        self.phone = phone
        self.email = email
        self.id = str(uuid.uuid4())

    def json(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'phone': self.phone,
            'email': self.email,
            'role': self.role,
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def edit_param(self, params):
        try:
            for couple in params:
                for key in couple:
                    value = couple[key]
                    if key == "password":
                        value = bcrypt.hash(value)

                    self.query.filter_by(id=self.id).update({key: value})

        except Exception as e:
            print("Exception:", e)
        db.session.commit()

    def verify_password(self, password):
        return bcrypt.verify(password, self.password)

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_email(cls, _email):
        return cls.query.filter_by(email=_email).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()
