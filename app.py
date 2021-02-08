from flask import Flask, redirect
from flask_mongoengine import MongoEngine
from flask_restful import Api
from flask_wtf.csrf import CSRFProtect
from apps.token_refresher import RefreshToken
from apps.registration.views import Register
from apps.movie.views import GetMovie, MovieList, WatchListRetrieve, WatchListAdd, LikedListRetrieve,\
LikedListAdd, WatchListRemove, LikedListRemove, MovieAdd, MovieUpdate, MovieDelete
from apps.profile.views import Login, Logout, UserDetail, AssignAdminRole
from apps.search.views import Search
from flask_jwt_extended import JWTManager
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(PROJECT_PATH, 'apps'))
app = Flask(__name__)
api = Api(app)

app.config['MONGODB_SETTINGS'] = {
    'db': 'fynd_imdb',
    # 'username':'root',
    # 'password':'root'
}
db = MongoEngine(app)
# SECRET_KEY = os.urandom(32)
# app.config['SECRET_KEY'] = SECRET_KEY
app.config['WTF_CSRF_ENABLED'] = False
csrf = CSRFProtect(app)
app.config['JWT_SECRET_KEY'] = '1VPtwvmWDvU0UHh6+DlWmWUgcDpU6GNeTcqCbD9Db5A='
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/refresh_token'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400
jwt = JWTManager(app)

@app.route('/', methods = ['GET'])
def redirect_to_login():
    return redirect("/login", code=200)

#Token handling api
api.add_resource(RefreshToken, '/refresh_token')

#Profiles api
api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(UserDetail, '/user_detail')
api.add_resource(AssignAdminRole, '/add_admin')

#Movie api
api.add_resource(GetMovie, '/movie')
api.add_resource(MovieList, '/movie_list')
api.add_resource(WatchListRetrieve, '/watchlist')
api.add_resource(WatchListAdd, '/add_to_watchlist')
api.add_resource(WatchListRemove, '/remove_from_watchlist')
api.add_resource(LikedListRetrieve, '/liked_list')
api.add_resource(LikedListAdd, '/like')
api.add_resource(LikedListRemove, '/unlike')
api.add_resource(MovieAdd, '/add_movie')
api.add_resource(MovieUpdate, '/update_movie/<string:movie_id>')
api.add_resource(MovieDelete, '/remove_movie')

#Search api
api.add_resource(Search, '/search')

