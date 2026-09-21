import os
import logging
from app import create_app
from app import db

# The app instance is created at module level for WSGI compatibility
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))

    # On Render.com (or other WSGI server deployments), use standard Flask server
    # Locally (default), use FlaskUI for desktop GUI mode
    is_render = os.environ.get("RENDER") == "1" or os.environ.get("RENDER_ON_GUY") == "1"

    if is_render:
        # Standard Flask WSGI server (used by Render.com with gunicorn)
        app.run(host=host, port=port)
    else:
        from flaskwebgui import FlaskUI
        # Suppress FlaskWebGUI verbose "Task queue depth" warnings
        logging.getLogger('flaskwebgui').setLevel(logging.ERROR)
        FlaskUI(
            app=app,
            server="flask",
            port=port,
            server_kwargs={"app": app, "host": host, "port": port},
            width=1024,
            height=768,
            fullscreen=False,
        ).run()
