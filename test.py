from mongoengine import connect, disconnect
from flask_mongoengine import MongoEngine
from flask_testing import TestCase
import flask_jwt_extended
from flask_jwt_extended import get_jwt_identity
from app import app
from apps.profile.models import Profile
from unittest.mock import patch

class BaseTestCase(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        # app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return app
    
    def setUp(self):
        connect('mongoenginetest', host='mongomock://localhost', alias='testdb')
        # app.config['MONGODB_SETTINGS'] =  {
        #     'db': 'mongoenginetest',
        #     'host': 'mongomock://localhost',
        #     'alias': 'testdb'
        # }
        # MongoEngine(app)

    def tearDown(self):
       disconnect()

class UserViewsTests(BaseTestCase):
    def test_users_can_registration(self):
        response = self.client.post('/register',
                                    data={'name': 'Test', 'username': 'admin@test.com', 'password': '12345', 'confirm_password': '12345'})

        self.assertEqual(response.json, dict(success=True, message = "Registered successfully"))

        response = self.client.post('/register',
                                    data={'name': 'Test', 'username': 'admin@test.com', 'password': '12345', 'confirm_password': '1234'})

        self.assertEqual(response.json, dict(success='False', message = "Password don't match"))

        response = self.client.post('/register',
                                    data={'name': 'Test', 'username': 'admin@test.com', 'password': '12345', 'confirm_password': '12345'})

        self.assertEqual(response.json, dict(success='False', message = "Profile already exists."))


    def test_users_can_login(self):
        response = self.client.post('/login',
                                    data={'username': 'admin@test.com', 'password': '12345'})
        
        self.assertTrue(response.json['success'])

        response = self.client.post('/login',
                                    data={'username': 'admin@test.com', 'password': '1234'})

        self.assertEqual(response.json['message'], 'Password wrong.')

        response = self.client.post('/login',
                                    data={'username': None, 'password': '12345'})

        self.assertEqual(response.json['message'], {'username': 'Missing required parameter in the post body'})

        response = self.client.post('/login',
                                    data={'username': 'admin@test.com', 'password': None})

        self.assertEqual(response.json['message'], {'password': 'Missing required parameter in the post body'})
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    def test_users_can_add_movie(self, *args, **kwargs):
        with self.client:
            self.client.post('/login',
                                    data={'username': 'user@test.com', 'password': '12345'})
            response = self.client.post('/add_movie',
                                    data={'username': 'admin@test.com', 'password': '1234'})
            self.assertEqual(response.json, {'password': 'Missing required parameter in the post body'})
            