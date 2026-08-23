from app import create_app, db
from app.models.community_event import CommunityEvent
from app.models.contribute import Contribution

app = create_app()
with app.app_context():
    events = CommunityEvent.query.all()
    print(f"Total events: {len(events)}")
    for event in events:
        contribs = event.contribute
        print(f"Event: {event.name}, Contributions count: {len(contribs)}, Total: {sum(c.amount for c in contribs)}")
        for c in contribs:
            print(f"  - Contribution: amount={c.amount}, propose={c.propose}, member_id={c.member_id}")
    
    total_contribs = Contribution.query.count()
    print(f"\nTotal contributions in DB: {total_contribs}")
    
    # Check contributions with propose set
    with_propose = Contribution.query.filter(Contribution.propose != None).count()
    print(f"Contributions with propose set: {with_propose}")
    
    # Check contributions without propose
    without_propose = Contribution.query.filter(Contribution.propose == None).count()
    print(f"Contributions without propose: {without_propose}")
