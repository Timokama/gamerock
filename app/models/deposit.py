from app import db
from sqlalchemy.sql import func
from app.models.cont_depo import cont_depo

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    reg_id = db.Column(db.Integer, db.ForeignKey('register.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    contribute = db.relationship('Contribute',  secondary=cont_depo, backref='deposit')

    def __repr__(self):
        return f'<Amount {self.amount} >'