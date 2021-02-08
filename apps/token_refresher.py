from flask_jwt_extended import create_access_token, set_access_cookies
from flask_jwt_extended import jwt_refresh_token_required, get_jwt_identity
from flask import jsonify
from flask_restful import Resource

class RefreshToken(Resource):
    @jwt_refresh_token_required
    def get(self, **kwargs):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user)
        response = jsonify({'refresh': True})
        response.status_code = 200
        set_access_cookies(response, access_token)
        return response

