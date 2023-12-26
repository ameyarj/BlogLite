from . import db
from flask_login import UserMixin,current_user
from sqlalchemy.sql import func



class Followers(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date_created=db.Column(db.DateTime(timezone=True), default=func.now())
    follower_id=db.Column(db.Integer,db.ForeignKey("user.id", ondelete='CASCADE'),nullable=False)
    followed_id=db.Column(db.Integer,db.ForeignKey("user.id", ondelete='CASCADE'),nullable=False)

class Like(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    date_created=db.Column(db.DateTime(timezone=True), default=func.now())
    author=db.Column(db.Integer,db.ForeignKey("user.id", ondelete='CASCADE'),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id", ondelete='CASCADE'),nullable=False)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(150), unique=True)
    username=db.Column(db.String(150), unique=True)
    password=db.Column(db.String(150))
    date_created=db.Column(db.DateTime(timezone=True), default=func.now())
    posts=db.relationship('Post',backref='user',passive_deletes=True)
    comments=db.relationship('Comment',backref='user',passive_deletes=True)
    followed=db.relationship('Followers',foreign_keys=[Followers.follower_id],backref=db.backref('follower', lazy='joined'),lazy='dynamic', cascade='all, delete-orphan')

    follower=db.relationship('Followers', foreign_keys=[Followers.followed_id],backref=db.backref('followed', lazy='joined'),lazy='dynamic', cascade='all, delete-orphan')


    post_liked=db.relationship("Like",backref='user',passive_deletes=True)

    def follow(self, user_id):
        if not self.is_following(user_id):
            follow = Followers(follower_id=self.id, followed_id=user_id)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user_id):
        if self.is_following(user_id):
            follow = Followers.query.filter_by(follower_id=self.id, followed_id=user_id).first()
            db.session.delete(follow)
        db.session.commit()


    def is_following(self, user_id):
        print(user_id)
        following=self.followed.filter(Followers.followed_id == user_id).first()
        if not following:
            return False
        else:
            return True
       
    
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.Text,nullable=False)
    date_created=db.Column(db.DateTime(timezone=True), default=func.now())
    author=db.Column(db.Integer,db.ForeignKey("user.id", ondelete='CASCADE'),nullable=False)
    comments=db.relationship('Comment',backref='post',passive_deletes=True)
    likes=db.relationship('Like',backref='post',passive_deletes=True)
    
class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    text=db.Column(db.String(70),nullable=False)
    date_created=db.Column(db.DateTime(timezone=True), default=func.now())
    author=db.Column(db.Integer,db.ForeignKey("user.id", ondelete='CASCADE'),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey("post.id", ondelete='CASCADE'),nullable=False)




