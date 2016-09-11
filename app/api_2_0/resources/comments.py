# -*- coding: utf-8 -*-
"""
Created on 2016/8/10

@author: wb-zy184129
"""
from flask_restful import fields, marshal, marshal_with, reqparse, Resource, url_for, current_app
from ...models import Post
from ... import db

comments_list_parser = reqparse.RequestParser()
comments_list_parser.add_argument('page', dest='page', type=int, location='args', default=1)


comment_fields = {
    'url': fields.String,
    'body': fields.String,
    # 'body_html': fields.String(default=None),
    'timestamp': fields.String,
    'author': fields.String,
    'comments': fields.String,
    'comment_count': fields.Integer
}

comment_page_fields = {
    'posts': fields.Nested(comment_fields),
    'prev': fields.String,
    'next': fields.String,
    'count': fields.Integer
}


class CommentsListApi(Resource):
    def get(self):
        return "this is null"

    def post(self):
        pass


class CommentInfoApi(Resource):
    def get(self):
        pass
