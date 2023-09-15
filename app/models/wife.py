from app import db
from datetime import date
from sqlalchemy.sql import func

class Wife(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    id_number = db.Column(db.Integer, unique=True)
    child = db.relationship('Child', backref='wife')
    register_id = db.Column(db.Integer, db.ForeignKey('register.id'))