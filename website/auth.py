from flask import Blueprint,render_template,redirect,url_for,request,flash,session
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from .__init__ import app

auth=Blueprint("auth",__name__)

@auth.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        user=User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,password):
                flash("Logged in!", category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.dashboard'))
            else:
                flash("Incorrect Password!",category='error')
        else:
            flash("Email does not exists.", category='error')
    return  render_template("login.html",user=current_user)

@auth.route("/sign-up",methods=["GET","POST"])

def sign_up():
    if request.method == "POST":
        email=request.form.get("email")
        username=request.form.get("username")
        password1=request.form.get("password1")
        password2=request.form.get("password2")
        
        email_exists=User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()
        
        if email_exists:
            flash('Email is already in Use.', category='error')
        elif username_exists:
            flash('Username is already Taken. Please use another', category='error')
        elif password1 != password2:
            flash('Passwords do not match!', category='error')
        elif len(username) < 2:
            flash('Username is too short!!', category='error')
        elif len(password1) < 6:
            flash('Password is too short!', category='error')
        elif len(email) < 4:
            flash('Invalid email',category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password1,method='sha256'))
            
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user,remember=True)
            flash("User Created")
            return redirect(url_for('views.dashboard'))
        
    return render_template("signup.html", user=current_user)

@auth.route("/edit_detail/<int:id>/",methods=["GET","POST"])
@login_required
def edit(id):
    user=User.query.filter_by(id=id).one()
    if(request.method=="GET"):
        return render_template('edit_detail.html', user=current_user)
    else:
        if request.method=="POST":
            user.username=request.form.get("username")
            user.email=request.form.get("email")
            # db.session.add("post")
            db.session.commit()
    return redirect(url_for("views.home"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return  redirect(url_for("views.home"))
