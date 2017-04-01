from flask import Flask


def make_application():
    import app.views

    flask_app = Flask(__name__, static_url_path='')

    flask_app.register_blueprint(app.views.blueprint_http)
    app.views.blueprint_http.config = flask_app.config

    return flask_app
