# -*- coding: utf-8 -*-
"""
Created on 2016/9/13

@author: wb-zy184129
"""
from flask_restful import url_for


def query_page(pagination, endpoint_name, page, envelope, **kwargs):
    obj_items = pagination.items
    count = pagination.total
    if count == 0:
        return {'message': "Query collection is empty!"}
    if count < 6:
        return {envelope: [item.to_dict() for item in obj_items], 'count': pagination.total}
    prev_page = None
    if pagination.has_prev:
        prev_page = url_for(endpoint_name, page=page - 1, _external=True, **kwargs)
    next_page = None
    if pagination.has_next:
        next_page = url_for(endpoint_name, page=page + 1, _external=True, **kwargs)

    return {envelope: [item.to_dict() for item in obj_items],
            'prev': prev_page,
            'next': next_page,
            'count': pagination.total
            }

