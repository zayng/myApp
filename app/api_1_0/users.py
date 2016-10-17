# -*- coding: utf-8 -*-
"""
Created on 2016/7/31

@author: susce
"""
from flask import url_for, request, jsonify, g, current_app
from . import api
from ..models import User, Post


@api.route('/users/')
def get_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.paginate(page, per_page=current_app.config['FLASK_API_USER_PER_PAGE'], error_out=False)
    users = pagination.items
    prev_page = None
    if pagination.has_prev:
        prev_page = url_for('api.get_users', page=page-1, _external=True)
    next_page = None
    if pagination.has_next:
        next_page = url_for('api.get_users', page=page+1, _external=True)
    return jsonify({
        'users': [user.to_json() for user in users],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })


@api.route('/users/<int:userid>')
def get_user(userid):
    user = User.query.get_or_404(userid)
    return jsonify(user.to_json())


@api.route('/users/<int:userid>/posts/')
def get_user_posts(userid):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(userid)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_API_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev_page = None
    if pagination.has_prev:
        prev_page = url_for('api.get_user_posts', userid=userid, page=page-1, _external=True)
    next_page = None
    if pagination.has_next:
        next_page = url_for('api.get_user_posts', userid=userid, page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })


@api.route('/users/<int:userid>/timeline/')
def get_user_followed_posts(userid):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(userid)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASK_API_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev_page = None
    if pagination.has_prev:
        prev_page = url_for('api.get_user_followed_posts', userid=userid, page=page-1, _external=True)
    next_page = None
    if pagination.has_next:
        next_page = url_for('api.get_user_followed_posts', userid=userid, page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })


