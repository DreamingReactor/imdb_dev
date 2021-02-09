from flask import jsonify, make_response, render_template, Response
from flask_restful import Resource, fields, marshal_with, marshal, reqparse
from flask_mongoengine import Pagination
from .models import Movie, Genre, WatchList, LikedList, MovieData
from .forms import MovieAddForm
from apps.artist.models import Artist, Profession
from apps.profile.models import Profile
import werkzeug
from flask_jwt_extended import jwt_required, get_jwt_identity
from apps.authorisation import admin_only
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

url_str_list = []
endpoint = ''

class DirectorName(fields.Raw):
    def format(self, value):
        return value.name

class Username(fields.Raw):
    def format(self, value):
        return value.username

class NextUrl(fields.Raw):
    def format(self, value):
        try:
            if value:
                global url_str_list, endpoint
                if not url_str_list:
                    return "/"+endpoint+"?page="+str(value().page)
                return "/"+endpoint+"?page="+str(value().page)+ '&'  + '&'.join(url_str_list)
        except werkzeug.exceptions.NotFound:
            return None

class PrevUrl(fields.Raw):
    def format(self, value):
        if value > 0:
            global url_str_list, endpoint
            if not url_str_list:
                return "/"+endpoint+"?page="+str(value)
            return "/"+endpoint+"?page="+str(value) + '&' + '&'.join(url_str_list)
        else:
            return None

class LastUrl(fields.Raw):
    def format(self, value):
        if value != 0:
            global url_str_list, endpoint
            if not url_str_list:
                return "/"+endpoint+"?page="+str(value)
            return "/"+endpoint+"?page="+str(value) + '&' + '&'.join(url_str_list)
        else:
            return None

movie_fields = {
    'id': fields.String(attribute = 'id'),
    'name': fields.String(attribute = 'name'),
    'director': DirectorName(attribute = 'director'),
    'genre': fields.List(fields.String(attribute = 'genre_str')),
    'rating': fields.Float(attribute = 'imdb_score'),
    'summary': fields.String(attribute = 'summary'),
    'starring': fields.List(fields.String(attribute = 'name')),
    'release_date': fields.DateTime,
    'added_by': Username(attribute = 'added_by'),
    'last_changed_by': Username(attribute = 'last_changed_by')
}
resource_fields = {
'count': fields.Integer(attribute = 'total'),
'limit': fields.Integer(attribute = 'per_page'),
'next': NextUrl(attribute = 'next'),
'previous': PrevUrl(attribute = 'prev_num'),
'last': LastUrl(attribute = 'pages'),
'result': fields.List(fields.Nested(movie_fields), attribute = 'items')
}

movie_save_fields = {
    'success': fields.Boolean(attribute = 'success'),
    'message': fields.String(attribute = 'message'),
    'movie_data': fields.Nested(movie_fields, attribute = 'movie_data', default = {})
}
class GetMovie(Resource):
    @marshal_with(movie_fields)
    def get(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', required = True, type=str, location='args')
        if parser.parse_args():
            movie_id = parser.parse_args()['movie_id']
            movie_obj = Movie.objects.filter(id = movie_id)
            if not movie_obj:
                response = jsonify({'success': False, 'message': 'Movie not found'})
                response.status_code = 404
                return response
            return movie_obj[0]

class MovieList(Resource):
    @marshal_with(resource_fields)
    def get(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default = 1, location='args')
        parser.add_argument('filter_genre', type = str, default = '', location='args')
        parser.add_argument('filter_director', type = str, default = '', location='args')
        parser.add_argument('filter_actor', type = str, default = '', location='args')
        queryset = Movie.objects.all()
        page_no = parser.parse_args()['page']
        global endpoint
        endpoint = 'movie_list'
        if parser.parse_args():
            filter_genre = parser.parse_args()['filter_genre']
            filter_director = parser.parse_args()['filter_director']
            filter_actor = parser.parse_args()['filter_actor']
            global url_str_list
            url_str_list = []
            if filter_genre:
                url_str_list.append('filter_genre='+filter_genre)
                genre_obj = Genre.objects.filter(genre_str__in = filter_genre.split(','))
                queryset = queryset.filter(genre__in = genre_obj)
            if filter_director:
                url_str_list.append('filter_director='+filter_director)
                artist_obj = Artist.objects.filter(name_lower = filter_director.lower())
                queryset = queryset.filter(director__in = artist_obj)
            if filter_actor:
                url_str_list.append('filter_actor='+filter_actor)
                artist_obj = Artist.objects.filter(name_lower = filter_actor.lower())
                queryset = queryset.filter(starring__in = artist_obj)
        page = Pagination(queryset, page_no, 10)
        return page

class WatchListRetrieve(Resource):
    @marshal_with(resource_fields)
    @jwt_required
    def get(self, **kwargs):
        queryset = []
        global endpoint
        endpoint = 'watchlist'
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default = 1, location='args')
        page_no = parser.parse_args()['page']
        current_user_id = get_jwt_identity()
        profile_object = Profile.objects.get(id = current_user_id)
        watchlist_object = WatchList.objects.filter(owner = profile_object)
        if watchlist_object.count() > 0:
            queryset = Movie.objects.filter(id__in = [i.movie_id for i in watchlist_object[0].movie_list])
        page = Pagination(queryset, page_no, 10)
        return page

