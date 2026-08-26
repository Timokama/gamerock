from app import db
from sqlalchemy.sql import func

class TreasurerRecord(db.Model):
    __tablename__ = 'treasurer_record'
    id = db.Column(db.Integer, primary_key=True)
    record_type = db.Column(db.String(20), nullable=False, default='Transaction')
    amount = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    transaction_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = db.relationship('User', backref='treasurer_records')

    def __repr__(self):
        return f'<TreasurerRecord {self.record_type} {self.amount} ({self.transaction_date})>'
