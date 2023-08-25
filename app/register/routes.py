from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.deposit import bp
from app.register import bp
from app import db
from app.user import User
from app.models.deposit import Deposit
from app.models.register import Register
from app.models.wife import Wife
from app.models.child import Child
from app.models.contribute import Contribute

@bp.route('/')
@login_required
def index():
    user = User.query.get(current_user.id)
    # depo_id = deposit.id
    # register = Register.query.get_or_404(depo_id)

    return render_template('register/index.html', user = user)

@bp.route('/<int:depo_id>/')
@login_required
def deposit(depo_id):
    user = User.query.get(current_user.id)
    register = Register.query.get_or_404(depo_id)
    # depo_id = register.deposit.id
    
    return render_template('register/deposit.html', register = register)


@bp.route('/create', methods=('POST', 'GET'))
@login_required
def create():
    user = User.query.get_or_404(current_user.id)
    # cont = Contribute.query.get_or_404(current_user.id)

    if request.method == 'POST':
        
        register = Register(firstname=request.form['firstname'], lastname = request.form['lastname'], date_of_birth=request.form['date_of_birth'],id_number=request.form['id_number'], user = user)
        
        db.session.add_all([register])
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id= register.id))
    return render_template('register/create.html')

@bp.route('/<int:depo_id>/editname', methods=('POST', 'GET'))
def edit_name(depo_id):
    register = Register.query.get_or_404(depo_id)
    if request.method == 'POST':
        firstname=request.form['firstname']
        lastname=request.form['lastname']
        date_of_birth=request.form['date_of_birth']
        id_number=request.form['id_number']

        register.firstname = firstname
        register.lastname = lastname
        register.date_of_birth = date_of_birth
        register.id_number = id_number

        db.session.add(register)
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template('register/edit.html', register = register)

@bp.route('/<int:depo_id>/create_wife/', methods=('POST','GET'))
def create_wife(depo_id):
    register = Register.query.get_or_404(depo_id)
    if request.method == 'POST':
        # register = Register.query.get_or_404(depo_id)
        # wife = depo.family.id
        new_wife = Wife(firstname = request.form['firstname'], lastname = request.form['lastname'], date_of_birth = request.form['date_of_birth'], id_number=request.form['id_number'],register = register)
        db.session.add_all([new_wife])
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id = register.id))
    return render_template('register/create_wife.html', register=register)

@bp.route('/<int:depo_id>/create_child/', methods=('POST','GET'))
def create_child(depo_id):
    # depo = Deposit.query.get_or_404(depo_id)
    register = Register.query.get_or_404(depo_id)
    if request.method == 'POST':
        # register = Register.query.get_or_404(depo_id)
        # wife = depo.family.id
        new_child = Child(firstname = request.form['firstname'], lastname = request.form['lastname'], date_of_birth = request.form['date_of_birth'], child = register)
        db.session.add_all([new_child])
        db.session.commit()
        return redirect(url_for('register.deposit', depo_id = register.id))
    return render_template('register/create_child.html', register = register)

@bp.post('/<int:depo_id>/delete/')
def delete(depo_id):
    # depo = User.query.get_or_404(current_user.id)
    register = Register.query.get_or_404(depo_id)
    for man in register:
        for deposit in register.depo_id:
            db.session.delete(deposit)
        for child in man.child:
            db.session.delete(child)
        for wife in man.wife:
            for child_ in wife.child:
                db.session.delete(child_)
            db.session.delete(wife)
    
    db.session.delete(man)
    db.session.commit()
    return redirect(url_for('register.index'))

@bp.route('/<int:depo_id>/edit', methods=('POST', 'GET'))
def edit(depo_id):
    register = Register.query.get_or_404(depo_id)
    depo = Deposit.query.filter_by(reg_id=depo_id).order_by(Deposit.id.desc()).first_or_404()
    if request.method == 'POST':
        depo.amount = request.form['amount']
        db.session.add(depo)
        db.session.commit()
        
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template("deposit/edit.html", register = register, deposit = depo)