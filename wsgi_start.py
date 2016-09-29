# -*- coding: utf-8 -*-
"""
Created on 2016/9/29

@author: wb-zy184129
"""

from app import create_app


app = create_app('default')


if __name__ == "__main__":
    app.run()
