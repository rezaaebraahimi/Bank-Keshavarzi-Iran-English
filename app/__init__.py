from flask import Flask,render_template,request
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import os
from dotenv import load_dotenv


app=Flask(__name__)

load_dotenv()

app.config["SECRET_KEY"]= (os.environ.get("SECRET_KEY"))
app.config['SQLALCHEMY_DATABASE_URI']= (os.environ.get("SQLALCHEMY_DATABASE_URI"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
app.config['FAVICON'] = os.path.join(os.getcwd(), 'static', 'favicon.ico')

db=SQLAlchemy(app)
app.app_context().push()
Session(app)

from app.admin.views import admin_blueprint
from app.user.views import user_blueprint
from app.blog.views import blog_blueprint

app.register_blueprint(admin_blueprint, url_prefix='/admin')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(blog_blueprint, url_prefix='/blog')



@app.route('/')
def index():
    return render_template('index.html',title="")


@app.errorhandler(404)
def not_found(e):
    app.logger.error(f" NOT FOUND: {e}, --> route: {request.url}")
    return render_template("error/404.html")


@app.errorhandler(403)
def forbidden(e):
    app.logger.error(f"Forbidden Access: {e}, --> route: {request.url}")
    return render_template("error/403.html")

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server Error: {e}, --> route: {request.url}")
    return render_template("error/500.html")

