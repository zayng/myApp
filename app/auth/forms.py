# -*- coding:utf-8 -*-
"""
Created on '2016/6/5'

@author: 'susce'
"""
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class LoginUsernameForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('请记住我')
    submit = SubmitField('登录')


class RegistrationForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64),
                                                Regexp('^[A-za-z][A-Za-z0-9_-]*$', 0,
                                                       'Username must have only letters,'
                                                       'numbers, dots or underscores')])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已使用.')


class ChangePasswordForm(Form):
    password = PasswordField('原密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('new_password2', '新密码必须匹配.')])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class ResetEmailRequestForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('提交')


class ResetPasswordForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('new_password2', '新密码必须匹配.')])
    new_password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('提交')


class NewRegistrationForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64),
                                                Regexp('^[A-za-z][A-Za-z0-9_-]*$', 0,
                                                       'Username must have only letters,'
                                                       'numbers, dots or underscores')])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')
