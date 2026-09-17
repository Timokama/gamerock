from flask import Flask, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flaskwebgui import FlaskUI
import os
import sys
import logging
from datetime import datetime

PEOPLE_FOLDER = os.path.join('static', 'photos')
EVENTS_FOLDER = os.path.join('static', 'photos', 'events')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Suppress verbose Flask/Jinja2/Werkzeug INFO logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('jinja2').setLevel(logging.WARNING)
logging.getLogger('flask').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
logging.getLogger('alembic').setLevel(logging.WARNING)

db = SQLAlchemy()
bootstrap = Bootstrap()

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
    
    # app.config["SERVER_NAME"] = 'localhost'
    app.config['SECRET_KEY'] = 'secret_key_goes_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gamerock_user:gamerock_password@localhost/gamerock'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    #app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:secret123@localhost/gamerock"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = False
    app.config['USE_RELOADER'] = False
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['DEBUG'] = False
    app.config['EXPLAIN_TEMPLATE_LOADING'] = False

    app.jinja_env.auto_reload = False
    app.jinja_env.cache = {}
    app.jinja_env.autoescape = True

    app.logger.setLevel(logging.WARNING)

    @app.after_request
    def set_no_cache(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    db.init_app(app)

    from sqlalchemy import inspect as sqlinspect
    with app.app_context():
        inspector = sqlinspect(db.engine)
        user_columns = [c['name'] for c in inspector.get_columns('user')]
        if 'status' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE \"user\" ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'pending'"))
                conn.commit()
        if 'created_at' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE \"user\" ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
        if 'phone_num' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE \"user\" ADD COLUMN phone_num VARCHAR(20)"))
                conn.commit()
        if 'id_number' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE \"user\" ADD COLUMN id_number INTEGER"))
                conn.commit()
        if 'date_of_birth' not in user_columns:
            with db.engine.connect() as conn:
                conn.execute(db.text("ALTER TABLE \"user\" ADD COLUMN date_of_birth DATE"))
                conn.commit()
        with db.engine.connect() as conn:
            id_number_constraint = inspector.get_unique_constraints('user')
            has_id_number_unique = any(
                'id_number' in (c['column_names'] if isinstance(c['column_names'], list) else [c['column_names']])
                for c in id_number_constraint
            )
            if not has_id_number_unique:
                try:
                    conn.execute(db.text("ALTER TABLE \"user\" ADD CONSTRAINT \"user_id_number_key\" UNIQUE (\"id_number\")"))
                    conn.commit()
                except Exception:
                    pass
        with db.engine.connect() as conn:
            conn.execute(db.text("UPDATE \"user\" SET status = 'active' WHERE role IN ('Developer', 'Administrator', 'Chairperson', 'Welfare Officer', 'Treasurer', 'Secretary') AND status = 'pending'"))
            conn.commit()

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

    from app.budget import bp as budget_bp
    app.register_blueprint(budget_bp, url_prefix='/budget')

    from app.minutes import bp as minutes_bp
    app.register_blueprint(minutes_bp, url_prefix='/minutes')

    from app.treasurer import bp as treasurer_bp
    app.register_blueprint(treasurer_bp, url_prefix='/treasurer')

    from app.requisition import bp as requisition_bp
    app.register_blueprint(requisition_bp, url_prefix='/requisition')

    from app.sponsor import bp as sponsor_bp
    app.register_blueprint(sponsor_bp, url_prefix='/sponsor')

    from app.models.register import Member
    from app.models.faq import FAQ
    from app.models.community_event import CommunityEvent
    from app.models.contribute import Contribution
    from app.models.spouse import Spouse
    from app.models.child import Child

    @app.context_processor
    def inject_global_variables():
        members = []
        faq_count = 0
        faq_categories = []
        pending_deposits_count = 0
        pending_users_count = 0
        recent_updates = []
        is_viewing_family = False
        family_member_name = None
        primary_member_id = None
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
                        pending_users_count = User.query.filter(
                            ~db.exists().where(Member.user_id == User.id),
                            ~db.exists().where(Spouse.user_id == User.id),
                            ~db.exists().where(Child.user_id == User.id)
                        ).count()
                    except Exception:
                        db.session.rollback()
                        pending_deposits_count = 0
                    try:
                        recent_members = Member.query.order_by(Member.created_at.desc()).limit(5).all()
                        recent_contributions = Contribution.query.order_by(Contribution.trans_date.desc()).limit(5).all()
                        recent_events = CommunityEvent.query.order_by(CommunityEvent.created_at.desc()).limit(5).all()
                        recent_faqs = FAQ.query.order_by(FAQ.created_at.desc()).limit(5).all()
                        
                        for m in recent_members:
                            recent_updates.append({
                                'type': 'member',
                                'icon': '👤',
                                'text': f'<strong>{m.firstname} {m.lastname}</strong> joined',
                                'time': m.created_at.strftime('%b %d, %I:%M %p') if m.created_at else 'Unknown',
                                'timestamp': m.created_at,
                                'url': url_for('register.edit', depo_id=m.id)
                            })
                        
                        for c in recent_contributions:
                            member = c.member
                            member_name = f'{member.firstname} {member.lastname}' if member else 'Unknown'
                            recent_updates.append({
                                'type': 'contribution',
                                'icon': '💰',
                                'text': f'<strong>{member_name}</strong> contributed Ksh. {c.amount:,}',
                                'time': c.trans_date.strftime('%b %d, %I:%M %p') if c.trans_date else 'Unknown',
                                'timestamp': c.trans_date,
                                'url': url_for('deposit.deposit', depo_id=c.member_id) if member else '#'
                            })
                        
                        for e in recent_events:
                            recent_updates.append({
                                'type': 'event',
                                'icon': '🎉',
                                'text': f'Event <strong>{e.name}</strong> created',
                                'time': e.created_at.strftime('%b %d, %I:%M %p') if e.created_at else 'Unknown',
                                'timestamp': e.created_at,
                                'url': url_for('community.index')
                            })
                        
                        for f in recent_faqs:
                            recent_updates.append({
                                'type': 'faq',
                                'icon': '💬',
                                'text': f'FAQ: <strong>{f.question[:40]}...</strong>',
                                'time': f.created_at.strftime('%b %d, %I:%M %p') if f.created_at else 'Unknown',
                                'timestamp': f.created_at,
                                'url': url_for('register.faq_list')
                            })
                        
                        recent_updates.sort(key=lambda x: x.get('timestamp') or datetime(1900, 1, 1), reverse=True)
                        recent_updates = recent_updates[:8]
                    except Exception as e:
                        import traceback
                        traceback.print_exc()
                        db.session.rollback()
                        recent_updates = []
                elif current_user.member_profile:
                    try:
                        member = current_user.member_profile
                        spouse_link = Spouse.query.filter_by(user_id=current_user.id).first()
                        child_link = Child.query.filter_by(user_id=current_user.id).first()
                        
                        if spouse_link and spouse_link.member_id == member.id:
                            is_viewing_family = True
                            primary_member_id = spouse_link.member_id
                            family_member_name = f"{spouse_link.firstname} {spouse_link.lastname}"
                        elif child_link and child_link.member_id == member.id:
                            is_viewing_family = True
                            primary_member_id = child_link.member_id
                            family_member_name = f"{child_link.firstname} {child_link.lastname}"
                        
                        member_contribution_events = db.session.query(Contribution.propose).where(
                            Contribution.member_id == member.id
                        ).distinct()
                        pending_deposits_count = CommunityEvent.query.filter(
                            CommunityEvent.id.notin_(member_contribution_events)
                        ).count()
                    except Exception:
                        db.session.rollback()
                        pending_deposits_count = 0
                        is_viewing_family = False
                else:
                    try:
                        spouse_link = Spouse.query.filter_by(user_id=current_user.id).first()
                        child_link = Child.query.filter_by(user_id=current_user.id).first()
                        
                        if spouse_link and spouse_link.member_id:
                            is_viewing_family = True
                            primary_member_id = spouse_link.member_id
                            family_member_name = f"{spouse_link.firstname} {spouse_link.lastname}"
                        elif child_link and child_link.member_id:
                            is_viewing_family = True
                            primary_member_id = child_link.member_id
                            family_member_name = f"{child_link.firstname} {child_link.lastname}"
                        
                        if is_viewing_family:
                            member_contribution_events = db.session.query(Contribution.propose).where(
                                Contribution.member_id == primary_member_id
                            ).distinct()
                            pending_deposits_count = CommunityEvent.query.filter(
                                CommunityEvent.id.notin_(member_contribution_events)
                            ).count()
                    except Exception:
                        db.session.rollback()
                        pending_deposits_count = 0
                        is_viewing_family = False
        except Exception:
            pending_deposits_count = 0
            recent_updates = []
        
        return dict(
            all_members=members,
            now=datetime.now,
            faq_count=faq_count,
            faq_categories=faq_categories,
            pending_deposits_count=pending_deposits_count,
            pending_users_count=pending_users_count,
            recent_updates=recent_updates,
            is_viewing_family=is_viewing_family,
            family_member_name=family_member_name,
            family_primary_member_id=primary_member_id,
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

    @app.template_global()
    def is_admin_or_dev():
        return hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN']

    @app.template_global()
    def can_manage_minutes():
        return hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN', 'SECRETARY']

    @app.template_global()
    def can_manage_treasurer():
        return hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and current_user.role.name in ['DEVEL', 'ADMIN', 'TREASURER']

    @app.template_global()
    def can_manage_requisition():
        return (
            hasattr(current_user, 'is_authenticated')
            and current_user.is_authenticated
            and getattr(current_user, 'role', None) is not None
            and current_user.role.name in ['DEVEL', 'ADMIN', 'CHAIRPERSON']
        )

    @app.template_global()
    def access_level_global():
        from .level import AccessLevel
        return AccessLevel

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

    @app.template_global()
    def static_version(filename):
        import os
        filepath = os.path.join(app.root_path, 'static', filename.replace('/', os.sep))
        try:
            return f"{url_for('static', filename=filename)}?v={int(os.path.getmtime(filepath))}"
        except OSError:
            return url_for('static', filename=filename)

    @app.context_processor
    def inject_template_versions():
        import os
        version_map = {}
        template_names = ['admin_dashboard.html', 'tag.html']
        for name in template_names:
            filepath = os.path.join(app.root_path, 'templates', name)
            try:
                version_map[name] = int(os.path.getmtime(filepath))
            except OSError:
                version_map[name] = 0
        return {'template_versions': version_map}

    return app
