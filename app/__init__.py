from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_ngrok import run_with_ngrok
import os
import sys
def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass

db = SQLAlchemy()
bootstarp = Bootstrap()

def create_app():
    app = Flask(__name__)
    # Initialize our ngrok settings into Flask
    app.config.from_mapping(
        BASE_URL="http://localhost:5000",
        USE_NGROK=os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("WERKZEUG_RUN_MAIN") != "true"
    )

    if app.config.get("ENV") == "development" and app.config["USE_NGROK"]:
        # pyngrok will only be installed, and should only ever be initialized, in a dev environment
        from pyngrok import ngrok

        # Get the dev server port defaults to 5000 for Flask, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        app.config["BASE_URL"] = public_url
        init_webhooks(public_url)

    app.config['SECRET_KEY'] = 'secret_key_goes_here'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/gamerock'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    bootstarp.init_app(app)
        
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

    from app.deposit import bp as questions_bp
    app.register_blueprint(questions_bp, url_prefix='/deposit')

    from app.family import bp as family_bp
    app.register_blueprint(family_bp, url_prefix='/family')

    from app.reports import bp as reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')

    return app
