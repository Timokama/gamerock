from app import db
from sqlalchemy.sql import func
# from app.models.cont_reg import event_reg
# from app.models.cont_depo import cont_event

class CommunityEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    details = db.Column(db.String(255))
    event_date = db.Column(db.Date)
    image = db.Column(db.String(255), nullable=True)
    # contribution_amt = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    update_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    update_by = db.Column(db.String(20))
    contribute = db.relationship('Contribution', backref='community_event')
    def __repr__(self):
        return f'<Name "{self.name}">'