# -*- coding:utf-8 -*-
"""
Created on '2016/6/9'

@author: 'susce'
"""
from flask import Flask, flash

app = Flask(__name__)


@app.route('/')
def index():
    # flash('this message!')
    return '<h1>Hello, world!<h1>'

if __name__ == '__main__':
    app.run()