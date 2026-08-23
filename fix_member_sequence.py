from app import create_app, db
from app.models.register import Member
from sqlalchemy import text

app = create_app()
with app.app_context():
    with db.session.begin():
        max_id = db.session.query(db.func.max(Member.id)).scalar()
        print('Current max member ID:', max_id)
        seq_name = db.session.execute(text("SELECT pg_get_serial_sequence('member', 'id')")).scalar()
        print('Sequence name:', seq_name)
        db.session.execute(text('SELECT setval(:seq, :max_id, false)'), {'seq': seq_name, 'max_id': max_id + 1})
        db.session.commit()
        print('Sequence reset to:', max_id + 1)
