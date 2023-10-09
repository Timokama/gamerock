from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.deposit import bp
from app.register import bp
from app import db
from app.user import User
# from app.models.deposit import Deposit
from app.models.community_event import CommunityEvent
from app.models.register import Member
from app.models.wife import Wife
from app.models.child import Child
from app.models.contribute import Contribution

@bp.route('/')
@login_required
def index():
    user = User.query.get(current_user.id)
    # depo_id = deposit.id
    # register = Member.query.all()

    return render_template('register/index.html', user = user)

@bp.route('/<int:depo_id>/')
@login_required
def deposit(depo_id):
    user = User.query.get(current_user.id)
    register = Member.query.get_or_404(depo_id)
    # depo_id = register.deposit.id
    
    return render_template('register/deposit.html', register = register)


@bp.route('/create', methods=('POST', 'GET'))
@login_required
def create():
    user = User.query.get_or_404(current_user.id)
    # cont = Contribute.query.get_or_404(current_user.id)

    if request.method == 'POST':
        
        register = Member(firstname=request.form['firstname'], lastname = request.form['lastname'],surname = request.form['surname'], date_of_birth=request.form['date_of_birth'],id_number=request.form['id_number'], phone_num = request.form['phone_num'],user = user)
        reg = Member.query.filter_by(id_number=register.id_number).first()
        if reg:
            flash("Duplicate Id, Kindly check your details")
            return redirect(url_for('register.create'))

        db.session.add_all([register])
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id= register.id))
    return render_template('register/create.html')

@bp.route('/<int:depo_id>/editname', methods=('POST', 'GET'))
def edit_name(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        surname = request.form['surname']
        date_of_birth=request.form['date_of_birth']
        phone_num=request.form['phone_num']
        id_number=request.form['id_number']

        register.firstname = firstname
        register.lastname = lastname
        register.surname = surname
        register.phone_num = phone_num
        register.date_of_birth = date_of_birth
        register.id_number = id_number

        db.session.add(register)
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template('register/edit.html', register = register, family = register)

@bp.route('/<int:depo_id>/create_wife/', methods=('POST','GET'))
def create_wife(depo_id):
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        # register = Register.query.get_or_404(depo_id)
        # wife = depo.family.id
        new_wife = Wife(firstname = request.form['firstname'], lastname = request.form['lastname'], surname = request.form['surname'], phone_num = request.form['phone_num'], date_of_birth = request.form['date_of_birth'], id_number=request.form['id_number'],member = register)
        db.session.add(new_wife)
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id = register.id))
    return render_template('register/create.html', register=register)

@bp.route('/<int:depo_id>/create_child/', methods=('POST','GET'))
def create_child(depo_id):
    # depo = Deposit.query.get_or_404(depo_id)
    register = Member.query.get_or_404(depo_id)
    if request.method == 'POST':
        # register = Register.query.get_or_404(depo_id)
        # wife = depo.family.id
        new_child = Child(firstname = request.form['firstname'], lastname = request.form['lastname'], surname = request.form['surname'], phone_num = request.form['phone_num'], date_of_birth = request.form['date_of_birth'], id_number=request.form['id_number'],member = register)
        db.session.add_all([new_child])
        db.session.commit()
        return redirect(url_for('family.family', depo_id = register.id))
    return render_template('register/create.html', register = register)

@bp.post('/<int:depo_id>/delete/')
def delete(depo_id):
    # depo = User.query.get_or_404(current_user.id)
    register = Member.query.get_or_404(depo_id)
    
    for deposit in register.contribute:
        db.session.delete(deposit)
    for child in register.child:
        db.session.delete(child)
    for wife in register.wife:
        for child_ in wife.child:
            db.session.delete(child_)
        db.session.delete(wife)
    
    db.session.delete(register)
    db.session.commit()
    return redirect(url_for('register.index'))

@bp.route('/<int:depo_id>/edit', methods=('POST', 'GET'))
def edit(depo_id):
    register = Member.query.get_or_404(depo_id)
    depo = Contribution.query.filter_by(member_id=depo_id).order_by(Contribution.id.desc()).first()

    if not depo:
        flash("Error! Please deposit before Edit.")
        return redirect(url_for('register.deposit', depo_id=register.id))

    if request.method == 'POST':
        depo.amount = request.form['amount']
        db.session.add(depo)
        db.session.commit()
        
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template("deposit/edit.html", register = register, deposit = depo)