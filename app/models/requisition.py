from app import db
from sqlalchemy.sql import func

class Requisition(db.Model):
    __tablename__ = 'requisition'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    date_taken = db.Column(db.Date, nullable=False)
    expected_return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    member = db.relationship('Member', backref='requisitions')
    creator = db.relationship('User', backref='created_requisitions')
    items = db.relationship('RequisitionItem', backref='requisition', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self):
        return f'<Requisition {self.item_name} x{self.quantity} ({self.status})>'


class RequisitionItem(db.Model):
    __tablename__ = 'requisition_item'
    id = db.Column(db.Integer, primary_key=True)
    requisition_id = db.Column(db.Integer, db.ForeignKey('requisition.id'), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    def __repr__(self):
        return f'<RequisitionItem {self.item_name} x{self.quantity}>'
