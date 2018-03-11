# -*- coding: utf-8 -*-
"""
Created on 2016/9/23

@author: wb-zy184129
"""
import os
import unittest
import threading
import time
from selenium import webdriver

from flask import current_app
from app import create_app, db
from app.models import Post, User, Comment, Follow, Role


class SeleniumTestCase(unittest.TestCase):
    client = None
    base_url = "http://127.0.0.1:5000/"

    @classmethod
    def setUpClass(cls):
        chromedriver_dir = os.path.abspath('./driver/chromedriver.exe')
        cls.client = webdriver.Chrome(executable_path=chromedriver_dir)

        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")

            db.create_all()
            Role.insert_roles()
            User.generate_fake(10)
            Post.generate_fake(10)

            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='admin@a.com',
                         username='admin',
                         password='123',
                         role=admin_role,
                         confirmed=True)
            db.session.add(admin)
            db.session.commit()

            threading.Thread(target=cls.app.run).start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://127.0.0.1:5000/shutdown')
            # cls.client.close()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_email_login(self):
        self.open()
        self.by_id("email").send_keys("admin@a.com")
        self.by_id("password").send_keys("123")
        self.by_id("submit").click()

    def open(self, uri="auth/login"):
        self.client.get(self.base_url + uri)
        self.client.maximize_window()
        self.sleep()

    def by_id(self, this_id):
        return self.client.find_element_by_id(this_id)

    def by_name(self, this_name):
        return self.client.find_element_by_name(this_name)

    def by_xpath(self, this_xpath):
        return self.client.find_elements_by_xpath(this_xpath)

    def by_css(self, this_css):
        return self.client.find_element_by_css_selector(this_css)

    def by_link(self, this_link):
        return self.client.find_element_by_link_text(this_link)

    def sleep(self, s=3):
        return time.sleep(s)


if __name__ == '__main__':
    unittest.main()
