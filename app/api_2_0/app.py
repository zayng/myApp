# -*- coding: utf-8 -*-
"""
Created on 2016/8/9

@author: susce
"""

# from flask.ext.httpauth import HTTPBasicAuth
from flask_restful import Api
from . import api_bp
from .resources.task import TaskAPI, TaskListAPI
# from .resources.users import Todo

api = Api(api_bp)
# auth = HTTPBasicAuth()


# api.add_resource(Todo, '/todo', endpoint='todo_ep')
api.add_resource(TaskListAPI, '/todo/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/tasks/<int:id>', endpoint='task')