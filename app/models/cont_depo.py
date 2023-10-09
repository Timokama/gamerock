from app import db

cont_event = db.Table('cont_event',
                    db.Column('event_id', db.Integer, db.ForeignKey('community_event.id')),
                    db.Column('cont_id', db.Integer, db.ForeignKey('contribute.id'))
                    )