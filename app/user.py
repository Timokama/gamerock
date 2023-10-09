from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .level import AccessLevel

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    surname = db.Column(db.String(1000))
    first_name = db.Column(db.String(100))
    password = db.Column(db.String(100))
    phone_num = db.Column(db.Integer)
    username = db.Column(db.String(100))
    role = db.Column(db.Enum(AccessLevel))

    event = db.relationship('CommunityEvent', backref='user')
    contribution = db.relationship('Contribution', backref='user')
    family = db.relationship('Member', backref='user')
    image = db.relationship('Images', backref='user')

    @property
    def passwords(self):
        raise AttributeError('passwordis not a readable attribute!')
    
    @passwords.setter
    def passwords(self, password):
        self.password = generate_password_hash(password)

    def verify_passwords(self, password):
        return check_password_hash(self.password, password)

