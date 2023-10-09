from app import db
from datetime import datetime, date
from sqlalchemy.sql import func
from app.models.cont_reg import event_reg

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    phone_num = db.Column(db.String(20))
    id_number = db.Column(db.Integer, unique=True)
    wife = db.relationship('Wife', backref='member')
    child = db.relationship('Child', backref='member')
    added_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    contribute = db.relationship('Contribution', backref='member')

    def __repr__(self):
        return f'<Member {self.firstname}>'