from app import db
from datetime import datetime, date
from sqlalchemy.sql import func
from app.models.cont_depo import cont_reg

class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(10))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    id_number = db.Column(db.Integer, unique=True)
    wife = db.relationship('Wife', backref='register')
    child = db.relationship('Child', backref='child')
    depo_id = db.relationship('Deposit', backref='register')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    contribute = db.relationship('Contribute', secondary=cont_reg, backref='register') 
    def __repr__(self):
        return f'<Member {self.firstname}>'