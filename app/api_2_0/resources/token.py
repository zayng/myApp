# -*- coding: utf-8 -*-
"""
Created on 2016/8/25

@author: wb-zy184129
"""
from flask import g
from flask_restful import Resource
from ..common.errors import unauthorized


class Token(Resource):

    def get(self):
        if g.current_user.is_anonymous or g.token_used:
            return unauthorized('Invalid credentials')
        token = g.current_user.generate_auth_token(expiration=3600)
        return {'token': token, 'expiration': 3600}
