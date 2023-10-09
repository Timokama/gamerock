import os
from flaskwebgui import FlaskUI
from app import create_app
app = create_app()

ui = FlaskUI(app, width=500, height=500)
test_env=True

@app.route("/close", methods=["GET"])
def close_window():
    close_application()


def start_flask(**server_kwargs):
    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug",True)

    try:
        import waitress

        waitress.serve(app, **server_kwargs)
    except:
        app.run(**server_kwargs)


if __name__ == "__main__":
#     # app.run(debug=True)

#     # Default start flask
    port = int(os.environ.get("PORT", 5000))
    FlaskUI(
        app=app,
        port=port,
        server="flask",
        width=800,
        height=600,
        on_startup=lambda: print("helooo"),
        on_shutdown=lambda: print("byee"),
    ).run()
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))
#     app.run(debug=True,host='0.0.0.0', port=port)
# if test_env:
#         ui.run()
# else:
#         app.run
