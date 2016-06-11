# -*- coding:utf-8 -*-
"""
Created on '2016/6/5'

@author: 'susce'
"""
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class LoginUsernameForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('请记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(1, 64),
                                                   Regexp('^[A-za-z][A-Za-z0-9_-]*$', 0,
                                                          'Username must have only letters,'
                                                          'numbers, dots or underscores')])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('注册')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class ChangePasswordForm(Form):
    password = PasswordField('现在密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('new_password2', '新密码必须匹配.')])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class ResetEmailForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('提交')


class ResetPasswordForm(Form):
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('new_password2', '新密码必须匹配.')])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('提交')

