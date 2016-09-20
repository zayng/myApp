# -*- coding: utf-8 -*-
"""
Created on 2016/8/9

@author: susce
"""
from flask import g
from flask_restful import Api
from . import api_bp
from .. import hp_auth
from ..models import User, AnonymousUser
from .common.errors import unauthorized, forbidden
from .resources.token import Token


from .resources.users import UserListApi, UserInfoApi
from .resources.posts import PostListApi, PostInfoApi, UserPostsApi, FollowedPostsApi
from .resources.comments import CommentListApi, CommentInfoApi, PostCommentsApi


build_api = Api(api_bp)


@hp_auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@hp_auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api_bp.before_request
@hp_auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


build_api.add_resource(UserListApi, '/users/', endpoint='get_user_list')
build_api.add_resource(UserInfoApi, '/users/<int:userid>', endpoint='get_user')
build_api.add_resource(UserPostsApi, '/users/<int:userid>/posts/', endpoint='get_user_posts')
build_api.add_resource(FollowedPostsApi, '/users/<int:userid>/timeline/', endpoint='get_user_followed_posts')


build_api.add_resource(PostListApi, '/posts/', endpoint='get_post_list')
build_api.add_resource(PostInfoApi, '/posts/<int:postid>', endpoint='get_post')

build_api.add_resource(CommentListApi, '/comments/', endpoint='get_comment_list')
build_api.add_resource(CommentInfoApi, '/comments/<int:commentid>', endpoint='get_comment')

build_api.add_resource(PostCommentsApi, '/posts/<int:postid>/comments/', endpoint='get_post_comments')
