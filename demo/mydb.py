# -*- coding: utf-8 -*-
"""
Created on 2016/7/8

@author: wb-zy184129
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import String, Integer, CHAR, BIGINT
from sqlalchemy.ext.declarative import declarative_base


basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'mydata.sqlite')

engine = create_engine(SQLALCHEMY_DATABASE_URI)
DBSession = sessionmaker(engine)
session = DBSession()

BaseModel = declarative_base()


class Blog(BaseModel):
    __tablename__ = 'blog'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    title = Column(String(64), server_default='', nullable=False)
    text = Column(String, server_default='', nullable=False)
    user = Column(BIGINT, ForeignKey('user.id'), index=True, nullable=False)
    create = Column(BIGINT, index=True, server_default='0', nullable=False)


class User(BaseModel):
    __tablename__ = 'user'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    name = Column(String(32), server_default='', nullable=False)
    username = Column(String(32), index=True, server_default='', nullable=True)
    password = Column(String(64), server_default='', nullable=False)
