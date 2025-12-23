from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='../static')

    app.secret_key = 'key'

    from app.routes import main
    app.register_blueprint(main)

    return app