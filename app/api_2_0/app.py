# -*- coding: utf-8 -*-
"""
Created on 2016/8/9

@author: susce
"""
from flask import url_for, render_template
from flask_restful import Resource, Api
from . import api_bp


api = Api(api_bp)


class TodoItem(Resource):
    def get(self, id):
        return {'task': 'Say "Hello, World!"'}

api.add_resource(TodoItem, '/todos/<int:id>')
