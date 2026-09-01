from app import db
from sqlalchemy.sql import func
# from app.models.cont_reg import event_reg
# from app.models.cont_depo import cont_event

class CommunityEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    details = db.Column(db.String(255), nullable=True)
    event_date = db.Column(db.Date, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    goal_amount = db.Column(db.Integer, nullable=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    update_by = db.Column(db.String(20), nullable=True)
    contribute = db.relationship('Contribution', backref='community_event')
    def __repr__(self):
        return f'<Name "{self.name}">'