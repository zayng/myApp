# -*- coding: utf-8 -*-
"""
Created on 2016/8/10

@author: wb-zy184129
"""
from flask_restful import fields, marshal, marshal_with, reqparse, Resource, url_for, current_app
from ...models import User
from ... import db


def validation_null(value, name):
    if value == "":
        raise ValueError("{0} cannot be empty".format(name))
    else:
        is_user = None
        if name == "username":
            is_user = User.query.filter_by(username=value).first()
        if name == "email":
            is_user = User.query.filter_by(email=value).first()
        if is_user:
            raise ValueError("'{0}',已注册".format(value))
    return value


user_list_parser = reqparse.RequestParser()
user_list_parser.add_argument('page', dest='page', type=int, location='args', default=1)

user_build_parser = user_list_parser.copy()
user_build_parser.remove_argument('page')
user_build_parser.add_argument('username', dest='username', type=validation_null, required=True, location='json',
                               trim=True, nullable=False)
user_build_parser.add_argument('email', dest='email', type=validation_null, required=True, location='json',
                               trim=True, nullable=False)
user_build_parser.add_argument('password', dest='password', type=validation_null, required=True, location='json',
                               trim=True, nullable=False)


user_fields = {
    'url': fields.String,
    'username': fields.String,
    'email': fields.String(default=None),
    'member_since': fields.String,
    'last_seen': fields.String,
    # 'posts': fields.String,
    # 'followed_posts': fields.String,
    'post_count': fields.Integer
}

user_page_fields = {
    'users': fields.Nested(user_fields),
    'prev': fields.String,
    'next': fields.String,
    'count': fields.Integer
}


class UserListApi(Resource):

    @marshal_with(user_page_fields)
    def get(self):
        args = user_list_parser.parse_args()
        page = args.get('page')
        pagination = User.query.paginate(page, per_page=current_app.config['FLASK_API_USER_PER_PAGE'], error_out=False)
        users = pagination.items
        prev_page = None
        if pagination.has_prev:
            prev_page = url_for('api_bp.get_user_list', page=page - 1, _external=True)
        next_page = None
        if pagination.has_next:
            next_page = url_for('api_bp.get_user_list', page=page + 1, _external=True)
        return {'users': [user.to_dict() for user in users],
                'prev': prev_page,
                'next': next_page,
                'count': pagination.total
                }

    def post(self):
        args = user_build_parser.parse_args(strict=True)
        user = User(username=args['username'], email=args['email'], password=args['password'])
        db.session.add(user)
        db.session.commit()
        return {'message': 'success', 'data': marshal(user.to_dict(), user_fields)}


class UserInfoApi(Resource):

    @marshal_with(user_fields)
    def get(self, userid):
        user = User.query.get_or_404(userid)
        user_info = user.to_dict()
        return user_info



