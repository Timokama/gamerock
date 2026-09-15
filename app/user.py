from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import func
from . import db
from .level import AccessLevel

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(1000))
    first_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(500))
    phone_num = db.Column(db.String(20))
    id_number = db.Column(db.Integer, unique=True, nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    role = db.Column(db.Enum(AccessLevel, values_callable=lambda e: [m.value for m in e]))
    status = db.Column(db.String(20), nullable=False, default='pending')
    bookmarks = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    event = db.relationship('CommunityEvent', backref='user')
    contribution = db.relationship('Contribution', backref='user')
    family = db.relationship('Member', backref='user', foreign_keys='Member.added_by')
    member_profile = db.relationship('Member', backref='user_account', uselist=False, foreign_keys='Member.user_id')
    image = db.relationship('Images', backref='user')
    spouse = db.relationship('Spouse', backref='user_account', uselist=False)
    child = db.relationship('Child', backref='user_account', uselist=False)

    def is_active(self):
        return self.status == 'active'
    @property
    def passwords(self):
        raise AttributeError('password is not a readable attribute!')
    
    @passwords.setter
    def passwords(self, password):
        self.password = generate_password_hash(password)

    def verify_passwords(self, password):
        return check_password_hash(self.password, password)

