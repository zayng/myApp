# -*- coding:utf-8 -*-
"""
Created on '2016/5/29'

@author: 'susce'
"""
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(Form):
    name = StringField('what is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
