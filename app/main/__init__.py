# -*- coding:utf-8 -*-
"""
Created on '2016/5/29'

@author: 'susce'
"""
from flask import Blueprint


main = Blueprint('main', __name__)

from . import views, errors

