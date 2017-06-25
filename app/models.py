from app import db
from werkzeug import generate_password_hash, check_password_hash
import os
from app import page
from app import whooshee

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    pwdhash = db.Column(db.String(54))
    interests = db.Column(db.String(200), index=True)
    activation_status = db.Column(db.Boolean, index=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    flwrs = db.Column(db.Integer, index=True)
    tokens = db.Column(db.Text)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')
    
    def __init__(self, nickname, email, password):
        self.nickname = nickname
        self.email = email.lower()
        self.set_password(password)
        self.activation_status = False
        self.flwrs = -1
        self.interests = ''

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            user.flwrs = user.flwrs + 1
            db.session.commit()
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            user.flwrs = user.flwrs - 1
            db.session.commit()
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def has_liked(self, post_id):
        res = Like.query.filter_by(post_id = post_id).all()
        for r in res:
            if r.user_id == self.id:
                return True
        return False

    def has_bookmarked(self, post_id):
        res = Bookmark.query.filter_by(post_id = post_id).all()
        for r in res:
            if r.user_id == self.id:
                return True
        return False

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def make_dirs(self):
        os.makedirs('/home/Manan/Programs/EduTech/app/static/userdata/'+str(self.nickname), exist_ok=True)

    def avatar(self):
        for root, dirs, files in os.walk("/home/manan/Programs/EduTech/app/static/userdata/" + str(self.nickname)):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".png"):
                    return "/static/userdata/" + str(self.nickname) + '/' + str(file)
        return "/static/userdata/avatar.png"

    def __repr__(self):
       return '<User %s, Email %s, Activation %s>' %(self.nickname, self.email, self.activation_status) 

@whooshee.register_model('title', 'body')
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(140))
    link = db.Column(db.String(140))
    image = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    likes = db.Column(db.Integer)
    category = db.Column(db.String(140)) 
    sub_category = db.Column(db.String(140))
    types = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '%s' %(self.title)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return '%s, %s' %(self.post_id, self.user_id)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer)
    post_id = db.Column(db.Integer)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id

    def __repr__(self):
        return '%s, %s' %(self.post_id, self.user_id)
    
    
class Categ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500)) 
    name =  db.Column(db.String(300))
    

    

    

   
