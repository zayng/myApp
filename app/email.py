# -*- coding: utf-8 -*-
"""
Created on 2016/6/1

@author: wb-zy184129
"""
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message as Message
from . import create_app, mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
