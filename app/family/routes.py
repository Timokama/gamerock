from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError
from app.family import bp
from app import db
from app.user import User
from app.level import AccessLevel
from app.models.register import Member
from app.models.community_event import CommunityEvent
from app.models.child import Child
from app.models.spouse import Spouse
from datetime import date

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
        return render_template("family/index.html", members=members)
    return render_template("family/index.html", user=user, member=member)


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
            new_spouse = Spouse(
                firstname=request.form['firstname'],
                lastname=request.form['lastname'],
                surname=request.form['surname'],
                phone_num=request.form['phone_num'],
                date_of_birth=date_of_birth,
                id_number=request.form['id_number'],
                member=register
            )
            db.session.add(new_spouse)
            db.session.commit()
            flash('Spouse added successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add spouse. Please check your input and try again.', 'error')
            return redirect(url_for('family.create_spouse', depo_id=register.id))
    return render_template('register/create.html', register=register)

@bp.route('/<int:depo_id>/<int:spouse_id>/create_child', methods=('POST', 'GET'))
@login_required
def create_child(depo_id, spouse_id):
    register = Member.query.get_or_404(depo_id)
    spouse = Spouse.query.get_or_404(spouse_id)
    if request.method == 'POST':
        try:
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            child = Child(
                firstname=request.form['firstname'],
                lastname=request.form['lastname'],
                surname=request.form['surname'],
                phone_num=request.form['phone_num'],
                id_number=request.form['id_number'],
                email=request.form['email'],
                date_of_birth=date_of_birth,
                spouse=spouse
            )
            db.session.add(child)
            db.session.commit()
            flash('Child added successfully!', 'success')
            return redirect(url_for('family.family', depo_id=register.id))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add child. Please check your input and try again.', 'error')
            return redirect(url_for('family.create_child', depo_id=register.id, spouse_id=spouse.id))
    return render_template('register/create.html', register=register, spouse=spouse)

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
            phone_num = request.form['phone_num']
            raw_id = request.form['id_number'].strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            
            spouse.firstname = firstname
            spouse.lastname = lastname
            spouse.surname = surname
            spouse.phone_num = phone_num
            spouse.id_number = id_number
            spouse.date_of_birth = date_of_birth

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
            phone_num = request.form['phone_num']
            email = request.form['email']
            raw_id = request.form['id_number'].strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            
            child.firstname = firstname
            child.lastname = lastname
            child.surname = surname
            child.phone_num = phone_num
            child.email = email
            child.id_number = id_number
            child.date_of_birth = date_of_birth

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
            phone_num = request.form['phone_num']
            email = request.form['email']
            raw_id = request.form['id_number'].strip()
            id_number = int(raw_id) if raw_id and raw_id.lower() != 'none' else None
            date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d').date()
            
            child.firstname = firstname
            child.lastname = lastname
            child.surname = surname
            child.phone_num = phone_num
            child.email = email
            child.id_number = id_number
            child.date_of_birth = date_of_birth

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
def contact():
    user = User.query.get_or_404(current_user.id)
    member = user.family
    age_list = []
    if member:
        for birthday in member:
            today = date.today()
            age = today.year - birthday.date_of_birth.year - ((today.month, today.day) < (birthday.date_of_birth.month, birthday.date_of_birth.day))
            age_list.append(age)


#    return render_template('contact.html', member = member, age = age_list)
    return render_template("family/birthday.html", member = member, age=age_list)
