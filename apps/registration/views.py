from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
from flask import Blueprint, render_template, jsonify, make_response, current_app, Response
from flask_restful import Resource, reqparse
from .forms import RegisterForm
from apps.profile.models import Profile
from apps.encrypt import Encrypt
import werkzeug
from werkzeug.utils import secure_filename
import os

enc = Encrypt()
register = Blueprint('register', __name__, template_folder='templates')

# @register.route("/register", methods=['get', 'post'])
# def register_view():
#     form = Register()
#     response = {'error_message': ''}
#     if request.method == 'POST' and form.validate_on_submit():
#         if isinstance(form.validate_on_submit(), dict) and 'error_message' in form.validate_on_submit():
#             return render_template('register.html', form=form, response = form.validate_on_submit())
#         profile_object = Profile(name = form.name.data, username = form.username.data)
#         profile_object.password = enc.generate_hash(form.password.data)
#         if form.display_picture.data:
#             filename = secure_filename(form.display_picture.data.filename)
#             form.display_picture.data.save(os.path.join(current_app.instance_path, 'display_picture', filename))
#             profile_object.display_picture.put(open(os.path.join(current_app.instance_path, 'display_picture', filename), 'rb'))
#         profile_object.save()
#         return jsonify({'success': True})
#     return render_template('register.html', form=form, response = response)

class Register(Resource):
    def get(self, **kwargs):
        form = RegisterForm()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('register.html', form=form), 200, headers)
    def post(self, **kwargs):
        form = RegisterForm()
        if isinstance(form.validate_on_submit(), Response):
            return form.validate_on_submit()
        parser = reqparse.RequestParser()
        parser.add_argument('name', required = True, type=str, location='form')
        parser.add_argument('username', required = True, type=str, location='form')
        parser.add_argument('password', required = True, type=str, location='form')
        parser.add_argument('display_picture', type=werkzeug.datastructures.FileStorage, location='files')
        if parser.parse_args():
            name = parser.parse_args()['name']
            username = parser.parse_args()['username']
            password = parser.parse_args()['password']
            display_picture = parser.parse_args()['display_picture']
            profile_exist = Profile.objects.filter(username = username)
            if profile_exist:
                response = jsonify({'success': 'False', 'message': 'Profile already exists.'})
                response.status_code = 409
                return response
            profile_object = Profile(name = name, username = username)
            profile_object.password = enc.generate_hash(password)
            if display_picture:
                picture_ext = display_picture.filename.split('.')[-1].strip()
                filename = secure_filename(username.replace('@', '').replace('.', '').strip()+ '.' + picture_ext)
                display_picture.save(os.path.join(current_app.instance_path, 'display_picture', filename))
                profile_object.display_picture.put(open(os.path.join(current_app.instance_path, 'display_picture', filename), 'rb'))
            profile_object.save()
            response = jsonify({'success': True, 'message': "Registered successfully"})
            response.status_code = 201
            access_token = create_access_token(identity = str(profile_object.id))
            refresh_token = create_refresh_token(identity= str(profile_object.id))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
            return response