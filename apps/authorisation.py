from functools import wraps

from flask.json import jsonify
from apps.profile.models import Profile
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

def admin_only(func):
    @wraps(func)
    def profile_check(*args, **kwargs):
        current_user_id = get_jwt_identity()
        profile_object = Profile.objects.get(id = current_user_id)
        if profile_object.is_admin == False:
            response = jsonify({'message': 'Admin authorisation required'})
            response.status_code = 403
            return response
        return func(*args, **kwargs)
    return profile_check
