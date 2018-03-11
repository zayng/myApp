# -*- coding: utf-8 -*-
"""
Created on 2016/8/10

@author: wb-zy184129
"""
from flask_restful import fields, marshal, marshal_with, reqparse, Resource, url_for, current_app
from ...models import Post, Comment

from ..common.utils import query_page

comments_list_parser = reqparse.RequestParser()
comments_list_parser.add_argument('page', dest='page', type=int, location='args', default=1)

comment_fields = {
    'url': fields.String,
    'body': fields.String,
    'author': fields.String,
    'timestamp': fields.String
}

comment_page_fields = {
    'comments': fields.Nested(comment_fields),
    'prev': fields.String,
    'next': fields.String,
    'count': fields.Integer
}


class CommentListApi(Resource):

    @marshal_with(comment_page_fields)
    def get(self):
        args = comments_list_parser.parse_args()
        page = args.get('page')
        pagination = Comment.query.paginate(page, per_page=current_app.config['FLASK_API_COMMENTS_PER_PAGE'],
                                            error_out=False)
        pagination_fields = query_page(pagination, 'api_bp.get_comment_list', page, envelope='comments')
        return pagination_fields

    def post(self):
        pass


class CommentInfoApi(Resource):

    @marshal_with(comment_fields)
    def get(self, commentid):
        comment = Comment.query.get_or_404(commentid)
        comment_info = comment.to_dict()
        return comment_info


class PostCommentsApi(Resource):

    @marshal_with(comment_page_fields)
    def get(self, postid):
        args = comments_list_parser.parse_args()
        page = args.get('page')
        post = Post.query.get_or_404(postid)
        if post.comments.count() == 0:
            return {'message': 'No comments', 'count': 0}
        pagination = post.comments.order_by(Comment.timestamp.asc()). \
            paginate(page, per_page=current_app.config['FLASK_API_COMMENTS_PER_PAGE'], error_out=False)
        pagination_fields = query_page(pagination, 'api_bp.get_post_comments', page, envelope='comments', postid=postid)
        return pagination_fields
