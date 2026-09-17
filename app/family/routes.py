from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from app.family import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member
from app.models.community_event import CommunityEvent
from app.models.child import Child
from app.models.spouse import Spouse

@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    total_members = 0
    total_spouses = 0
    total_children = 0
    member_stats = {}
    if user.role in (AccessLevel.ADMIN, AccessLevel.DEVEL):
        members = Member.query.order_by(Member.created_at.desc()).all()
        total_members = len(members)
        member_children = {}
        for member in members:
            spouse_count = len(member.spouse)
            direct_children = len(member.child)
            spouse_children = sum(len(spouse.child) for spouse in member.spouse)
            total_spouses += spouse_count
            total_children += direct_children + spouse_children
            member_stats[member.id] = {
                'spouse_count': spouse_count,
                'direct_children': direct_children,
                'spouse_children': spouse_children,
                'total_children': direct_children + spouse_children,
            }
            all_children = list(member.child)
            for spouse in member.spouse:
                all_children.extend(spouse.child)
            member_children[member.id] = all_children
        return render_template("family/index.html", members=members, total_members=total_members, total_spouses=total_spouses, total_children=total_children, member_stats=member_stats, member_children=member_children)
    member = user.member_profile
    if not member:
        members = []
        return render_template("family/index.html", members=members, total_members=0, total_spouses=0, total_children=0, member_stats={}, member_children={})

    members = [member]
    spouse_count = len(member.spouse)
    direct_children = len(member.child)
    spouse_children = sum(len(spouse.child) for spouse in member.spouse)
    total_spouses = spouse_count
    total_children = direct_children + spouse_children
    member_stats = {
        member.id: {
            'spouse_count': spouse_count,
            'direct_children': direct_children,
            'spouse_children': spouse_children,
            'total_children': total_children,
        }
    }
    member_children = {}
    all_children = list(member.child)
    for spouse in member.spouse:
        for child in spouse.child:
            all_children.append(child)
    member_children[member.id] = all_children
    return render_template("family/index.html", members=members, total_members=1, total_spouses=total_spouses, total_children=total_children, member_stats=member_stats, member_children=member_children, user=user, member=member)


@bp.route('/<int:depo_id>/')
@login_required
def family(depo_id):
    register = Member.query.get_or_404(depo_id)
    return render_template('family/family.html', register = register)

