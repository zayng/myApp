# -*- coding: utf-8 -*-
"""
Created on 2016/7/31

@author: susce
"""
from . import api
from ..exceptions import ValidationError
from flask import jsonify


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.stats_code = 403
    return response


def unanthorized(message):
    response = jsonify({'error': 'unanthorized', 'message': message})
    response.stats_code = 401
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])