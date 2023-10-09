from flask import render_template, request, redirect, url_for,flash
from app.deposit import bp
from flask_login import login_required, current_user
from app import db
from app.user import User
from app.models.register import Member
# from app.models.deposit import Deposit
from app.models.community_event import CommunityEvent
from app.models.wife import Wife
from app.models.child import Child
from app.models.contribute import Contribution
from app.models.payments import Payment
@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    register = user.family
    return render_template("deposit/index.html", user = user, register = register)

@bp.route('/<int:depo_id>/')
def deposit(depo_id):
    # depo = Deposit.query.get_or_404(depo_id)
    register = Member.query.get_or_404(depo_id)
    # depo_id = register.deposit.id
    deposit = register.contribute
        

    total = 0
    for acc in register.contribute:
        total += acc.amount
    
    return render_template('deposit/deposit.html', register = register, total = total, deposit = deposit)

@bp.route('/<int:depo_id>/amount', methods=('POST', 'GET'))
def amount(depo_id):
    user = User.query.get_or_404(current_user.id)
    level = Payment
    register = Member.query.get_or_404(depo_id)

    if request.method == 'POST':
        amount = Contribution(amount = request.form['amount'], payment_type = request.form['payment'], transaction_ref=request.form['transaction_ref'], propose = request.form.get('propose'), member = register, user = user)        
        
        community = CommunityEvent.query.filter_by(id = amount.propose).first()
        if not community:
            flash("Error, Select Community Event!")
            return redirect(url_for('deposit.amount', depo_id=register.id))
        # propose = amount.propose
        # if community:
        #     # amount.propose.append(community)
            # event.register.append(community)
        db.session.add(amount)
        db.session.commit()
        
        return redirect(url_for('register.deposit', depo_id=register.id))
    return render_template("deposit/amount.html", register = register, user = user, level = level)

