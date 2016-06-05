# -*- coding:utf-8 -*-
"""
Created on '2016/6/5'

@author: 'susce'
"""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
