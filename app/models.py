# -*- coding: utf-8 -*-
"""
Created on 2016/6/1

@author: wb-zy184129
"""
from datetime import datetime
import hashlib

from flask import request, url_for
from . import db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager
from markdown import markdown
import bleach

from app.exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', postid=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', userid=self.author_id, _external=True),
            'comments': url_for('api.get_post_comments', postid=self.id, _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True
                     ),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.TEXT())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))

    ''' 查询用户写的文章,SQL:
    SELECT
        posts.id AS posts_id,
        posts.body AS posts_body,
        posts.body_html AS posts_body_html,
        posts.timestamp AS posts_timestamp,
        posts.author_id AS posts_author_id
    FROM
        posts
    WHERE
        posts.author_id = 2
    '''
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    """follower_id表示关注者， followed_id表示被关注者
        查询被关注者，select * from follows  LEFT JOIN users on follower_id = id where follower_id=2
    SELECT
        follows.follower_id AS follows_follower_id,
        follows.followed_id AS follows_followed_id,
        follows.timestamp AS follows_timestamp,
        users_1.id AS users_1_id,
        users_1.email AS users_1_email,
        users_1.username AS users_1_username,
        users_1.password_hash AS users_1_password_hash,
        users_1.confirmed AS users_1_confirmed,
        users_1.role_id AS users_1_role_id,
        users_1.name AS users_1_name,
        users_1.location AS users_1_location,
        users_1.about_me AS users_1_about_me,
        users_1.member_since AS users_1_member_since,
        users_1.last_seen AS users_1_last_seen,
        users_1.avatar_hash AS users_1_avatar_hash,
        users_2.id AS users_2_id,
        users_2.email AS users_2_email,
        users_2.username AS users_2_username,
        users_2.password_hash AS users_2_password_hash,
        users_2.confirmed AS users_2_confirmed,
        users_2.role_id AS users_2_role_id,
        users_2.name AS users_2_name,
        users_2.location AS users_2_location,
        users_2.about_me AS users_2_about_me,
        users_2.member_since AS users_2_member_since,
        users_2.last_seen AS users_2_last_seen,
        users_2.avatar_hash AS users_2_avatar_hash
    FROM
        follows
    LEFT OUTER JOIN users AS users_1 ON users_1.id = follows.follower_id
    LEFT OUTER JOIN users AS users_2 ON users_2.id = follows.followed_id
    WHERE
        follows.follower_id = 2;
    """
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    """ 查询关注者， select * from follows  LEFT JOIN users on followed_id = id where followed_id=3
        users_1：关注者表
        users_2：被关注者表
    SELECT
        follows.follower_id AS follows_follower_id,
        follows.followed_id AS follows_followed_id,
        follows.timestamp AS follows_timestamp,
        users_1.id AS users_1_id,
        users_1.email AS users_1_email,
        users_1.username AS users_1_username,
        users_1.password_hash AS users_1_password_hash,
        users_1.confirmed AS users_1_confirmed,
        users_1.role_id AS users_1_role_id,
        users_1.name AS users_1_name,
        users_1.location AS users_1_location,
        users_1.about_me AS users_1_about_me,
        users_1.member_since AS users_1_member_since,
        users_1.last_seen AS users_1_last_seen,
        users_1.avatar_hash AS users_1_avatar_hash,
        users_2.id AS users_2_id,
        users_2.email AS users_2_email,
        users_2.username AS users_2_username,
        users_2.password_hash AS users_2_password_hash,
        users_2.confirmed AS users_2_confirmed,
        users_2.role_id AS users_2_role_id,
        users_2.name AS users_2_name,
        users_2.location AS users_2_location,
        users_2.about_me AS users_2_about_me,
        users_2.member_since AS users_2_member_since,
        users_2.last_seen AS users_2_last_seen,
        users_2.avatar_hash AS users_2_avatar_hash
    FROM
        follows
    LEFT OUTER JOIN users AS users_1 ON users_1.id = follows.follower_id
    LEFT OUTER JOIN users AS users_2 ON users_2.id = follows.followed_id
    WHERE
        follows.followed_id = 7;
    """
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            # if self.email == current_app.config['FLASKY_ADMIN']:
            if self.email == "admin@admin.com":
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
            # 生成email地址的hash,en.gravatar.com头像生成服务
            if self.email is not None and self.avatar_hash is None:
                self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
            # 添加自己为被关注者
            self.follow(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_password_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})


    def generate_auth_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def reset_password_confirm(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True


    # gravatar请求响应缓慢，注释该头像服务。
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://s.gravatar.com/avatar'
        email_hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=email_hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    # 关注
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    # 取消关注
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    # 是否关注
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    # 是否被关注
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).fisrt() is not None

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', userid=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', userid=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', userid=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user


    def to_dict(self):
        json_user = {
            'url': url_for('api.get_user', userid=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', userid=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts', userid=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Permission(object):
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),
                                                       tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_comment', commentid=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', userid=self.author_id, _external=True)
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)
