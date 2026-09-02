import os
from flaskwebgui import FlaskUI
from app import create_app
from app import db
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    FlaskUI(
        app=app,
        server="flask",
        port=port,
        server_kwargs={"app": app, "host": host, "port": port},
        width=1024,
        height=768,
        fullscreen=False,
    ).run()