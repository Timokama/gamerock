from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import base64
from werkzeug.security import generate_password_hash
from app.register import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.image import get_image_mime_type
# from app.models.deposit import Deposit
from app.models.community_event import CommunityEvent
from app.models.register import Member
from app.models.spouse import Spouse
from app.models.child import Child
from app.models.contribute import Contribution
from app.models.payments import Payment
from app.models.faq import FAQ
from sqlalchemy.orm import joinedload, subqueryload

def is_developer():
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

def can_manage_faq():
    """Developers and administrators may manage the knowledge base."""
    return current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

@bp.route('/')
@login_required
def index():
    user = User.query.get(current_user.id)
    search = request.args.get('search', '')
    email = request.args.get('email', '')
    phone = request.args.get('phone', '')
    id_number = request.args.get('id_number', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')

    query = Member.query

    if search:
        search_terms = [term.strip() for term in search.split() if term.strip()]
        name_conditions = []
        for term in search_terms:
            name_conditions.append(
                db.or_(
                    db.cast(Member.id_number, db.String).ilike(f'%{term}%'),
                    Member.firstname.ilike(f'%{term}%'),
                    Member.lastname.ilike(f'%{term}%'),
                    Member.surname.ilike(f'%{term}%')
                )
            )
        query = query.filter(db.and_(*name_conditions))

    if email:
        query = query.filter(Member.email.ilike(f'%{email}%'))

    if phone:
        query = query.filter(Member.phone_num.ilike(f'%{phone}%'))

    if id_number:
        query = query.filter(db.cast(Member.id_number, db.String).ilike(f'%{id_number}%'))

    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Member.created_at >= from_date)
        except (ValueError, TypeError):
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Member.created_at <= to_date)
        except (ValueError, TypeError):
            pass

    members = query.order_by(Member.created_at.desc()).all()

    return render_template('register/index.html', user=user, members=members, access_levels=AccessLevel, filters={
        'search': search,
        'email': email,
        'phone': phone,
        'id_number': id_number,
        'date_from': date_from,
        'date_to': date_to
    })

@bp.route('/<int:depo_id>/')
@login_required
def deposit(depo_id):
    user = User.query.get(current_user.id)
    register = Member.query.get_or_404(depo_id)
    
    event_id = request.args.get('event', type=int)
    payment_type = request.args.get('payment_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Contribution.query.options(
        joinedload(Contribution.member),
        joinedload(Contribution.community_event)
    ).filter_by(member_id=register.id)
    
    if event_id:
        query = query.filter_by(propose=event_id)
    if payment_type:
        query = query.filter_by(payment_type=payment_type)
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Contribution.trans_date >= from_date)
        except (ValueError, TypeError):
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Contribution.trans_date <= to_date)
        except (ValueError, TypeError):
            pass
    
    contributions = query.order_by(Contribution.trans_date.desc()).all()
    total = sum(c.amount for c in contributions)
    member_contribution_events = db.select(Contribution.propose).where(
        Contribution.member_id == register.id
    ).distinct()
    pending_contributions = CommunityEvent.query.filter(
        ~CommunityEvent.id.in_(member_contribution_events)
    ).all()
    
    spouses = register.spouse
    children = register.child
    all_children = list(register.child)
    for spouse in spouses:
        for child in spouse.child:
            if child.id not in [c.id for c in all_children]:
                all_children.append(child)
    
    events = CommunityEvent.query.all()

    member_profile_image = None
    member_profile_mime_type = 'image/jpeg'
    if register.user_account:
        user_img = register.user_account.image
        if user_img:
            first_img = user_img[0] if isinstance(user_img, list) else user_img
            if first_img and first_img.image:
                member_profile_image = base64.b64encode(first_img.image).decode('ascii')
                member_profile_mime_type = get_image_mime_type(first_img.image)

    return render_template('register/deposit.html', register=register, total=total,
                           pending_contributions=pending_contributions,
                           spouses=spouses, children=children, all_children=all_children,
                           contributions=contributions, events=events, level=Payment,
                           filters={'event': event_id, 'payment_type': payment_type, 'date_from': date_from, 'date_to': date_to},
                           member_profile_image=member_profile_image, member_profile_mime_type=member_profile_mime_type)


