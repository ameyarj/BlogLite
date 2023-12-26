import os
from unicodedata import category
from flask import Blueprint,render_template,request,flash,redirect,url_for,abort
from flask_login import login_required, current_user
from .models import Followers, Post,User,Comment,Like,Followers
from . import db
from .auth import login
from .__init__ import app
from sqlalchemy import or_



views=Blueprint("views",__name__)  #help to structure application by organizing the logic into subdirectories

@views.route("/")
@views.route("/home")
@login_required
def home():
    q = request.args.get('q')
    if q:
        posts = (db.session.query(Post).join(User, User.id == Post.author).filter(or_(User.username.contains(q), Post.text.contains(q))).all())
        if not posts:
            abort(404)
    else:
        posts = Post.query.order_by(Post.date_created.desc()).all()

    return  render_template("home.html", user=current_user,posts=posts)

@views.route("/dashboard")
@login_required
def dashboard():
    follower = User.query.filter(User.id.in_(follower.follower_id for follower in current_user.follower)).all()
    followed=User.query.filter(User.id.in_(followed.followed_id for followed in current_user.followed)).all()
    followed_count =current_user.followed.count()
    follower_count =current_user.follower.count()
    posts=current_user.posts
    likes = Like.query.filter(Like.post_id.in_([p.id for p in current_user.posts])).filter(Like.author == current_user.id).count()

    return  render_template("dashboard.html", user=current_user,followed_count=followed_count,follower_count=follower_count,posts=posts,follower=follower,post=Post,followed=followed,likes=likes)


@views.route("/create-post", methods=["GET","POST"])
@login_required
def create_post():
    if request.method=="POST":
        text=request.form.get('text')
        if not text:
            flash("Post cannot be empty!", category="error")
        else:
            post=Post(text=text,author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Post Created!",category="success")
            return redirect(url_for('views.home'))
    return render_template("create_post.html",user=current_user)   

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post=Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist!", category="error")
    elif current_user.id != post.user.id:
        flash("You can not delete this post!", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted!", category="success")
    return redirect(url_for("views.home"))

@views.route("/posts/<username>")
@login_required
def posts(username):
    user=User.query.filter_by(username=username).first()
    if not user:
        flash("User does not exists.", category="error")
        return redirect(url_for("views.home"))
    posts=user.posts
    return render_template("posts.html", user=current_user, posts=posts,username=username)

@views.route("/create-comment/<post_id>",methods=["POST"])
@login_required
def create_comment(post_id):
    text=request.form.get('text')

    if not text:
        flash("Comment cannot be empty!", category="error")
    else:
        post=Post.query.filter_by(id=post_id)
        if post:
            comment=Comment(text=text, author=current_user.id,post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash("Post do not exist.", category="error")
    return redirect(url_for("views.home"))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment=Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash("comment does'nt exists!", category="error")
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash("You don't have permission to delete!", category="error")
    else:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for("views.home"))

@views.route("/like-post/<post_id>",methods=["GET"])
@login_required
def like(post_id):
    post=Post.query.filter_by(id=post_id).first()
    like=Like.query.filter_by(author=current_user.id,post_id=post_id).first()
    if not post:
        flash("Post does'nt exists!", category="error")
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like=Like(author=current_user.id,post_id=post_id)
        db.session.add(like)
        db.session.commit()
    return redirect(url_for("views.home"))

@views.route("/follow/<int:user_id>",methods=["GET","POST"])
@login_required
def follow(user_id):

    if current_user.is_following(user_id):
        current_user.unfollow(user_id)
        flash("Unfollowed user!", category="success")
    else:
        current_user.follow(user_id)
        flash("Followed user!", category="success")

    return redirect(url_for("views.home"))


@views.route("/edit/<int:id>/",methods=["GET","POST"])
@login_required
def edit(id):
    post=Post.query.filter_by(id=id).one()
    if current_user.id != post.user.id:
        flash("You can not edit this post!", category="error")
    elif(request.method=="GET"):
        return render_template('edit_post.html',Post=post, user=current_user)
    else:
        if request.method=="POST":
            post.text=request.form.get("text")
            # db.session.add("post")
            db.session.commit()
    return redirect(url_for("views.home"))
    
@views.errorhandler(404)
def user_not_found(e):
    return render_template("404.html",user=current_user), 404
views.errorhandler(404)(user_not_found)
# @views.errorhandler(500)
# def internal_error(e):
#     return render_template("500.html",user=current_user), 500
# views.errorhandler(404)(internal_error)