from flask import Flask, request, redirect, Response
from flask_migrate import Migrate
from flask_basicauth import BasicAuth
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from src.models import db
from src.admin import setup_admin
from src.routes import api
from flask_jwt_extended import JWTManager


import os

load_dotenv()

app = Flask(__name__)

app.register_blueprint(api, url_prefix='/v1')

app.url_map.strict_slashes = False

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY") 
jwt = JWTManager(app)

# database condiguration
db_url = os.getenv("DB_URI")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db, compare_type=True)
db.init_app(app)

setup_admin(app)


app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True

@app.route("/")
def redirect_to_main():
    return redirect("/v1/hello", code=302)


@app.before_request
def restrict_admin_to_basic_auth():
    if request.path.startswith('/admin'):
        auth = request.authorization
        if not auth or not (auth.username == os.getenv("BA_USERNAME") and auth.password == os.getenv("BA_PASSWORD")):
            return Response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
