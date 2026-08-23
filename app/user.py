from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .level import AccessLevel

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    surname = db.Column(db.String(1000))
    first_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(500))
    phone_num = db.Column(db.String(20))
    role = db.Column(db.Enum(AccessLevel))

    event = db.relationship('CommunityEvent', backref='user')
    contribution = db.relationship('Contribution', backref='user')
    family = db.relationship('Member', backref='user', foreign_keys='Member.added_by')
    member_profile = db.relationship('Member', backref='user_account', uselist=False, foreign_keys='Member.user_id')
    image = db.relationship('Images', backref='user')

    def is_active(self):
        return True
    @property
    def passwords(self):
        raise AttributeError('passwordis not a readable attribute!')
    
    @passwords.setter
    def passwords(self, password):
        self.password = generate_password_hash(password)

    def verify_passwords(self, password):
        return check_password_hash(self.password, password)

