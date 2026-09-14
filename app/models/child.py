from app import db
from datetime import date
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property


class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    phone_num = db.Column(db.String(20))
    id_number = db.Column(db.Integer)
    email = db.Column(db.String(120))
    date_of_birth = db.Column(db.Date)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    spouse_id = db.Column(db.Integer, db.ForeignKey('spouse.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    @hybrid_property
    def display_email(self):
        if self.email:
            return self.email
        if self.user_account:
            return self.user_account.email
        return ''

    def __repr__(self):
        return f'<Member {self.firstname}>'