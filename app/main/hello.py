# -*- coding: utf-8 -*-
"""
Created on 2016/4/21

@author: wb-zy184129
"""
import os
from threading import Thread

from flask import Flask, session, redirect, url_for
from flask import render_template
from flask.ext.script import Manager
from flask.ext.moment import Moment
from flask.ext.bootstrap import Bootstrap

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand

from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.script import Shell

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
manage = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
manage.add_command('db', MigrateCommand)

app.config['SECRET_KEY'] = 'hand to guess string'
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
# app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USERNAME'] = "410105205@qq.com"
app.config['MAIL_PASSWORD'] = "dvaolbxgzgbbbjbd"
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = "410105205@qq.com"
app.config['FLASKY_ADMIN'] = "testleader@163.com"
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manage.add_command("shell", Shell(make_context=make_shell_context()))
manage.add_command('db', MigrateCommand)


class NameForm(Form):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_mail(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))


@app.route('/user/<name>')
def user_name(name):
    return render_template('user.html', name=name)


if __name__ == "__main__":
    # manage.run()
    app.run(debug=True)