import unittest
import os
import vue2doc
import io
import time


class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = vue2doc.app.test_client()
        self.timestamp = '1234567890'

    def tearDown(self):
        pass

    def test_homepage(self):
        rv = self.app.get('/')
        self.assertIn('VUE', rv.data)

    @unittest.skip('')
    def test_05_upload(self):

        # Upload a dummy .vue file...
        rv = self.app.post('/upload',
                           data=dict(
                           title=('Concept Map'), file=(io.BytesIO("this is a test"), 'test.vue'),
                           ), follow_redirects=True)
        self.assertIn('Alright!', rv.data)
        # Upload a dummy .vpk file...
        time.sleep(1)
        rv = self.app.post('/upload',
                           data=dict(
                           title=('Concept Map'), file=(io.BytesIO("this is a test"), 'test.vpk'),
                           ), follow_redirects=True)
        self.assertIn('Alright!', rv.data)

    @unittest.skip('')
    def test_06_download_pdf(self):

        app = vue2mdflask.Flask(__name__)
        app.config['SECRET_KEY'] = 'sekrit!'

        with app.test_client() as c:
            with c.session_transaction() as sess:
                sess['title'] = 'Title of the Map'
            rv = c.get('/download/markdown/' + self.timestamp)
        self.assertIsNone(rv)