class WatchListAdd(Resource):
    @jwt_required
    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', required = True, type=str, location='args')
        if parser.parse_args():
            current_user_id = get_jwt_identity()
            movie_id = parser.parse_args()['movie_id']
            profile_obj = Profile.objects.get(id = current_user_id)
            movie_obj = Movie.objects.get(id = movie_id)
            watchlist_obj = WatchList.objects.filter(owner = profile_obj)
            if not watchlist_obj:
                watchlist_obj = WatchList(owner = profile_obj, movie_list = [MovieData(movie_id = movie_obj.id)])
                watchlist_obj.save()
                response = jsonify({'success': True, 'message': 'Movie successfully added to watchlist.'})
                response.status_code = 200
            else:
                if watchlist_obj.filter(movie_list__movie_id = movie_obj.id).count() == 0:
                    watchlist_obj = watchlist_obj[0]
                    movie_list = watchlist_obj.movie_list[:]
                    movie_data = MovieData(movie_id = movie_obj.id)
                    movie_list.append(movie_data)
                    watchlist_obj.movie_list = movie_list
                    watchlist_obj.save()
                    response = jsonify({'success': True, 'message': 'Movie successfully added to watchlist.'})
                    response.status_code = 200
                else:
                    response = jsonify({'success': False, 'message': 'Movie already on watchlist.'})
                    response.status_code = 409
            return response

class WatchListRemove(Resource):
    @jwt_required
    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', required = True, type=str, location='args')
        if parser.parse_args():
            current_user_id = get_jwt_identity()
            movie_id = parser.parse_args()['movie_id']
            profile_obj = Profile.objects.get(id = current_user_id)
            # movie_obj = Movie.objects.get(id = movie_id)
            watchlist_obj = WatchList.objects.filter(owner = profile_obj)
            if watchlist_obj.filter(movie_list__movie_id = movie_id).count() > 0:
                watchlist_obj = watchlist_obj[0]
                movie_list = watchlist_obj.movie_list[:]
                movie_dict = [i for i in movie_list if str(i['movie_id']) == movie_id][0]
                movie_list.remove(movie_dict)
                watchlist_obj.movie_list = movie_list
                watchlist_obj.save()
                response = jsonify({'success': True, 'message': 'Movie successfully removed from watchlist.'})
                response.status_code = 200
            else:
                response = jsonify({'success': False, 'message': 'Movie not on watchlist.'})
                response.status_code = 409
            return response

class LikedListRetrieve(Resource):
    @marshal_with(resource_fields)
    @jwt_required
    def get(self, **kwargs):
        queryset = []
        global endpoint
        endpoint = 'liked_list'
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int, default = 1, location='args')
        page_no = parser.parse_args()['page']
        current_user_id = get_jwt_identity()
        profile_object = Profile.objects.get(id = current_user_id)
        likedlist_object = LikedList.objects.filter(owner = profile_object)
        if likedlist_object.count() > 0:
            queryset = Movie.objects.filter(id__in = [i['movie_id'] for i in likedlist_object[0].movie_list])
        page = Pagination(queryset, page_no, 10)
        return page

