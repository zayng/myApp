# -*- coding: utf-8 -*-
"""
Created on 2016/8/9

@author: susce
"""
from flask import g, jsonify
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
from . import api_bp
from .errors import unauthorized, forbidden
from ..models import User, AnonymousUser, Post, Comment, Permission
from .resources.task import TaskAPI, TaskListAPI


api = Api(api_bp)

re_auth = HTTPBasicAuth()


@re_auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@re_auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api_bp.before_request
@re_auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api_bp.route('/token')
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    token = g.current_user.generate_auth_token(expiration=3600)
    return jsonify({'token': token, 'expiration': 3600})



api.add_resource(TaskListAPI, '/todo/tasks', endpoint='.tasks')
api.add_resource(TaskAPI, '/todo/tasks/<int:id>', endpoint='.task')



