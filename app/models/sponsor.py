from app import db
from sqlalchemy.sql import func

class Sponsor(db.Model):
    __tablename__ = 'sponsor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    sponsorship_type = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Integer, nullable=True, default=0)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Active')
    notes = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = db.relationship('User', foreign_keys=[created_by], backref='created_sponsors')
    items = db.relationship('SponsorItem', backref='sponsor', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Sponsor {self.name}>'

class SponsorItem(db.Model):
    __tablename__ = 'sponsor_item'
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    item_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Integer, nullable=True, default=0)
    total_price = db.Column(db.Integer, nullable=True, default=0)
    item_type = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<SponsorItem {self.item_name}>'