class LikedListAdd(Resource):
    @jwt_required
    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', required = True, type=str, location='args')
        if parser.parse_args():
            current_user_id = get_jwt_identity()
            movie_id = parser.parse_args()['movie_id']
            profile_obj = Profile.objects.get(id = current_user_id)
            movie_obj = Movie.objects.get(id = movie_id)
            likedlist_obj = LikedList.objects.filter(owner = profile_obj)
            if not likedlist_obj:
                likedlist_obj = LikedList(owner = profile_obj, movie_list = [MovieData(movie_id = movie_obj.id)])
                likedlist_obj.save()
                response = jsonify({'success': True, 'message': 'Movie liked.'})
                response.status_code = 200
            else:
                if likedlist_obj.filter(movie_list__movie_id = movie_obj.id).count() == 0:
                    likedlist_obj = likedlist_obj[0]
                    movie_list = likedlist_obj.movie_list[:]
                    movie_data = MovieData(movie_id = movie_obj.id)
                    movie_list.append(movie_data)
                    likedlist_obj.movie_list = movie_list
                    likedlist_obj.save()
                    response = jsonify({'success': True, 'message': 'Movie liked'})
                    response.status_code = 200
                else:
                    response = jsonify({'success': False, 'message': 'Movie already liked.'})
                    response.status_code = 409
            return response

class LikedListRemove(Resource):
    @jwt_required
    def post(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', required = True, type=str, location='args')
        if parser.parse_args():
            current_user_id = get_jwt_identity()
            movie_id = parser.parse_args()['movie_id']
            profile_obj = Profile.objects.get(id = current_user_id)
            # movie_obj = Movie.objects.get(id = movie_id)
            likedlist_obj = LikedList.objects.filter(owner = profile_obj)
            if likedlist_obj.filter(movie_list__movie_id = movie_id).count() > 0:
                likedlist_obj = likedlist_obj[0]
                movie_list = likedlist_obj.movie_list[:]
                movie_dict = [i for i in movie_list if str(i['movie_id']) == movie_id][0]
                movie_list.remove(movie_dict)
                likedlist_obj.movie_list = movie_list
                likedlist_obj.save()
                response = jsonify({'success': True, 'message': 'Movie successfully unliked.'})
                response.status_code = 200
            else:
                response = jsonify({'success': False, 'message': 'Movie was not liked.'})
                response.status_code = 409
            return response

class MovieAdd(Resource):
    @jwt_required
    @admin_only
    def get(self, **kwargs):
        form = MovieAddForm()
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('movie_form.html', form=form), 200, headers)
    
    @jwt_required
    @admin_only
    def post(self, **kwargs):
        form = MovieAddForm()
        if isinstance(form.validate_on_submit(), Response):
            return form.validate_on_submit()
        parser = reqparse.RequestParser()
        parser.add_argument('name', required = True, type=str, location='form')
        parser.add_argument('director', required = True, type=str, location='form')
        parser.add_argument('genre', required = True, action = 'append', location='form')
        parser.add_argument('imdb_score', required = True, type=float, location='form')
        parser.add_argument('summary', required = True, type=str, location='form')
        parser.add_argument('release_date', required = True, type=str, location='form')
        if parser.parse_args():
            name = parser.parse_args()['name']
            director = parser.parse_args()['director']
            genre = parser.parse_args()['genre']
            imdb_score = parser.parse_args()['imdb_score']
            summary = parser.parse_args()['summary']
            release_date = parser.parse_args()['release_date']
            movie_exist = Movie.objects.filter(name_lower = name.lower())
            director_exist = Artist.objects.filter(name_lower = director.lower())
            if movie_exist and director_exist:
                response = jsonify({'success': 'False', 'message': 'Movie already exists.'})
                response.status_code = 409
                return response
            movie_object = Movie(name = name, imdb_score = imdb_score, summary = summary)
            try:
                release_date = datetime.strptime(release_date, '%d-%m-%Y')
                movie_object.release_date = release_date
            except ValueError:
                response = jsonify({'success': 'False', 'message': 'Date format incorrect'})
                response.status_code = 406
                return response
            director_obj = Artist.objects.filter(name_lower = director.lower())
            if director_obj:
                movie_object.director = director_obj[0]
            else:
                profession_obj = Profession.objects.get(profession_name = 'Director')
                director_obj = Artist(name = director, profession = [profession_obj])
                director_obj.save()
                movie_object.director = director_obj
            genre_objects = Genre.objects.filter(id__in = genre)
            movie_object.genre = list(genre_objects)
            current_user_id = get_jwt_identity()
            profile_object = Profile.objects.get(id = current_user_id)
            movie_object.added_by = profile_object
            movie_object.save()
            response_dict = {'success': True, 'message': 'Movie Saved', 'movie_data': movie_object}
            response = jsonify(marshal(response_dict, movie_save_fields))
            response.status_code = 201
            return response