@bp.route('/create', methods=('POST', 'GET'))
@login_required
def create():
    user = User.query.get_or_404(current_user.id)
    # cont = Contribute.query.get_or_404(current_user.id)

    if request.method == 'POST':
        
        # Convert date string to Python date object
        date_of_birth = None
        raw_dob = request.form.get('date_of_birth', '').strip()
        if raw_dob:
            try:
                date_of_birth = datetime.strptime(raw_dob, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                flash('Invalid date of birth format.', 'danger')
                return redirect(url_for('register.create'))
        
        id_number = request.form.get('id_number', '').strip()
        email = request.form.get('email', '').strip()
        
        # Check for duplicate ID
        reg = Member.query.filter_by(id_number=id_number).first()
        if reg:
            flash("Duplicate Id, Kindly check your details")
            return redirect(url_for('register.create'))

        # Check for duplicate email
        existing_email = Member.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already exists. Please use a different email.")
            return redirect(url_for('register.create'))

        member_id_number = None
        if id_number:
            try:
                member_id_number = int(id_number)
            except (ValueError, TypeError):
                flash('ID number must be a valid integer.', 'danger')
                return redirect(url_for('register.create'))

        # Create member
        register = Member(
            firstname=request.form['firstname'],
            lastname=request.form['lastname'],
            surname=request.form['surname'],
            date_of_birth=date_of_birth,
            id_number=member_id_number,
            phone_num=request.form['phone_num'],
            email=email,
            user=user
        )
        db.session.add(register)
        db.session.flush()  # Get the member ID before committing
        
        # Create user account for the member with password = ID number
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(
                surname=register.surname,
                first_name=register.firstname,
                email=email,
                phone_num=register.phone_num,
                passwords=id_number or str(register.id),  # Password is the ID number or member ID
                role=AccessLevel.USER
            )
            db.session.add(new_user)
            db.session.flush()
            register.user_id = new_user.id
        
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template('register/create.html')

@bp.route('/<int:depo_id>/editname', methods=('POST', 'GET'))
@login_required
def edit_name(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        surname = request.form['surname']
        
        raw_dob = request.form.get('date_of_birth', '').strip()
        date_of_birth = None
        if raw_dob:
            try:
                date_of_birth = datetime.strptime(raw_dob, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                flash('Invalid date of birth format.', 'danger')
                return redirect(url_for('register.edit_name', depo_id=register.id))
        
        phone_num=request.form['phone_num']
        email=request.form['email']
        raw_id = request.form['id_number'].strip()
        id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None

        register.firstname = firstname
        register.lastname = lastname
        register.surname = surname
        register.phone_num = phone_num
        register.email = email
        register.date_of_birth = date_of_birth
        register.id_number = id_number

        # Update linked user account email if exists
        if register.user_account:
            register.user_account.email = email
            register.user_account.phone_num = phone_num
            register.user_account.role = AccessLevel.USER
        else:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(
                    surname=register.surname,
                    first_name=register.firstname,
                    email=email,
                    phone_num=register.phone_num,
                    passwords=str(id_number) if id_number is not None else str(register.id),
                    role=AccessLevel.USER
                )
                db.session.add(new_user)
                db.session.flush()
                register.user_id = new_user.id

        db.session.add(register)
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template('register/edit.html', register = register, family = register)

@bp.route('/<int:depo_id>/create_spouse/', methods=('POST','GET'))
def create_spouse(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        # register = Register.query.get_or_404(depo_id)
        # spouse = depo.family.id
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        new_spouse = Spouse(firstname = request.form['firstname'], lastname = request.form['lastname'], surname = request.form['surname'], phone_num = request.form['phone_num'], date_of_birth = date_of_birth, id_number=request.form['id_number'],member = register)
        db.session.add(new_spouse)
        db.session.commit()
        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/create_spouse.html', register=register)

@bp.route('/<int:depo_id>/create_child/', methods=('POST','GET'))
def create_child(depo_id):
    # depo = Deposit.query.get_or_404(depo_id)
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        # register = Register.query.get_or_404(depo_id)
        # spouse = depo.family.id
        date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
        new_child = Child(firstname = request.form['firstname'], lastname = request.form['lastname'], surname = request.form['surname'], phone_num = request.form['phone_num'], date_of_birth = date_of_birth, id_number=request.form['id_number'],member = register)
        db.session.add_all([new_child])
        db.session.commit()
        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/create_child.html', register = register)

@bp.post('/<int:depo_id>/delete/')
@login_required
def delete(depo_id):
    # depo = User.query.get_or_404(current_user.id)
    register = Member.query.get_or_404(depo_id)
    
    for deposit in register.contribute:
        db.session.delete(deposit)
    for child in register.child:
        db.session.delete(child)
    for spouse in register.spouse:
        for child_ in spouse.child:
            db.session.delete(child_)
        db.session.delete(spouse)
    
    db.session.delete(register)
    db.session.commit()
    return redirect(url_for('register.index'))

@bp.route('/<int:depo_id>/edit', methods=('POST', 'GET'))
@login_required
def edit(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        surname = request.form['surname']
        
        raw_dob = request.form.get('date_of_birth', '').strip()
        date_of_birth = None
        if raw_dob:
            try:
                date_of_birth = datetime.strptime(raw_dob, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                flash('Invalid date of birth format.', 'danger')
                return redirect(url_for('register.edit', depo_id=register.id))
        
        phone_num=request.form['phone_num']
        email=request.form['email']
        raw_id = request.form['id_number'].strip()
        id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None

        register.firstname = firstname
        register.lastname = lastname
        register.surname = surname
        register.phone_num = phone_num
        register.email = email
        register.date_of_birth = date_of_birth
        register.id_number = id_number

        # Update linked user account email if exists
        if register.user_account:
            register.user_account.email = email
            register.user_account.phone_num = phone_num
            register.user_account.role = AccessLevel.USER
        else:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(
                    surname=register.surname,
                    first_name=register.firstname,
                    email=email,
                    phone_num=register.phone_num,
                    passwords=str(id_number) if id_number is not None else str(register.id),
                    role=AccessLevel.USER
                )
                db.session.add(new_user)
                db.session.flush()
                register.user_id = new_user.id

        db.session.add(register)
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template("register/edit.html", register = register)


@bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get_or_404(current_user.id)
    
    search = request.args.get('search', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    member = Member.query.filter_by(user_id=user.id).first()
    
    user_image = None
    user_image_mime_type = 'image/jpeg'
    if user.image:
        first_img = user.image[0]
        user_image = base64.b64encode(first_img.image).decode('ascii')
        user_image_mime_type = get_image_mime_type(first_img.image)
    
    if not member:
        return render_template('register/dashboard.html', user=user, member=None, user_image=user_image, user_image_mime_type=user_image_mime_type)
    
    contributions = Contribution.query.filter_by(member_id=member.id).order_by(Contribution.trans_date.desc()).all()
    
    total_contributed = sum(c.amount for c in contributions)
    total_contributed = "{:,}".format(total_contributed)
    
    from app.models.community_event import CommunityEvent
    query = CommunityEvent.query.options(subqueryload(CommunityEvent.contribute))
    
    if search:
        query = query.filter(
            db.or_(
                CommunityEvent.name.ilike(f'%{search}%'),
                CommunityEvent.details.ilike(f'%{search}%')
            )
        )
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(CommunityEvent.event_date >= from_date)
        except (ValueError, TypeError):
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(CommunityEvent.event_date <= to_date)
        except (ValueError, TypeError):
            pass
    
    events = query.order_by(CommunityEvent.event_date.desc()).all()
    
    event_balances = []
    contributed_event_ids = set()
    for event in events:
        event_total = sum(c.amount for c in event.contribute if c.member_id == member.id)
        event_balances.append({
            'event': event,
            'contributed': event_total,
            'has_contributed': event_total > 0
        })
        if event_total > 0:
            contributed_event_ids.add(event.id)
    
    all_events = []
    contributed_events = []
    pending_events = []
    for event in events:
        event_total = sum(c.amount for c in event.contribute)
        contributor_count = len(set(c.member_id for c in event.contribute))
        event_data = {
            'event': event,
            'total': event_total,
            'contributions': event.contribute,
            'contributor_count': contributor_count
        }
        all_events.append(event_data)
        if event.id in contributed_event_ids:
            contributed_events.append(event_data)
        else:
            pending_events.append(event_data)
    
    all_contributions = Contribution.query.order_by(Contribution.trans_date.desc()).all()
    
    spouses = member.spouse
    children = member.child
    
    all_children = list(member.child)
    for spouse in spouses:
        for child in spouse.child:
            if child.id not in [c.id for c in all_children]:
                all_children.append(child)
    
    deposits = contributions
    total_deposits = sum(c.amount for c in deposits)
    total_deposits = "{:,}".format(total_deposits)
    
    faqs = []
    if current_user.role.name in ['DEVEL', 'ADMIN']:
        faqs = FAQ.query.order_by(FAQ.created_at.asc()).all()
    
    return render_template('register/dashboard.html',
                         user=user,
                         member=member,
                         contributions=contributions,
                         total_contributed=total_contributed,
                         event_balances=event_balances,
                         all_events=all_events,
                         contributed_events=contributed_events,
                         pending_events=pending_events,
                         all_contributions=all_contributions,
                         spouses=spouses,
                         children=children,
                         all_children=all_children,
                         deposits=deposits,
                         total_deposits=total_deposits,
                         faqs=faqs,
                         user_image=user_image,
                         user_image_mime_type=user_image_mime_type)

@bp.post('/<int:member_id>/assign_admin')
@login_required
def assign_admin(member_id):
    if not is_developer():
        flash('You do not have permission to assign admin roles.')
        return redirect(url_for('register.index'))
    
    member = Member.query.get_or_404(member_id)
    if not member.user_id:
        flash('This member does not have a user account.')
        return redirect(url_for('register.index'))
    
    user = User.query.get(member.user_id)
    if user:
        user.role = AccessLevel.ADMIN
        db.session.commit()
        flash(f'Successfully assigned Admin role to {member.firstname} {member.lastname}.')
    else:
        flash('User account not found.')
    
    return redirect(url_for('register.index'))

@bp.post('/<int:member_id>/assign_user')
@login_required
def assign_user(member_id):
    if not is_developer():
        flash('You do not have permission to assign user roles.')
        return redirect(url_for('register.index'))
    
    member = Member.query.get_or_404(member_id)
    if not member.user_id:
        flash('This member does not have a user account.')
        return redirect(url_for('register.index'))
    
    user = User.query.get(member.user_id)
    if user:
        user.role = AccessLevel.USER
        db.session.commit()
        flash(f'Successfully assigned User role to {member.firstname} {member.lastname}.')
    else:
        flash('User account not found.')
    
    return redirect(url_for('register.index'))

@bp.post('/<int:member_id>/assign_role')
@login_required
def assign_role(member_id):
    if not is_developer():
        flash('You do not have permission to assign roles.')
        return redirect(url_for('register.index'))
    
    member = Member.query.get_or_404(member_id)
    if not member.user_id:
        flash('This member does not have a user account.')
        return redirect(url_for('register.index'))
    
    role_name = request.form.get('role')
    if not role_name:
        flash('No role specified.')
        return redirect(url_for('register.index'))
    
    try:
        new_role = AccessLevel[role_name]
    except KeyError:
        flash('Invalid role specified.')
        return redirect(url_for('register.index'))
    
    if new_role == AccessLevel.DEVEL:
        flash('Developer role cannot be assigned through this interface.')
        return redirect(url_for('register.index'))
    
    user = User.query.get_or_404(member.user_id)
    if user.role == new_role:
        flash(f'{member.firstname} {member.lastname} already has the {new_role.display_name} role.')
        return redirect(url_for('register.index'))
    
    user.role = new_role
    db.session.commit()
    flash(f'Successfully assigned {new_role.display_name} role to {member.firstname} {member.lastname}.')
    return redirect(url_for('register.index'))

FAQ_DEFAULT_CATEGORIES = [
    'General',
    'Membership',
    'Contributions',
    'Events',
    'Family',
    'Account',
    'Support',
]


def faq_category_choices():
    """Curated categories merged with any category already stored in the DB."""
    used = [
        row[0] for row in db.session.query(FAQ.category)
        .filter(FAQ.category.isnot(None), FAQ.category != '')
        .distinct().all()
    ]
    choices = list(FAQ_DEFAULT_CATEGORIES)
    for category in sorted(used):
        if category not in choices:
            choices.append(category)
    return choices


@bp.route('/faq')
@login_required
def faq_list():
    if not can_manage_faq():
        flash('You do not have permission to manage FAQs.')
        return redirect(url_for('main.faq'))

    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', 'newest')

    query = FAQ.query

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(
                FAQ.question.ilike(like),
                FAQ.answer.ilike(like),
                FAQ.category.ilike(like),
            )
        )

    if category == 'uncategorised':
        query = query.filter(db.or_(FAQ.category.is_(None), FAQ.category == ''))
    elif category:
        query = query.filter(FAQ.category == category)

    sort_options = {
        'newest': FAQ.created_at.desc(),
        'oldest': FAQ.created_at.asc(),
        'question': FAQ.question.asc(),
        'category': FAQ.category.asc(),
    }
    query = query.order_by(sort_options.get(sort, FAQ.created_at.desc()))

    faqs = query.all()
    all_faqs = FAQ.query.all()

    category_counts = {}
    uncategorised = 0
    for faq in all_faqs:
        if faq.category:
            category_counts[faq.category] = category_counts.get(faq.category, 0) + 1
        else:
            uncategorised += 1

    stats = {
        'total': len(all_faqs),
        'categories': len(category_counts),
        'uncategorised': uncategorised,
        'showing': len(faqs),
    }

    return render_template(
        'register/faq.html',
        faqs=faqs,
        stats=stats,
        category_counts=dict(sorted(category_counts.items())),
        categories=faq_category_choices(),
        filters={'search': search, 'category': category, 'sort': sort},
    )

@bp.route('/faq/create', methods=('GET', 'POST'))
@login_required
def faq_create():
    if not can_manage_faq():
        flash('You do not have permission to manage FAQs.')
        return redirect(url_for('main.faq'))
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        category = request.form.get('category', '').strip()
        if not question or not answer:
            flash('Question and answer are required.', 'danger')
            return redirect(url_for('register.faq_create'))
        faq = FAQ(question=question, answer=answer, category=category or None, created_by=current_user.id)
        db.session.add(faq)
        db.session.commit()
        flash('FAQ created successfully!', 'success')
        return redirect(url_for('register.faq_list'))
    return render_template('register/faq_form.html', faq=None, categories=faq_category_choices())

@bp.route('/faq/<int:faq_id>/edit', methods=('GET', 'POST'))
@login_required
def faq_edit(faq_id):
    if not can_manage_faq():
        flash('You do not have permission to manage FAQs.')
        return redirect(url_for('main.faq'))
    faq = FAQ.query.get_or_404(faq_id)
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        answer = request.form.get('answer', '').strip()
        if not question or not answer:
            flash('Question and answer are required.', 'danger')
            return redirect(url_for('register.faq_edit', faq_id=faq.id))
        faq.question = question
        faq.answer = answer
        faq.category = request.form.get('category', '').strip() or None
        db.session.commit()
        flash('FAQ updated successfully!', 'success')
        return redirect(url_for('register.faq_list'))
    return render_template('register/faq_form.html', faq=faq, categories=faq_category_choices())

@bp.post('/faq/<int:faq_id>/delete')
@login_required
def faq_delete(faq_id):
    if not can_manage_faq():
        flash('You do not have permission to manage FAQs.')
        return redirect(url_for('main.faq'))
    faq = FAQ.query.get_or_404(faq_id)
    db.session.delete(faq)
    db.session.commit()
    flash('FAQ deleted successfully!', 'success')
    return redirect(url_for('register.faq_list'))
