# -*- coding: utf-8 -*-
"""
Created on 2016/7/31

@author: susce
"""
from flask import url_for, redirect, request, jsonify, g
from . import api
from ..models import Post, Permission
from .. import db
from .authentication import auth
from .decorators import permission_required


@api.route('/posts', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Locaion': url_for('api.get_post', id=post.id, _external=True)}


@api.route('/posts/')
@auth.login_required
def get_posts():
    posts = Post.query.all()
    return jsonify({'posts': [post.to_json() for post in posts]})


@api('/posts/<int:id>')
@auth.login_required
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())
