from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flaskwebgui import FlaskUI
from flask_migrate import Migrate
import os
import sys
from datetime import datetime

PEOPLE_FOLDER = os.path.join('static', 'photos')
EVENTS_FOLDER = os.path.join('static', 'photos', 'events')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy()
bootstrap = Bootstrap()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
    
    # app.config["SERVER_NAME"] = 'localhost'
    app.config['SECRET_KEY'] = 'secret_key_goes_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gamerock_user:gamerock_password@localhost/gamerock'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    #app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:secret123@localhost/gamerock"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['DEBUG'] = True
    app.config['USE_RELOADER'] = False

    @app.after_request
    def set_no_cache(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    ui = FlaskUI(app, width=800, height=1000)
    db.init_app(app)
    migrate.init_app(app, db)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.index'
    login_manager.init_app(app)
    bootstrap.init_app(app)
        
    from .user import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    #blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    #Register blueprint here
    from app.home import bp as home_dp
    app.register_blueprint(home_dp)
    
    from app.account import bp as account_bp
    app.register_blueprint(account_bp, url_prefix='/account')

    from app.register import bp as register_bp
    app.register_blueprint(register_bp, url_prefix='/register')

    from app.community import bp as questions_bp
    app.register_blueprint(questions_bp, url_prefix='/community')

    from app.deposit import bp as contribute_bp
    app.register_blueprint(contribute_bp, url_prefix='/contribution')

    from app.family import bp as family_bp
    app.register_blueprint(family_bp, url_prefix='/family')

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    from app.models.register import Member
    from app.models.faq import FAQ
    from app.models.community_event import CommunityEvent
    from app.models.contribute import Contribution

    @app.context_processor
    def inject_global_variables():
        members = []
        faq_count = 0
        faq_categories = []
        pending_deposits_count = 0
        try:
            if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                if current_user.role.name in ['DEVEL', 'ADMIN']:
                    members = Member.query.order_by(Member.firstname).all()
                    try:
                        faq_count = FAQ.query.count()
                        faq_categories = [
                            row[0] for row in db.session.query(FAQ.category)
                            .filter(FAQ.category.isnot(None), FAQ.category != '')
                            .distinct().order_by(FAQ.category).all()
                        ]
                    except Exception:
                        db.session.rollback()
                        faq_count = 0
                        faq_categories = []
                    try:
                        events_needing_contributions = CommunityEvent.query.filter(
                            CommunityEvent.id.notin_(
                                db.session.query(Contribution.propose).distinct().where(Contribution.propose.isnot(None))
                            )
                        ).count()
                        pending_deposits_count = events_needing_contributions
                    except Exception:
                        db.session.rollback()
                        pending_deposits_count = 0
                elif current_user.member_profile:
                    try:
                        member_contribution_events = db.session.query(Contribution.propose).where(
                            Contribution.member_id == current_user.member_profile.id
                        ).distinct()
                        pending_deposits_count = CommunityEvent.query.filter(
                            CommunityEvent.id.notin_(member_contribution_events)
                        ).count()
                    except Exception:
                        db.session.rollback()
                        pending_deposits_count = 0
        except Exception:
            pending_deposits_count = 0
        return dict(
            all_members=members,
            now=datetime.now,
            faq_count=faq_count,
            faq_categories=faq_categories,
            pending_deposits_count=pending_deposits_count,
        )

    def mask_phone(value):
        if not value:
            return value
        s = str(value)
        if len(s) <= 6:
            return s
        return s[:3] + '****' + s[-3:]

    def mask_id(value):
        if not value:
            return value
        s = str(value)
        if len(s) <= 6:
            return s
        return s[:3] + '****' + s[-3:]

    def is_admin_or_dev():
        return hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

    @app.template_filter('mask_phone')
    def mask_phone_filter(value):
        return mask_phone(value)

    @app.template_filter('mask_id')
    def mask_id_filter(value):
        return mask_id(value)

    @app.template_filter('member_phone')
    def member_phone_filter(value):
        if is_admin_or_dev():
            return value
        return mask_phone(value)

    @app.template_filter('member_id')
    def member_id_filter(value):
        if is_admin_or_dev():
            return value
        return mask_id(value)

    return app
