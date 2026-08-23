from app import create_app, db
from app.user import User
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Get current max id
    result = db.session.execute(text("SELECT MAX(id) FROM \"user\""))
    max_id = result.scalar()
    print(f"Current max user id: {max_id}")

    # Reset sequence
    if max_id is not None:
        db.session.execute(text(f"SELECT setval(pg_get_serial_sequence('user', 'id'), :new_id)"), {"new_id": max_id + 1})
        db.session.commit()
        print(f"Sequence reset to {max_id + 1}")
    else:
        print("No users found, sequence unchanged")