class MovieUpdate(Resource):
    @jwt_required
    @admin_only
    def get(self, movie_id, **kwargs):
        movie_obj = Movie.objects.filter(id = movie_id)
        if not movie_obj:
            response = jsonify({'success': False, 'message': 'Movie not found'})
            response.status_code = 404
            return response
        movie_obj = movie_obj[0]
        form_dict = {}
        form_dict['name'] = movie_obj.name
        form_dict['director'] = movie_obj.director.name
        form_dict['genre'] = [str(i.id) for i in movie_obj.genre]
        form_dict['imdb_score'] = movie_obj.imdb_score
        form_dict['summary'] = movie_obj.summary
        method_name = 'put'
        if movie_obj.release_date:
            form_dict['release_date'] = movie_obj.release_date.date()
        form = MovieAddForm(**form_dict)
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('movie_form.html', form=form, method_name = method_name), 200, headers)
    
    @jwt_required
    @admin_only
    def post(self, movie_id, **kwargs):
        form = MovieAddForm()
        if isinstance(form.validate_on_submit(), Response):
            return form.validate_on_submit()
        parser = reqparse.RequestParser()
        parser.add_argument('name', required = True, type=str, location='form')
        parser.add_argument('director', required = True, type=str, location='form')
        parser.add_argument('genre', required = True, action = 'append', location='form')
        parser.add_argument('imdb_score', required = True, type=float, location='form')
        parser.add_argument('summary', required = True, type=str, location='form')
        parser.add_argument('release_date', required = True, type=str, location='form')
        if parser.parse_args():
            movie_object = Movie.objects.filter(id = movie_id)
            if not movie_object:
                response = jsonify({'success': False, 'message': 'Movie not found'})
                response.status_code = 404
                return response
            movie_object = movie_object[0]
            name = parser.parse_args()['name']
            director = parser.parse_args()['director']
            genre = parser.parse_args()['genre']
            imdb_score = parser.parse_args()['imdb_score']
            summary = parser.parse_args()['summary']
            release_date = parser.parse_args()['release_date']
            movie_exist = Movie.objects.filter(name_lower = name.lower(), id__ne = movie_id)
            director_exist = Artist.objects.filter(name_lower = director.lower())
            if movie_exist and director_exist:
                response = jsonify({'success': 'False', 'message': 'Movie already exists.'})
                response.status_code = 409
                return response
            change_made = False
            if movie_object.name != name:
                movie_object.name = name
                change_made = True
            if movie_object.imdb_score != imdb_score:
                movie_object.imdb_score = imdb_score
                change_made = True
            if movie_object.summary != summary:
                movie_object.summary = summary
                change_made = True
            try:
                release_date = datetime.strptime(release_date, '%d-%m-%Y')
                if movie_object.release_date != release_date:
                    movie_object.release_date = release_date
                    change_made = True
            except ValueError:
                response = jsonify({'success': 'False', 'message': 'Date format incorrect'})
                response.status_code = 406
                return response
            director_obj = Artist.objects.filter(name_lower = director.lower())
            if director_obj:
                if movie_object.director != director_obj[0]:
                    movie_object.director = director_obj[0]
                    change_made = True
            else:
                profession_obj = Profession.objects.get(profession_name = 'Director')
                director_obj = Artist(name = director, profession = [profession_obj])
                director_obj.save()
                movie_object.director = director_obj
                change_made = True
            genre_objects = Genre.objects.filter(id__in = genre)
            if set(movie_object.genre) != set(list(genre_objects)):
                movie_object.genre = list(genre_objects)
                change_made = True
            if change_made:
                current_user_id = get_jwt_identity()
                profile_object = Profile.objects.get(id = current_user_id)
                movie_object.last_changed_by = profile_object
                movie_object.save()
            response_dict = {'success': True, 'message': 'Movie Saved', 'movie_data': movie_object}
            response = jsonify(marshal(response_dict, movie_save_fields))
            return response

class MovieDelete(Resource):
    @jwt_required
    @admin_only
    def delete(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('movie_id', required = True, type=str, location='args')
        if parser.parse_args():
            movie_id = parser.parse_args()['movie_id']
            movie_object = Movie.objects.filter(id = movie_id)
            if not movie_object:
                response = jsonify({'success': False, 'message': 'Movie not found'})
                response.status_code = 404
                return response
            movie_object.delete()
            response = jsonify({'success': True, 'message': 'Movie Deleted'})
            return response