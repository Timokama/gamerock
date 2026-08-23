"""
Import data from GM RCK CONT LIST 2026.xlsx into the welfare project database.
Simplified version without FlaskUI.
"""
import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.register import Member
from app.models.community_event import CommunityEvent
from app.models.contribute import Contribution
from app.models.payments import Payment
import re

def clean_phone(phone):
    """Clean phone number by removing non-digit characters."""
    if pd.isna(phone):
        return None
    phone = str(phone).strip()
    # Remove spaces, commas, etc.
    phone = re.sub(r'[^\d+]', '', phone)
    if phone.startswith('+'):
        phone = phone[1:]
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    return phone if phone else None

def clean_id_number(id_number):
    """Clean id_number by stripping whitespace and converting to int if valid."""
    if pd.isna(id_number):
        return None
    id_str = str(id_number).strip()
    if not id_str:
        return None
    try:
        return int(id_str)
    except (ValueError, TypeError):
        return None

def split_name(full_name):
    """Split full name into firstname, lastname, surname."""
    if pd.isna(full_name):
        return None, None, None
    full_name = str(full_name).strip()
    parts = full_name.split()
    if len(parts) >= 3:
        firstname = parts[0]
        lastname = parts[1]
        surname = ' '.join(parts[2:])
    elif len(parts) == 2:
        firstname = parts[0]
        lastname = parts[1]
        surname = ''
    elif len(parts) == 1:
        firstname = parts[0]
        lastname = ''
        surname = ''
    else:
        return None, None, None
    return firstname, lastname, surname

def is_numeric(value):
    """Check if value is a numeric contribution amount."""
    if pd.isna(value):
        return False
    val = str(value).strip()
    # Skip non-numeric text values
    if not val or any(c.isalpha() for c in val):
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False

def main():
    app = create_app()
    with app.app_context():
        # Read Excel file
        df = pd.read_excel('GM RCK CONT LIST 2026.xlsx')
        df_clean = df.dropna(how='all')
        
        # Get event columns (all columns after PHONE NO.)
        # Filter out unnamed columns
        event_cols = [col for col in df_clean.columns[3:] if not str(col).startswith('Unnamed')]
        
        print(f"Total members to import: {len(df_clean)}")
        print(f"Event columns: {list(event_cols)}")
        
        # Create or update CommunityEvents
        events_created = 0
        events_updated = 0
        for col in event_cols:
            col = str(col).strip()
            if not col:
                continue
            event = CommunityEvent.query.filter_by(name=col).first()
            if not event:
                event = CommunityEvent(name=col, details='Imported from Excel')
                db.session.add(event)
                events_created += 1
            else:
                events_updated += 1
        db.session.commit()
        print(f"Events created: {events_created}, updated: {events_updated}")
        
        # Get all events for lookup (use stripped names)
        all_events = {e.name: e for e in CommunityEvent.query.all()}
        
        # Import members and contributions
        members_created = 0
        members_updated = 0
        contributions_created = 0
        
        for idx, row in df_clean.iterrows():
            # Skip rows without member name
            if pd.isna(row['MEMBER']):
                continue
            
            # Parse member info
            firstname, lastname, surname = split_name(row['MEMBER'])
            if not firstname:
                continue
            
            phone = clean_phone(row['PHONE NO.'])
            id_number = clean_id_number(row['#'])
            
            # Try to find existing member by id_number or name+phone
            member = None
            if id_number:
                try:
                    member = Member.query.filter_by(id_number=int(id_number)).first()
                except (ValueError, TypeError):
                    pass
            
            if not member:
                member = Member.query.filter_by(
                    firstname=firstname,
                    lastname=lastname,
                    phone_num=phone
                ).first()
            
            if member:
                # Update existing member
                member.phone_num = phone or member.phone_num
                member.surname = surname or member.surname
                members_updated += 1
            else:
                # Create new member
                member = Member(
                    firstname=firstname,
                    lastname=lastname,
                    surname=surname or '',
                    phone_num=phone,
                    id_number=id_number
                )
                db.session.add(member)
                db.session.flush()  # Get member ID
                members_created += 1
            
            # Process contributions for each event
            for col in event_cols:
                event_name = str(col).strip()
                if not event_name:
                    continue
                
                # Use original column name to access row data
                value = row[col]
                if not is_numeric(value):
                    continue
                
                amount = int(float(str(value).strip()))
                if amount <= 0:
                    continue
                
                event = all_events.get(event_name)
                if not event:
                    continue
                
                # Check if contribution already exists
                existing = Contribution.query.filter_by(
                    member_id=member.id,
                    propose=event.id
                ).first()
                
                if not existing:
                    contrib = Contribution(
                        amount=amount,
                        member_id=member.id,
                        propose=event.id,
                        payment_type=Payment.CASH
                    )
                    db.session.add(contrib)
                    contributions_created += 1
        
        db.session.commit()
        print(f"\nImport complete!")
        print(f"Members created: {members_created}")
        print(f"Members updated: {members_updated}")
        print(f"Contributions created: {contributions_created}")

if __name__ == '__main__':
    main()
