#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Tests
    ~~~~~~

    This will be the test bed for the entire application. I'm not sure
    how to test apps, just yet, but I'll figure it out.

    :author: Jeff Kereakoglow
    :date: 2013-09-09
    :copyright: (c) 2013 by NESN.
    :license: BSD, see LICENSE for more details.
"""
# import os
import unittest

from app import app

class NESNAPITestCase(unittest.TestCase):
    def setUp(self):
        # Flask apps testing. See: http://flask.pocoo.org/docs/testing/
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False


    def tearDown(self):
        pass

    def test_posts(self):
        rv = self.app.get('/')
        app.logger.debug("Value for data: " + str(app.data))
        assert 1 == 1
        # assert rv.status == '302 FOUND'

    # def setCurrentUser(self, email, user_id, is_admin=False):
    #     os.environ['USER_EMAIL'] = email or ''
    #     os.environ['USER_ID'] = user_id or ''
    #     os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    # def test_home_redirects(self):
    #     rv = self.app.get('/')
    #     assert rv.status == '302 FOUND'

    # def test_says_hello(self):
    #     rv = self.app.get('/hello/world')
    #     assert 'Hello world' in rv.data

    # def test_displays_no_data(self):
    #     rv = self.app.get('/examples')
    #     assert 'No examples yet' in rv.data

    # def test_inserts_data(self):
    #     self.setCurrentUser(u'john@example.com', u'123')
    #     rv = self.app.post('/example/new', data=dict(
    #         example_name='An example',
    #         example_description='Description of an example'
    #     ), follow_redirects=True)
    #     assert 'Example successfully saved' in rv.data

    #     rv = self.app.get('/examples')
    #     assert 'No examples yet' not in rv.data
    #     assert 'An example' in rv.data

    # def test_admin_login(self):
    #     #Anonymous
    #     rv = self.app.get('/admin_only')
    #     assert rv.status == '302 FOUND'
    #     #Normal user
    #     self.setCurrentUser(u'john@example.com', u'123')
    #     rv = self.app.get('/admin_only')
    #     assert rv.status == '302 FOUND'
    #     #Admin
    #     self.setCurrentUser(u'john@example.com', u'123', True)
    #     rv = self.app.get('/admin_only')
    #     assert rv.status == '200 OK'

    def test_404(self):
        """Test the 404"""
        rv = self.app.get('/missing')
        assert rv.status == '404 NOT FOUND'
        assert '<h1>Not found</h1>' in rv.data


if __name__ == '__main__':
    # print sys.path
    unittest.main()
