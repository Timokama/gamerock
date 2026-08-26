"""
Seed script: creates demo users (if missing) and populates
realistic sample data for Budget, BudgetItem, TreasurerRecord, and Minutes.

Usage:
    python seed_demo_data.py
"""

from app import create_app, db
from app.user import User
from app.level import AccessLevel
from app.models.budget import Budget, BudgetItem
from app.models.treasurer import TreasurerRecord
from app.models.minutes import Minutes
from datetime import datetime, date, timedelta

app = create_app()

DEMO_USERS = [
    {
        "email": "admin@gamerock.org",
        "password": "admin123",
        "first_name": "Admin",
        "surname": "User",
        "role": AccessLevel.ADMIN,
    },
    {
        "email": "treasurer@gamerock.org",
        "password": "treasurer123",
        "first_name": "Treasurer",
        "surname": "User",
        "role": AccessLevel.TREASURER,
    },
    {
        "email": "secretary@gamerock.org",
        "password": "secretary123",
        "first_name": "Secretary",
        "surname": "User",
        "role": AccessLevel.SECRETARY,
    },
]

BUDGETS = [
    {
        "name": "Q1 2026 Operations Budget",
        "description": "Quarterly operating budget covering utilities, rent, and admin costs.",
        "fiscal_year": "2026",
        "total_amount": 850000,
        "status": "Approved",
        "items": [
            {"category": "Rent", "description": "Community hall rental", "amount": 300000, "item_type": "Expense"},
            {"category": "Utilities", "description": "Power, water, internet", "amount": 120000, "item_type": "Expense"},
            {"category": "Office Supplies", "description": "Stationery and printing", "amount": 50000, "item_type": "Expense"},
            {"category": "Event Contribution", "description": "Expected community event support", "amount": 380000, "item_type": "Income"},
        ],
    },
    {
        "name": "2026 Welfare Fund Budget",
        "description": "Annual welfare fund allocation for member support and outreach.",
        "fiscal_year": "2026",
        "total_amount": 1200000,
        "status": "Active",
        "items": [
            {"category": "Member Support", "description": "Emergency member assistance", "amount": 400000, "item_type": "Expense"},
            {"category": "Outreach", "description": "Community outreach programs", "amount": 250000, "item_type": "Expense"},
            {"category": "Savings", "description": "Reserve fund contribution", "amount": 200000, "item_type": "Income"},
            {"category": "Donations", "description": "External donations received", "amount": 350000, "item_type": "Income"},
        ],
    },
    {
        "name": "2025 Annual Budget",
        "description": "Previous year annual budget for reference and carryover analysis.",
        "fiscal_year": "2025",
        "total_amount": 950000,
        "status": "Closed",
        "items": [
            {"category": "Administration", "description": "Staff and admin costs", "amount": 450000, "item_type": "Expense"},
            {"category": "Programs", "description": "Member programs and events", "amount": 300000, "item_type": "Expense"},
            {"category": "Grants", "description": "Grant funding received", "amount": 200000, "item_type": "Income"},
        ],
    },
]

TREASURER_RECORDS = [
    {
        "record_type": "Income",
        "amount": 150000,
        "category": "Tithes",
        "description": "Monthly tithe collection from members.",
        "reference": "TITHE-2026-001",
        "transaction_date": date.today() - timedelta(days=2),
    },
    {
        "record_type": "Income",
        "amount": 85000,
        "category": "Donations",
        "description": "Donation received from local business.",
        "reference": "DON-2026-004",
        "transaction_date": date.today() - timedelta(days=5),
    },
    {
        "record_type": "Expense",
        "amount": 120000,
        "category": "Utilities",
        "description": "Quarterly electricity and water bill.",
        "reference": "UTIL-2026-012",
        "transaction_date": date.today() - timedelta(days=7),
    },
    {
        "record_type": "Expense",
        "amount": 45000,
        "category": "Supplies",
        "description": "Office and event supplies purchase.",
        "reference": "SUP-2026-008",
        "transaction_date": date.today() - timedelta(days=10),
    },
    {
        "record_type": "Income",
        "amount": 300000,
        "category": "Event Contribution",
        "description": "Community fundraising event proceeds.",
        "reference": "EVENT-2026-003",
        "transaction_date": date.today() - timedelta(days=12),
    },
    {
        "record_type": "Expense",
        "amount": 95000,
        "category": "Rent",
        "description": "Monthly hall rental payment.",
        "reference": "RENT-2026-005",
        "transaction_date": date.today() - timedelta(days=14),
    },
    {
        "record_type": "Income",
        "amount": 120000,
        "category": "Member Dues",
        "description": "Annual membership dues batch.",
        "reference": "DUES-2026-002",
        "transaction_date": date.today() - timedelta(days=20),
    },
    {
        "record_type": "Expense",
        "amount": 60000,
        "category": "Outreach",
        "description": "Welfare outreach program expenses.",
        "reference": "OUT-2026-006",
        "transaction_date": date.today() - timedelta(days=25),
    },
]

