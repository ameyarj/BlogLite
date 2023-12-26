from re import A
from flask import Flask,render_template,redirect,url_for,request,flash,Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager,current_user


db=SQLAlchemy()
DB_NAME="database.db"
app=Flask(__name__)
def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY']="Bello" # to encrypt session data
    app.config["SQLALCHEMY_DATABASE_URI"]= f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    db.init_app(app) #initializing the database with flask application


    from .views import views
    from .auth import auth
    

    app.register_blueprint(views,url_prefix="/")
    app.register_blueprint(auth,url_prefix="/") 

    from .models import User,Post,Comment,Like
        
    create_database(app)

    login_manager=LoginManager()  
    login_manager.login_view ='auth.login' # when anyone who is not logged in tries to get to a page it will redirect them to login page

    login_manager.init_app(app)

    @login_manager.user_loader #This sets the callback for reloading a user from the session. The function set takes a user ID (a str) and return a user object, or None if the user does not exist.
    
    def load_user(id):
        return User.query.get(int(id))
    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app = app)
        print("Created Database")
    