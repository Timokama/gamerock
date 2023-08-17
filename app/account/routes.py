from flask import render_template, request, redirect, url_for
from app.account import bp
from flask_login import login_required, current_user
from app import db
from app.user import User
from app.models.contribute import Contribute

@bp.route('/')
@login_required
def index():
    user = User.query.get_or_404(current_user.id)
    return render_template("contribute/index.html", user = user)

@bp.route('/create_account/', methods=('GET', 'POST'))
def cont():
    user = User.query.get_or_404(current_user.id)
    if request.method == 'POST':
        cont = Contribute(name=request.form['name'], user=user)

        db.session.add(cont)
        db.session.commit()
        return redirect(url_for('register.index'))

    return render_template('contribute/post.html', user = user)


@bp.route('/contribute/<tag_name>/')
def contribute(tag_name):
    user = User.query.get_or_404(current_user.id)
    register = user.family
    
    contribute = Contribute.query.filter_by(name=tag_name).order_by(Contribute.id.desc()).first_or_404()

    return render_template('contribute/tag.html', contribute = contribute, user = user, register = register)


@bp.post('/<int:depo_id>/delete')
def delete(depo_id):
    user = User.query.get_or_404(current_user.id)
    contribute = Contribute.query.get_or_404(depo_id)
    for cont in contribute.deposit:
        db.session.delete(cont)
    db.session.delete(contribute)
    db.session.commit()
    return redirect(url_for('account.index'))