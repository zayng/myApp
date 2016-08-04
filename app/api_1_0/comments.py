# -*- coding: utf-8 -*-
"""
Created on 2016/7/31

@author: susce
"""
from flask import url_for, request, jsonify, g, current_app
from . import api
from ..models import User, Post, Comment, Permission
from .decorators import permission_required
from .. import db


@api.route('/comments/<int:commentid>')
def get_comment(commentid):
    comment = Comment.query.get_or_404(commentid)
    return jsonify(comment.to_json())


@api.route('/comments/')
def get_comments():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc())\
        .paginate(page, per_page=current_app.config['FLASK_API_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    prev_page = None
    if pagination.has_prev:
        prev_page = url_for('api.get_comments', page=page -1, _external=True)
    next_page = None
    if pagination.has_next:
        next_page = url_for('api.get_comments', page=page + 1, _external=True)
    return jsonify({
        "comments": [comment.to_json() for comment in comments],
        "prev": prev_page,
        "next": next_page,
        "count": pagination.total
    })


@api.route('/posts/<int:postid>/comments/')
def get_post_comments(postid):
    page = request.args.get('page', 1, type=int)
    post = Post.query.get_or_404(postid)
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config[
        'FLASK_API_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    prev_page = None
    if pagination.has_prev:
        prev_page = url_for('api.get_post_comments', postid=postid, page=page - 1, _external=True)
    next_page = None
    if pagination.has_next:
        next_page = url_for('api.get_post_comments', postid=postid, page=page + 1, _external=True)
    return jsonify({
        'posts': [comment.to_json() for comment in comments],
        'prev': prev_page,
        'next': next_page,
        'count': pagination.total
    })



@api.route('/posts/<int:postid>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_post_comment(postid):
    comment = Comment.from_json(request.json)
    comment.author_id = g.current_user
    comment.post_id = postid
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'Location': url_for('api.get_comment', commentid=comment.id, _external=True)}

