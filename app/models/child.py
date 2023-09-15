from app import db
from datetime import date
from sqlalchemy.sql import func
# from app.models.deposit import Deposit

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
    family_id = db.Column(db.Integer, db.ForeignKey('wife.id'))
    register_id = db.Column(db.Integer, db.ForeignKey('register.id'))

    def __repr__(self):
        return f'<Member {self.firstname}>'