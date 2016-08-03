# -*- coding: utf-8 -*-
"""
Created on 2016/7/31

@author: susce
"""
from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, posts, users, comments, errors
