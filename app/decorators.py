# -*- coding:utf-8 -*-
"""
Created on '2016/6/19'

@author: 'susce'
"""
from functools import wraps
from flask import abort
from flask.ext.login import current_user
from .models import Permission


def permission_required(permission):
    def decortor(f):
        @wraps(f)
        def decorted_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorted_function
    return decortor


def admin_requied(f):
    return permission_required(Permission.ADMINISTER)(f)
