# -*- coding: utf-8 -*-
"""
Created on 2016/8/10

@author: wb-zy184129
"""
from flask_restful import fields, marshal, marshal_with, reqparse, Resource, url_for, current_app
from ...models import Post
from ... import db

posts_list_parser = reqparse.RequestParser()
posts_list_parser.add_argument('page', dest='page', type=int, location='args', default=1)


post_fields = {
    'url': fields.String,
    'body': fields.String,
    # 'body_html': fields.String(default=None),
    'timestamp': fields.String,
    'author': fields.String,
    'comments': fields.String,
    'comment_count': fields.Integer
}

post_page_fields = {
    'posts': fields.Nested(post_fields),
    'prev': fields.String,
    'next': fields.String,
    'count': fields.Integer
}


class PostsListApi(Resource):


    @marshal_with(post_page_fields)
    def get(self):
        args = posts_list_parser.parse_args()
        page = args.get('page')
        pagination = Post.query.paginate(page, per_page=current_app.config['FLASK_API_POSTS_PER_PAGE'], error_out=False)
        posts = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = url_for('api_bp.get_posts_list', page=page - 1, _external=True)
        next_page = None
        if pagination.has_next:
            next_page = url_for('api_bp.get_posts_list', page=page + 1, _external=True)
        return {'users': [post.to_dict() for post in posts],
                'prev': prev_page,
                'next': next_page,
                'count': pagination.total
                }

    def post(self):
        pass


class PostInfoApi(Resource):


    @marshal_with(post_fields)
    def get(self, postid):
        post = Post.query.get_or_404(postid)
        post_info = post.to_dict()
        return post_info
