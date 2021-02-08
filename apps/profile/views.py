from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import render_template, jsonify, make_response
from flask_restful import Resource, fields, marshal_with, marshal, reqparse
from .models import Profile
from .forms import LoginForm, AddAdminRollForm
from apps.encrypt import Encrypt
from apps.authorisation import admin_only
from datetime import datetime

enc = Encrypt()

profile_data = {
    'id': fields.String(attribute = 'id'),
    'name': fields.String(attribute = 'name'),
    'username': fields.String(attribute = 'username'),
    'is_admin': fields.Boolean(attribute = 'is_admin'),
    'registration_date': fields.DateTime(attribute = 'registeration_date'),
    'last_login': fields.DateTime
}
login_resource_fields = {
    'success': fields.Boolean(attribute = 'success'),
    'message': fields.String(attribute = 'message'),
    'profile_data': fields.Nested(profile_data, attribute = 'profile_data', default = {})
}

class Login(Resource):
    def get(self, **kwargs):
        form = LoginForm()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html', form=form), 200, headers)

    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required = True, type=str, location='form')
        parser.add_argument('password', required = True, type=str, location='form')
        if parser.parse_args():
            username = parser.parse_args()['username']
            password = parser.parse_args()['password']
            profile_obj = Profile.objects.filter(username = username)
            if profile_obj:
                profile_obj = profile_obj[0]
                if enc.verify_hash(password, profile_obj.password):
                    access_token = create_access_token(identity = str(profile_obj.id))
                    refresh_token = create_refresh_token(identity= str(profile_obj.id))
                    response_dict = {'success': True, 'message': 'Successfully logged in', 'profile_data': profile_obj}
                    profile_obj.update(last_login = datetime.now())
                    profile_obj.save()
                    response = jsonify(marshal(response_dict, login_resource_fields))
                    set_access_cookies(response, access_token)
                    set_refresh_cookies(response, refresh_token)
                    return response
                else:
                    response = jsonify(marshal({'success': False, 'message': 'Password wrong.'}, login_resource_fields))
                    unset_jwt_cookies(response)
                    response.status_code = 403
                    return response
            else:
                response = jsonify(marshal({'success': False, 'message': 'Email doesn\'t exist.'}, login_resource_fields))
                unset_jwt_cookies(response)
                response.status_code = 404
                return response

class Logout(Resource):
    def get(self, **kwargs):
        response = jsonify({'success': True, 'message': 'Successfully logged out.'})
        unset_jwt_cookies(response)
        response.status_code = 200
        return response

class UserDetail(Resource):
    @jwt_required
    @marshal_with(profile_data)
    def get(self, **kwargs):
        current_user_id = get_jwt_identity()
        profile_object = Profile.objects.get(id = current_user_id)
        return profile_object

class AssignAdminRole(Resource):
    @jwt_required
    @admin_only
    def get(self, **kwargs):
        form = AddAdminRollForm()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('add_admin.html', form=form), 200, headers)

    @jwt_required
    @admin_only   
    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required = True, type=str, location='form')
        if parser.parse_args():
            username = parser.parse_args()['username']
            user_obj = Profile.objects.filter(username = username)
            if user_obj:
                user_obj = user_obj[0]
                if user_obj.is_admin != True:
                    user_obj.is_admin = True
                    user_obj.save()
                    response = jsonify({'success': True, 'message': user_obj.name + ' is now a admin'})
                else:
                    response = jsonify({'success': False, 'message': user_obj.name + ' is already an admin'})
                    response.status_code = 409
            else:
                response = jsonify({'success': False, 'message': 'User with email {username} does not exist'.format(username = username)})
                response.status_code = 404
            return response