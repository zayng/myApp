# -*- coding: utf-8 -*-
"""
Created on 2016/8/10

@author: wb-zy184129
"""

from flask_restful import fields, marshal_with, reqparse, Resource, current_app
from ...models import User


user_parser = reqparse.RequestParser()
user_parser.add_argument('id', dest='userid', type=int, required=True, help='The user\'s username')
user_parser.add_argument('page', type=int, help='page is required.')


user_fields = {
    'url': fields.String,
    'username': fields.String,
    'member_since': fields.String,
    'last_seen': fields.String,
    'posts': fields.String,
    'followed_posts': fields.String,
    'post_count': fields.Integer
}


class UserListApi(Resource):

    @marshal_with(user_fields)
    def get(self):
        args = user_parser.parse_args()
        page = args.get('page', 1, type=int)
        pagination = User.query.paginate(page, per_page=current_app.config['FLASK_API_USER_PER_PAGE'], error_out=False)
        users = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = url_for('api.get_users', page=page - 1, _external=True)
        next_page = None
        if pagination.has_next:
           next_page = url_for('api.get_users', page=page + 1, _external=True)
        user_dict = [user.to_dict() for user in users]
        return user_dict


class UserInfoApi(Resource):

    @marshal_with(user_fields)
    def get(self, userid):
        user = User.query.get_or_404(userid)
        user_dict = user.to_dict()
        return user_dict
