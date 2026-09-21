#!/usr/bin/env python
"""
Admin Bootstrap Script
Creates initial admin/developer user for the application.
Run once after database initialization: python scripts/create_admin.py
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.user import User
from app.level import AccessLevel
from werkzeug.security import generate_password_hash


def create_admin():
    """Create or update admin user."""
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(role=AccessLevel.ADMIN).first()
        dev = User.query.filter_by(role=AccessLevel.DEVEL).first()
        
        if admin:
            print(f"Admin user already exists: {admin.email}")
        else:
            # Get admin details from environment or prompt
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@gamerock.local')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'ChangeMe123!')
            admin_first = os.environ.get('ADMIN_FIRST_NAME', 'System')
            admin_surname = os.environ.get('ADMIN_SURNAME', 'Administrator')
            
            admin = User(
                surname=admin_surname,
                first_name=admin_first,
                email=admin_email,
                password=generate_password_hash(admin_password, method='pbkdf2:sha256'),
                role=AccessLevel.ADMIN,
                status='active',
                is_primary_account=True,
                family_relation_type='primary',
            )
            db.session.add(admin)
            print(f"Created admin user: {admin_email}")
        
        if dev:
            print(f"Developer user already exists: {dev.email}")
        else:
            dev_email = os.environ.get('DEVEL_EMAIL', 'dev@gamerock.local')
            dev_password = os.environ.get('DEVEL_PASSWORD', 'ChangeMe123!')
            dev_first = os.environ.get('DEVEL_FIRST_NAME', 'Developer')
            dev_surname = os.environ.get('DEVEL_SURNAME', 'System')
            
            dev = User(
                surname=dev_surname,
                first_name=dev_first,
                email=dev_email,
                password=generate_password_hash(dev_password, method='pbkdf2:sha256'),
                role=AccessLevel.DEVEL,
                status='active',
                is_primary_account=True,
                family_relation_type='primary',
            )
            db.session.add(dev)
            print(f"Created developer user: {dev_email}")
        
        db.session.commit()
        print("\n[OK] Admin bootstrap complete!")
        print("\n[!] IMPORTANT: Change default passwords immediately!")
        print("   Set ADMIN_PASSWORD and DEVEL_PASSWORD environment variables.")


if __name__ == '__main__':
    create_admin()