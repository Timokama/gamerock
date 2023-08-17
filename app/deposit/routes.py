from flask import render_template, request, redirect, url_for,flash
from app.deposit import bp
from flask_login import login_required, current_user
from app import db
from app.user import User
from app.models.register import Register
from app.models.deposit import Deposit
from app.models.wife import Wife
from app.models.child import Child
from app.models.contribute import Contribute

@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    register = user.family
    return render_template("deposit/index.html", user = user, register = register)

@bp.route('/<int:depo_id>/')
def deposit(depo_id):
    # depo = Deposit.query.get_or_404(depo_id)
    register = Register.query.get_or_404(depo_id)
    # depo_id = register.deposit.id
    deposit = register.depo_id
        

    total = 0
    for acc in register.depo_id:
        total += acc.amount
    
    return render_template('deposit/deposit.html', register = register, total = total, deposit = deposit)

@bp.route('/<int:depo_id>/amount', methods=('POST', 'GET'))
def amount(depo_id):
    user = User.query.get_or_404(current_user.id)
    register = Register.query.get_or_404(depo_id)
    if request.method == 'POST':
        amount = Deposit(amount  = request.form['amount'], register = register)        

        name = request.form.get('name')
        contribute = Contribute.query.get_or_404(name)
        if name:
            amount.contribute.append(contribute)
            register.contribute.append(contribute)
        db.session.add_all([amount])
        db.session.commit()
        
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template("deposit/amount.html", register = register, user = user)

