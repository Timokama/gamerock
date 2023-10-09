from app import db

event_reg = db.Table('event_reg',
        db.Column('membeber', db.Integer, db.ForeignKey('member.id')),
        db.Column('community_event', db.Integer, db.ForeignKey('community_event.id'))
    )