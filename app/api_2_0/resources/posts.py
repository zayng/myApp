# -*- coding: utf-8 -*-
"""
Created on 2016/8/10

@author: wb-zy184129
"""
from flask_restful import fields, marshal, marshal_with, reqparse, Resource, url_for, current_app
from ...models import User, Post
from ... import db

from ..common.utils import query_page

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


class PostListApi(Resource):

    @marshal_with(post_page_fields)
    def get(self):
        args = posts_list_parser.parse_args()
        page = args.get('page')
        pagination = Post.query.paginate(page, per_page=current_app.config['FLASK_API_POSTS_PER_PAGE'], error_out=False)
        pagination_fields = query_page(pagination, 'api_bp.get_post_list', page, envelope='posts')
        return pagination_fields

    def post(self):
        pass


class PostInfoApi(Resource):

    @marshal_with(post_fields)
    def get(self, postid):
        post = Post.query.get_or_404(postid)
        post_info = post.to_dict()
        return post_info


class UserPostsApi(Resource):

    @marshal_with(post_page_fields)
    def get(self, userid):
        args = posts_list_parser.parse_args()
        page = args.get('page')
        user = User.query.get_or_404(userid)
        pagination = user.posts.oder_by(Post.timestamp.desc())\
            .paginate(page, per_page=current_app.config['FLASK_API_POSTS_PER_PAGE'], error_out=False)
        pagination_fields = query_page(pagination, 'api_bp.get_user_posts', page, envelope='posts')
        return pagination_fields


class FollowedPostsApi(Resource):

    @marshal_with(post_page_fields)
    def get(self, userid):
        args = posts_list_parser.parse_args()
        page = args.get('page')
        user = User.query.get_or_404(userid)
        pagination = user.followed_posts.oder_by(Post.timestamp.desc())\
            .paginate(page, per_page=current_app.config['FLASK_API_POSTS_PER_PAGE'], error_out=False)
        pagination_fields = query_page(pagination, 'api_bp.get_user_followed_posts', page, envelope='posts')
        return pagination_fields
