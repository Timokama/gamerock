from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    contact = db.Column(db.String(20))
    contribute = db.relationship('Contribute', backref='user')
    family = db.relationship('Register', backref='user')
    image = db.relationship('Images', backref='user')

    @property
    def passwords(self):
        raise AttributeError('passwordis not a readable attribute!')
    
    @passwords.setter
    def passwords(self, password):
        self.password = generate_password_hash(password)

    def verify_passwords(self, password):
        return check_password_hash(self.password, password)

