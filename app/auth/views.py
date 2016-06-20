# -*- coding:utf-8 -*-
"""
Created on '2016/6/5'

@author: 'susce'
"""
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .. import db
from .forms import (LoginForm, LoginUsernameForm, ChangePasswordForm,
                    ResetEmailRequestForm, ResetPasswordForm, RegistrationForm)
from ..email import send_mail
from flask.ext.login import current_user


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/login-user', methods=['GET', 'POST'])
def login_username():
    form = LoginUsernameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('无效的用户名和密码.')
    return render_template('auth/login_user.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        """
        send_mail(user.email, 'Confirm Your Account',
                  'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('auth.login'))
        """
        flash('一个包含令牌的链接地址已生成.')
        return render_template('/auth/gets_token.html', token=token, user=user)
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed you accout. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('/auth/unconfirmed.html')


"""取消件发送操作,采用生成链接页面代替
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm you account',
              'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you email.')
    return redirect(url_for('main.index'))
"""


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    flash('一个包含令牌的链接地址已生成.')
    return render_template('/auth/gets_token.html', token=token, user=current_user)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            flash('密码已更新成功.')
            return redirect(url_for('.login_username'))
        else:
            flash('无效密码,请重新输入.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def reset_email_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetEmailRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            token = user.generate_reset_password_token()
            flash('一个包含令牌的链接地址已生成.')
            return render_template('/auth/gets_token.html', token=token, user=user)
        else:
            flash('输入的邮箱地址未注册.')
    return render_template('/auth/reset_email.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('您输入的邮箱地址未找到.')
            return redirect(url_for('main.index'))
        if user.reset_password_confirm(token, form.new_password.data):
            flash('您的密码已更新.')
            return redirect(url_for('.login'))
        else:
            flash('这个重置密码的链接无效或已过期，请重新找回密码.')
            return redirect(url_for('main.index'))
    return render_template('/auth/reset_password.html', form=form)

