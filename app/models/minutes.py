from app import db
from sqlalchemy.sql import func

class Minutes(db.Model):
    __tablename__ = 'minutes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    meeting_type = db.Column(db.String(50), nullable=False, default='General')
    meeting_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(150), nullable=True)
    agenda = db.Column(db.Text, nullable=True)
    discussion = db.Column(db.Text, nullable=True)
    decisions = db.Column(db.Text, nullable=True)
    action_items = db.Column(db.Text, nullable=True)
    next_meeting_date = db.Column(db.Date, nullable=True)
    attendees = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Draft')
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    creator = db.relationship('User', foreign_keys=[created_by], backref='created_minutes')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_minutes')

    def __repr__(self):
        return f'<Minutes {self.title} ({self.meeting_date})>'
