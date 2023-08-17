from app import db

cont_depo = db.Table('cont_reg',
                    db.Column('reg_id', db.Integer, db.ForeignKey('register.id')),
                    db.Column('cont_id', db.Integer, db.ForeignKey('contribute.id'))
                    )