@bp.route('/<int:depo_id>/edit', methods=('POST', 'GET'))
@login_required
def edit(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        try:
            firstname=request.form['firstname']
            lastname=request.form['lastname']
            surname = request.form['surname']
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            phone_num=request.form['phone_num']
            email=request.form['email']
            id_number=request.form['id_number']

            register.firstname = firstname
            register.lastname = lastname
            register.surname = surname
            register.phone_num = phone_num
            register.email = email
            register.date_of_birth = date_of_birth
            register.id_number = id_number

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
                        passwords=id_number,
                        role=AccessLevel.USER
                    )
                    db.session.add(new_user)
                    db.session.flush()
                    register.user_id = new_user.id

            db.session.add(register)
            db.session.commit()
            flash('Member updated successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except IntegrityError:
            db.session.rollback()
            flash('Failed to update member. The ID number or email you entered is already in use.', 'error')
            return redirect(url_for('family.edit', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update member. Please check your input and try again.', 'error')
            return redirect(url_for('family.edit', depo_id=register.id))
    return render_template('register/edit.html', register = register, family = register)

@bp.route('/<int:depo_id>/create_spouse', methods=('POST', 'GET'))
@login_required
def create_spouse(depo_id):
    if depo_id == 0:
        flash("Please select a member first to add family information.", "error")
        return redirect(url_for('register.index'))
    
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        try:
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            raw_id = request.form.get('id_number', '').strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            phone_num = request.form.get('phone_num', '').strip()
            email = request.form.get('email', '').strip()

            # Check for duplicate ID number
            if id_number:
                if Spouse.query.filter_by(id_number=id_number).first():
                    flash('This ID number is already associated with another spouse.', 'error')
                    return redirect(url_for('family.create_spouse', depo_id=register.id))
                if Member.query.filter_by(id_number=id_number).first():
                    flash('This ID number is already associated with another member.', 'error')
                    return redirect(url_for('family.create_spouse', depo_id=register.id))

            # Check for duplicate email
            if email:
                if User.query.filter_by(email=email).first():
                    flash('This email is already associated with an account.', 'error')
                    return redirect(url_for('family.create_spouse', depo_id=register.id))
                if Member.query.filter_by(email=email).first():
                    flash('This email is already associated with a member.', 'error')
                    return redirect(url_for('family.create_spouse', depo_id=register.id))

            new_spouse = Spouse(
                firstname=request.form['firstname'],
                lastname=request.form['lastname'],
                surname=request.form['surname'],
                phone_num=phone_num,
                email=email,
                date_of_birth=date_of_birth,
                id_number=id_number,
                member=register
            )
            db.session.add(new_spouse)
            db.session.flush()

            # Create User account for the spouse if email provided
            if email:
                password_value = str(id_number) if id_number else str(new_spouse.id)
                new_user = User(
                    surname=new_spouse.surname,
                    first_name=new_spouse.firstname,
                    email=email,
                    phone_num=phone_num,
                    passwords=password_value,
                    role=AccessLevel.USER
                )
                db.session.add(new_user)
                db.session.flush()
                new_spouse.user_id = new_user.id

            db.session.commit()
            flash('Spouse added successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add spouse. Please check your input and try again.', 'error')
            return redirect(url_for('family.create_spouse', depo_id=register.id))
    return render_template('register/create_spouse.html', register=register)

@bp.route('/<int:depo_id>/<int:spouse_id>/create_child', methods=('POST', 'GET'))
@login_required
def create_child(depo_id, spouse_id):
    register = Member.query.get_or_404(depo_id)
    spouse = Spouse.query.get_or_404(spouse_id)
    if request.method == 'POST':
        try:
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            raw_id = request.form.get('id_number', '').strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            phone_num = request.form.get('phone_num', '').strip()
            email = request.form.get('email', '').strip()

            # Check for duplicate ID number
            if id_number:
                if Child.query.filter_by(id_number=id_number).first():
                    flash('This ID number is already associated with another child.', 'error')
                    return redirect(url_for('family.create_child', depo_id=register.id, spouse_id=spouse.id))
                if Member.query.filter_by(id_number=id_number).first():
                    flash('This ID number is already associated with a member.', 'error')
                    return redirect(url_for('family.create_child', depo_id=register.id, spouse_id=spouse.id))

            # Check for duplicate email
            if email:
                if User.query.filter_by(email=email).first():
                    flash('This email is already associated with an account.', 'error')
                    return redirect(url_for('family.create_child', depo_id=register.id, spouse_id=spouse.id))
                if Member.query.filter_by(email=email).first():
                    flash('This email is already associated with a member.', 'error')
                    return redirect(url_for('family.create_child', depo_id=register.id, spouse_id=spouse.id))

            child = Child(
                firstname=request.form['firstname'],
                lastname=request.form['lastname'],
                surname=request.form['surname'],
                phone_num=phone_num,
                id_number=id_number,
                email=email,
                date_of_birth=date_of_birth,
                spouse=spouse
            )
            db.session.add(child)
            db.session.flush()

            # Create User account for the child if email provided
            if email:
                password_value = str(id_number) if id_number else str(child.id)
                new_user = User(
                    surname=child.surname,
                    first_name=child.firstname,
                    email=email,
                    phone_num=phone_num,
                    passwords=password_value,
                    role=AccessLevel.USER
                )
                db.session.add(new_user)
                db.session.flush()
                child.user_id = new_user.id

            db.session.commit()
            flash('Child added successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add child. Please check your input and try again.', 'error')
            return redirect(url_for('family.create_child', depo_id=register.id, spouse_id=spouse.id))
    return render_template('register/create_child.html', register=register, spouse=spouse)

@bp.post('/<int:depo_id>/<int:del_id>/delete')
@login_required
def delete(depo_id, del_id):
    register = Member.query.get_or_404(depo_id)
    spouse = Spouse.query.get_or_404(del_id)
    for child in spouse.child:
        db.session.delete(child)
    db.session.delete(spouse)
    db.session.commit()
    return redirect(url_for('family.family', depo_id = register.id))

@bp.route('/<int:depo_id>/<int:edit_id>/edit_spouse', methods=('POST','GET'))
@login_required
def edit_spouse(depo_id, edit_id):
    register = Member.query.get_or_404(depo_id)
    spouse = Spouse.query.get_or_404(edit_id)
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            surname = request.form['surname']
            phone_num = request.form.get('phone_num', '').strip()
            email = request.form.get('email', '').strip()
            raw_id = request.form.get('id_number', '').strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()

            # Check for duplicate ID number
            if id_number:
                existing_spouse = Spouse.query.filter_by(id_number=id_number).first()
                if existing_spouse and existing_spouse.id != spouse.id:
                    flash('This ID number is already associated with another spouse.', 'error')
                    return redirect(url_for('family.edit_spouse', depo_id=register.id, edit_id=spouse.id))
                existing_member = Member.query.filter_by(id_number=id_number).first()
                if existing_member:
                    flash('This ID number is already associated with a member.', 'error')
                    return redirect(url_for('family.edit_spouse', depo_id=register.id, edit_id=spouse.id))

            # Check for duplicate email
            if email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and (not spouse.user_id or existing_user.id != spouse.user_id):
                    flash('This email is already associated with an account.', 'error')
                    return redirect(url_for('family.edit_spouse', depo_id=register.id, edit_id=spouse.id))
                existing_member = Member.query.filter_by(email=email).first()
                if existing_member and existing_member.id != register.id:
                    flash('This email is already associated with a member.', 'error')
                    return redirect(url_for('family.edit_spouse', depo_id=register.id, edit_id=spouse.id))

            spouse.firstname = firstname
            spouse.lastname = lastname
            spouse.surname = surname
            spouse.phone_num = phone_num
            spouse.email = email
            spouse.id_number = id_number
            spouse.date_of_birth = date_of_birth

            # Update or create User account for the spouse
            if email:
                password_value = str(id_number) if id_number else str(spouse.id)
                if spouse.user_id:
                    existing_user = User.query.get(spouse.user_id)
                    if existing_user:
                        existing_user.surname = surname
                        existing_user.first_name = firstname
                        existing_user.email = email
                        existing_user.phone_num = phone_num
                        existing_user.role = AccessLevel.USER
                else:
                    new_user = User(
                        surname=surname,
                        first_name=firstname,
                        email=email,
                        phone_num=phone_num,
                        passwords=password_value,
                        role=AccessLevel.USER
                    )
                    db.session.add(new_user)
                    db.session.flush()
                    spouse.user_id = new_user.id

            db.session.add(spouse)
            db.session.commit()
            flash('Spouse updated successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update spouse. Please check your input and try again.', 'error')
            return redirect(url_for('family.edit_spouse', depo_id=register.id, edit_id=spouse.id))
    return render_template('register/edit.html', register = spouse, family = register)

@bp.route('/<int:depo_id>/<int:edit_id>/<int:child_id>/edit_child', methods=('POST','GET'))
@login_required
def edit_child(depo_id, edit_id, child_id):
    register = Member.query.get_or_404(depo_id)
    spouse = Spouse.query.get_or_404(edit_id)
    child = Child.query.get_or_404(child_id)
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            surname = request.form['surname']
            phone_num = request.form.get('phone_num', '').strip()
            email = request.form.get('email', '').strip()
            raw_id = request.form.get('id_number', '').strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()

            # Check for duplicate ID number
            if id_number:
                existing_child = Child.query.filter_by(id_number=id_number).first()
                if existing_child and existing_child.id != child.id:
                    flash('This ID number is already associated with another child.', 'error')
                    return redirect(url_for('family.edit_child', depo_id=register.id, edit_id=spouse.id, child_id=child.id))
                existing_member = Member.query.filter_by(id_number=id_number).first()
                if existing_member:
                    flash('This ID number is already associated with a member.', 'error')
                    return redirect(url_for('family.edit_child', depo_id=register.id, edit_id=spouse.id, child_id=child.id))

            # Check for duplicate email
            if email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user and (not child.user_id or existing_user.id != child.user_id):
                    flash('This email is already associated with an account.', 'error')
                    return redirect(url_for('family.edit_child', depo_id=register.id, edit_id=spouse.id, child_id=child.id))
                existing_member = Member.query.filter_by(email=email).first()
                if existing_member and existing_member.id != register.id:
                    flash('This email is already associated with a member.', 'error')
                    return redirect(url_for('family.edit_child', depo_id=register.id, edit_id=spouse.id, child_id=child.id))

            child.firstname = firstname
            child.lastname = lastname
            child.surname = surname
            child.phone_num = phone_num
            child.email = email
            child.id_number = id_number
            child.date_of_birth = date_of_birth

            # Update or create User account for the child
            if email:
                password_value = str(id_number) if id_number else str(child.id)
                if child.user_id:
                    existing_user = User.query.get(child.user_id)
                    if existing_user:
                        existing_user.surname = surname
                        existing_user.first_name = firstname
                        existing_user.email = email
                        existing_user.phone_num = phone_num
                        existing_user.role = AccessLevel.USER
                else:
                    new_user = User(
                        surname=surname,
                        first_name=firstname,
                        email=email,
                        phone_num=phone_num,
                        passwords=password_value,
                        role=AccessLevel.USER
                    )
                    db.session.add(new_user)
                    db.session.flush()
                    child.user_id = new_user.id

            db.session.add(child)
            db.session.commit()
            flash('Child updated successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update child. Please check your input and try again.', 'error')
            return redirect(url_for('family.edit_child', depo_id=register.id, edit_id=spouse.id, child_id=child.id))
    return render_template('register/edit.html', register = child, family = register)

@bp.route('/<int:depo_id>/<int:child_id>/edit_child', methods=('POST','GET'))
@login_required
def editchild(depo_id, child_id):
    register = Member.query.get_or_404(depo_id)
    child = Child.query.get_or_404(child_id)
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            surname = request.form['surname']
            phone_num = request.form.get('phone_num', '').strip()
            email = request.form.get('email', '').strip()
            raw_id = request.form.get('id_number', '').strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()

            child.firstname = firstname
            child.lastname = lastname
            child.surname = surname
            child.phone_num = phone_num
            child.email = email
            child.id_number = id_number
            child.date_of_birth = date_of_birth

            # Update or create User account for the child
            if email:
                password_value = str(id_number) if id_number else str(child.id)
                if child.user_id:
                    existing_user = User.query.get(child.user_id)
                    if existing_user:
                        existing_user.surname = surname
                        existing_user.first_name = firstname
                        existing_user.email = email
                        existing_user.phone_num = phone_num
                        existing_user.role = AccessLevel.USER
                else:
                    new_user = User(
                        surname=surname,
                        first_name=firstname,
                        email=email,
                        phone_num=phone_num,
                        passwords=password_value,
                        role=AccessLevel.USER
                    )
                    db.session.add(new_user)
                    db.session.flush()
                    child.user_id = new_user.id

            db.session.add(child)
            db.session.commit()
            flash('Child updated successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update child. Please check your input and try again.', 'error')
            return redirect(url_for('family.editchild', depo_id=register.id, child_id=child.id))
    return render_template('register/edit.html', register = child, family = register)

@bp.post('/<int:depo_id>/<int:child_id>/delete_child')
@login_required
def delete_child(depo_id, child_id):
    register = Member.query.get_or_404(depo_id)
    child = Child.query.get_or_404(child_id)
    db.session.delete(child)
    db.session.commit()
    return redirect(url_for('family.family', depo_id = register.id))

@bp.post('/<int:depo_id>/delete/')
@login_required
def delete_family(depo_id):
    register = Member.query.get_or_404(depo_id)
    for spouse in register.spouse:
        for child in spouse.child:
            db.session.delete(child)
        db.session.delete(spouse)
    
    db.session.commit()
    return redirect(url_for('family.index'))


@bp.post('/<int:depo_id>/delete_member/')
@login_required
def delete_member(depo_id):
    register = Member.query.get_or_404(depo_id)

    for contribution in register.contribute:
        db.session.delete(contribution)

    for spouse in register.spouse:
        if spouse.user_account:
            db.session.delete(spouse.user_account)
        for child in spouse.child:
            if child.user_account:
                db.session.delete(child.user_account)
            db.session.delete(child)
        db.session.delete(spouse)

    for child in register.child:
        if child.user_account:
            db.session.delete(child.user_account)
        db.session.delete(child)

    if register.user_account:
        db.session.delete(register.user_account)

    db.session.delete(register)
    db.session.commit()

    flash('Member and all associated records deleted successfully.', 'success')
    return redirect(url_for('family.index'))


# @bp.route('/<int:depo_id>/age')
# def date_of_b(depo_id):
#         deposit = Deposit.query.get_or_404(depo_id)
#         register = Member.query.get_or_404(depo_id)
#         today = date.today()
#         d3 = today.strftime("%m-%d-%y")
#         d4 = register.date_of_birth
#         # d4 = d_4.strftime(d_4"%m-%d-%Y")
#         # print("d3 =", d3)
#         age = d3.year - d4.year - ((today.month, today.day) < (d4.month, d4.day))
@bp.route('/birthday')
@login_required
def birthday():
    user = User.query.get_or_404(current_user.id)
    
    # Get all members added by the current user (or all for admin/dev roles)
    if user.role.name in ['DEVEL', 'ADMIN']:
        members = Member.query.options(
            joinedload(Member.user_account).subqueryload(User.image)
        ).order_by(Member.firstname).all()
    else:
        members = Member.query.filter_by(added_by=user.id).options(
            joinedload(Member.user_account).subqueryload(User.image)
        ).order_by(Member.firstname).all()
    
    # Build combined member list with age and birthday info
    birthday_data = []
    today = date.today()
    upcoming_birthdays = []
    
    for member in members:
        if member.date_of_birth:
            age = today.year - member.date_of_birth.year - (
                (today.month, today.day) < (member.date_of_birth.month, member.date_of_birth.day)
            )
            try:
                birthday_this_year = member.date_of_birth.replace(year=today.year)
            except ValueError:
                # Handle Feb 29th in non-leap years - move to March 1st
                birthday_this_year = member.date_of_birth.replace(year=today.year, day=1, month=3)
            if birthday_this_year < today:
                try:
                    birthday_this_year = member.date_of_birth.replace(year=today.year + 1)
                except ValueError:
                    birthday_this_year = member.date_of_birth.replace(year=today.year + 1, day=1, month=3)
            days_until = (birthday_this_year - today).days
            
            member_data = {
                'member': member,
                'age': age,
                'birthday': member.date_of_birth,
                'birthday_month': member.date_of_birth.month,
                'birthday_day': member.date_of_birth.day,
                'days_until': days_until,
                'is_today': days_until == 0,
                'is_upcoming': 0 < days_until <= 30,
                'initials': f"{member.firstname[0]}{member.lastname[0]}".upper() if member.firstname and member.lastname else '?',
            }
            birthday_data.append(member_data)
            
            if 0 <= days_until <= 30:
                upcoming_birthdays.append(member_data)
    
    # Sort by days until birthday
    birthday_data.sort(key=lambda x: x['days_until'])
    upcoming_birthdays.sort(key=lambda x: x['days_until'])
     # Separate members with and without DOB
    members_without_dob = [m for m in members if not m.date_of_birth]
    
    # Helper function to calculate birthday info
    def build_birthday_entry(person, person_type='member'):
        try:
            birthday_this_year = person.date_of_birth.replace(year=today.year)
        except ValueError:
            # Handle Feb 29th in non-leap years - move to March 1st
            birthday_this_year = date(today.year, 3, 1)
        if birthday_this_year < today:
            try:
                birthday_this_year = person.date_of_birth.replace(year=today.year + 1)
            except ValueError:
                birthday_this_year = date(today.year + 1, 3, 1)
        days_until = (birthday_this_year - today).days
        age = today.year - person.date_of_birth.year - (
            (today.month, today.day) < (person.date_of_birth.month, person.date_of_birth.day)
        )
        return {
            'birthday': person.date_of_birth,
            'birthday_month': person.date_of_birth.month,
            'birthday_day': person.date_of_birth.day,
            'days_until': days_until,
            'is_today': days_until == 0,
            'is_upcoming': 0 < days_until <= 30,
            'age': age,
        }
    
    # Build spouse birthday data
    spouse_birthday_data = []
    for member in members:
        for spouse in member.spouse:
            if spouse.date_of_birth:
                spouse_data = build_birthday_entry(spouse, 'spouse')
                spouse_data['spouse'] = spouse
                spouse_data['member'] = member
                spouse_data['initials'] = f"{spouse.firstname[0]}{spouse.lastname[0]}".upper() if spouse.firstname and spouse.lastname else '?'
                spouse_birthday_data.append(spouse_data)
    
    spouse_birthday_data.sort(key=lambda x: x['days_until'])
    
    # Build child birthday data
    child_birthday_data = []
    for member in members:
        # Direct children of member
        for child in member.child:
            if child.date_of_birth:
                child_data = build_birthday_entry(child, 'child')
                child_data['child'] = child
                child_data['member'] = member
                child_data['initials'] = f"{child.firstname[0]}{child.lastname[0]}".upper() if child.firstname and child.lastname else '?'
                child_birthday_data.append(child_data)
        # Children of spouses
        for spouse in member.spouse:
            for child in spouse.child:
                if child.date_of_birth:
                    child_data = build_birthday_entry(child, 'child')
                    child_data['child'] = child
                    child_data['member'] = member
                    child_data['initials'] = f"{child.firstname[0]}{child.lastname[0]}".upper() if child.firstname and child.lastname else '?'
                    child_birthday_data.append(child_data)
    
    child_birthday_data.sort(key=lambda x: x['days_until'])

    return render_template(
        "family/birthday.html",
        member=birthday_data,
        upcoming_birthdays=upcoming_birthdays,
        members_without_dob=members_without_dob,
        spouse_birthday=spouse_birthday_data,
        child_birthday=child_birthday_data,
        today=today
    )