MINUTES = [
    {
        "title": "January 2026 General Meeting",
        "meeting_type": "General",
        "meeting_date": date.today() - timedelta(days=25),
        "location": "Community Hall",
        "agenda": "Budget approval, welfare fund review, upcoming events.",
        "discussion": "Members reviewed Q4 financials and approved the annual welfare budget.",
        "decisions": "Approved 2026 welfare fund budget. Assigned event planning committee.",
        "action_items": "Treasurer to open new savings account. Secretary to publish meeting notes.",
        "next_meeting_date": date.today() + timedelta(days=25),
        "attendees": "All available members",
        "status": "Approved",
    },
    {
        "title": "February 2026 Committee Meeting",
        "meeting_type": "Committee",
        "meeting_date": date.today() - timedelta(days=15),
        "location": "Zoom / Hybrid",
        "agenda": "Event planning, budget reallocation.",
        "discussion": "Reviewed venue options and proposed budget adjustments for Q2.",
        "decisions": "Approved venue booking. Reallocated Ksh. 50,000 from supplies to events.",
        "action_items": "Chair to confirm venue contract. Treasurer to update budget tracker.",
        "next_meeting_date": date.today() + timedelta(days=15),
        "attendees": "Committee members",
        "status": "Approved",
    },
    {
        "title": "March 2026 Emergency Session",
        "meeting_type": "Emergency",
        "meeting_date": date.today() - timedelta(days=5),
        "location": "Community Hall",
        "agenda": "Urgent welfare support case.",
        "discussion": "Discussed urgent member support request and emergency fund eligibility.",
        "decisions": "Approved emergency welfare disbursement. Agreed to review policy next quarter.",
        "action_items": "Treasurer to process disbursement within 48 hours. Secretary to notify member.",
        "next_meeting_date": date.today() + timedelta(days=5),
        "attendees": "Core committee",
        "status": "Approved",
    },
    {
        "title": "April 2026 General Meeting",
        "meeting_type": "General",
        "meeting_date": date.today() + timedelta(days=5),
        "location": "Community Hall",
        "agenda": "Q1 review, new member onboarding, community day planning.",
        "discussion": "Pending. Scheduled for next month.",
        "decisions": "Pending.",
        "action_items": "Pending.",
        "next_meeting_date": date.today() + timedelta(days=35),
        "attendees": "All available members",
        "status": "Draft",
    },
]


def get_or_create_user(spec):
    user = User.query.filter_by(email=spec["email"]).first()
    if user:
        return user
    user = User(
        email=spec["email"],
        first_name=spec["first_name"],
        surname=spec["surname"],
        role=spec["role"],
    )
    user.passwords = spec["password"]
    db.session.add(user)
    db.session.commit()
    return user


def seed_budgets(users):
    admin = next((u for u in users if u.role.name == "ADMIN"), users[0])
    for data in BUDGETS:
        existing = Budget.query.filter_by(name=data["name"], fiscal_year=data["fiscal_year"]).first()
        if existing:
            continue
        budget = Budget(
            name=data["name"],
            description=data.get("description", ""),
            fiscal_year=data["fiscal_year"],
            total_amount=data["total_amount"],
            status=data.get("status", "Draft"),
            created_by=admin.id,
            approved_by=admin.id if data.get("status") == "Approved" else None,
            approved_at=datetime.utcnow() if data.get("status") == "Approved" else None,
            created_at=datetime.utcnow() - timedelta(days=30),
        )
        db.session.add(budget)
        db.session.flush()

        for item_data in data.get("items", []):
            item = BudgetItem(
                budget_id=budget.id,
                category=item_data["category"],
                description=item_data.get("description", ""),
                amount=item_data["amount"],
                item_type=item_data.get("item_type", "Expense"),
            )
            db.session.add(item)
    db.session.commit()


def seed_treasurer_records(users):
    treasurer = next((u for u in users if u.role.name == "TREASURER"), users[0])
    existing_count = TreasurerRecord.query.count()
    if existing_count >= len(TREASURER_RECORDS):
        return
    for data in TREASURER_RECORDS:
        record = TreasurerRecord(
            record_type=data["record_type"],
            amount=data["amount"],
            category=data["category"],
            description=data.get("description", ""),
            reference=data.get("reference", ""),
            transaction_date=data["transaction_date"],
            created_by=treasurer.id,
            created_at=datetime.utcnow() - timedelta(days=10),
        )
        db.session.add(record)
    db.session.commit()


def seed_minutes(users):
    secretary = next((u for u in users if u.role.name == "SECRETARY"), users[0])
    existing_count = Minutes.query.count()
    if existing_count >= len(MINUTES):
        return
    for data in MINUTES:
        entry = Minutes(
            title=data["title"],
            meeting_type=data["meeting_type"],
            meeting_date=data["meeting_date"],
            location=data.get("location", ""),
            agenda=data.get("agenda", ""),
            discussion=data.get("discussion", ""),
            decisions=data.get("decisions", ""),
            action_items=data.get("action_items", ""),
            next_meeting_date=data.get("next_meeting_date"),
            attendees=data.get("attendees", ""),
            status=data.get("status", "Draft"),
            created_by=secretary.id,
            approved_by=secretary.id if data.get("status") == "Approved" else None,
            approved_at=datetime.utcnow() if data.get("status") == "Approved" else None,
            created_at=datetime.utcnow() - timedelta(days=20),
        )
        db.session.add(entry)
    db.session.commit()


def main():
    with app.app_context():
        db.create_all()
        users = [get_or_create_user(spec) for spec in DEMO_USERS]
        print(f"Ensured {len(users)} demo users exist.")

        seed_budgets(users)
        print("Seeded budgets and budget items.")

        seed_treasurer_records(users)
        print("Seeded treasurer records.")

        seed_minutes(users)
        print("Seeded minutes.")

        print("Done. Summary:")
        print(f"  Budgets: {Budget.query.count()}")
        print(f"  Budget Items: {BudgetItem.query.count()}")
        print(f"  Treasurer Records: {TreasurerRecord.query.count()}")
        print(f"  Minutes: {Minutes.query.count()}")


if __name__ == "__main__":
    main()
