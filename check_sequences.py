from app import create_app
from sqlalchemy import text

app = create_app()
with app.app_context():
    from app import db
    tables = ['member', '"user"', 'spouse', 'child', 'contribution', 'community_event']
    for table in tables:
        try:
            seq = db.session.execute(text(f"SELECT pg_get_serial_sequence('{table}', 'id')")).scalar()
            if seq:
                curr = db.session.execute(text(f'SELECT last_value FROM {seq}')).scalar()
                max_id = db.session.execute(text(f'SELECT MAX(id) FROM {table}')).scalar()
                print(f'{table}: seq={curr}, max={max_id}')
            else:
                print(f'{table}: no sequence')
        except Exception as e:
            print(f'{table}: error - {e}')
