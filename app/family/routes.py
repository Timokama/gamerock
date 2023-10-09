from flask import render_template, request, redirect, url_for
# from app.register import bp
from flask_login import login_required, current_user
from datetime import date
from app.family import bp
from app import db
from app.user import User
from app.models.register import Member
# from app.models.deposit import Deposit
from app.models.community_event import CommunityEvent
from app.models.child import Child
from app.models.wife import Wife
from datetime import date

@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    return render_template("family/index.html", user = user)


@bp.route('/<int:depo_id>/')
def family(depo_id):
    register = Member.query.get_or_404(depo_id)
    return render_template('family/family.html', register = register)

@bp.route('/<int:depo_id>/edit', methods=('POST', 'GET'))
def edit(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        date_of_birth=request.form['date_of_birth']
        phone_num=request.form['phone_num']
        id_number=request.form['id_number']

        register.firstname = firstname
        register.lastname = lastname
        register.date_of_birth = date_of_birth
        register.contact = contact
        register.id_number = id_number

        db.session.add(register)
        db.session.commit()
        return redirect(url_for('family.family', depo_id=register.id))
    return render_template('register/edit.html', register = register, family = register)

@bp.route('/<int:depo_id>/create_wife', methods=('POST', 'GET'))
def create_wife(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        new_wife = Wife(firstname = request.form['firstname'], lastname = request.form['lastname'], surname = request.form['surname'], phone_num = request.form['phone_num'], date_of_birth = request.form['date_of_birth'], id_number=request.form['id_number'],member = register)
        db.session.add(new_wife)
        db.session.commit()
        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/create.html', register=register)

@bp.route('/<int:depo_id>/<int:wife_id>/create_child', methods=('POST', 'GET'))
def create_child(depo_id, wife_id):
    register = Member.query.get_or_404(depo_id)
    wife = Wife.query.get_or_404(wife_id)
    if request.method == 'POST':
        child = Child(
            firstname=request.form['firstname'],
            lastname=request.form['lastname'],
            surname=request.form['surname'],
            phone_num=request.form['phone_num'],
            id_number=request.form['id_number'],
            date_of_birth=request.form['date_of_birth'],
            wife = wife
        )
        db.session.add(child)
        db.session.commit()
        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/create.html', register=register, wife = wife)

@bp.post('/<int:depo_id>/<int:del_id>/delete')
def delete(depo_id, del_id):
    register = Member.query.get_or_404(depo_id)
    wife = Wife.query.get_or_404(del_id)
    for child in wife.child:
        db.session.delete(child)
    db.session.delete(wife)
    db.session.commit()
    return redirect(url_for('family.family', depo_id = register.id))

@bp.route('/<int:depo_id>/<int:edit_id>/edit_wife', methods=('POST','GET'))
def edit_wife(depo_id, edit_id):
    register = Member.query.get_or_404(depo_id)
    wife = Wife.query.get_or_404(edit_id)
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        surname = request.form['surname']
        phone_num = request.form['phone_num']
        id_number = request.form['id_number']
        date_of_birth = request.form['date_of_birth']
        
        wife.firstname = firstname
        wife.lastname = lastname
        wife.surname = surname
        wife.phone_num = phone_num
        wife.id_number = id_number
        wife.date_of_birth = date_of_birth

        db.session.add(wife)
        db.session.commit()

        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/edit.html', register = wife, family = register)

@bp.route('/<int:depo_id>/<int:edit_id>/<int:child_id>/edit_child', methods=('POST','GET'))
def edit_child(depo_id, edit_id, child_id):
    register = Member.query.get_or_404(depo_id)
    wife = Wife.query.get_or_404(edit_id)
    child = Child.query.get_or_404(child_id)
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        surname = request.form['surname']
        phone_num = request.form['phone_num']
        id_number = request.form['id_number']
        date_of_birth = request.form['date_of_birth']
        
        child.firstname = firstname
        child.lastname = lastname
        child.surname = surname
        child.phone_num = phone_num
        child.id_number = id_number
        child.date_of_birth = date_of_birth

        db.session.add(child)
        db.session.commit()

        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/edit.html', register = child, family = register)

@bp.route('/<int:depo_id>/<int:child_id>/edit_child', methods=('POST','GET'))
def editchild(depo_id, child_id):
    register = Member.query.get_or_404(depo_id)
    child = Child.query.get_or_404(child_id)
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        surname = request.form['surname']
        phone_num = request.form['phone_num']
        id_number = request.form['id_number']
        date_of_birth = request.form['date_of_birth']
        
        child.firstname = firstname
        child.lastname = lastname
        child.surname = surname
        child.phone_num = phone_num
        child.id_number = id_number
        child.date_of_birth = date_of_birth

        db.session.add(child)
        db.session.commit()

        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/edit.html', register = child, family = register)

@bp.post('/<int:depo_id>/delete/')
def delete_family(depo_id):
    depo = Deposit.query.get_or_404(depo_id)
    register = Member.query.get_or_404(depo_id)
    for man in depo.family:
        for child in man.child:
            db.session.delete(child)
    for wife in man.wife:
        for child_ in wife.child:
            db.session.delete(child_)
        db.session.delete(wife)
    
    db.session.delete(man)
    db.session.delete(depo)
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
    if member:
        age_list = []
        for birthday in member:
            today = date.today()
            age = today.year - birthday.date_of_birth.year - ((today.month, today.day) < (birthday.date_of_birth.month, birthday.date_of_birth.day))
            age_list.append(age)


#    return render_template('contact.html', member = member, age = age_list)
    return render_template("family/birthday.html", member = member, register = register, age=age)
