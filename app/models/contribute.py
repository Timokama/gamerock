from app import db
from sqlalchemy.sql import func
from app.models.payments import Payment

class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    trans_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    payment_type = db.Column(db.Enum(Payment))
    transaction_ref = db.Column(db.String(50))
    member_id = db.Column(db.Integer,db.ForeignKey('member.id'))
    propose = db.Column(db.Integer, db.ForeignKey('community_event.id'))
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<"{self.member_id}">' 