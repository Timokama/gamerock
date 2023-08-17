from app import db

cont_depo = db.Table('cont_depo',
                    db.Column('depo_id', db.Integer, db.ForeignKey('deposit.id')),
                    db.Column('cont_id', db.Integer, db.ForeignKey('contribute.id'))
                    )

cont_reg = db.Table('cont_reg',
                    db.Column('reg_id', db.Integer, db.ForeignKey('register.id')),
                    db.Column('cont_id', db.Integer, db.ForeignKey('contribute.id'))
                    )