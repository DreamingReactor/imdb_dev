from apps.artist.models import Artist
from apps.movie.models import Movie
from flask import jsonify
from flask_restful import Resource, fields, marshal_with, marshal, reqparse
from flask_mongoengine import Pagination

class Search(Resource):
    def get(self, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument('search_str', required = True, type=str, location='args')
        if parser.parse_args():
            search_str = parser.parse_args()['search_str']
            result = {'movies': [], "artists": []}
            suggestion = {'movies': [], "artists": []}
            if len(search_str) > 2:
                movie_obj = Movie.objects.filter(name_lower = search_str.lower())
                artist_obj = Artist.objects.filter(name_lower = search_str.lower())
                movie_obj_partial = Movie.objects.filter(name_lower__contains = search_str.lower())
                artist_obj_partial = Artist.objects.filter(name_lower__contains = search_str.lower())
                if movie_obj:
                    for movie in movie_obj:
                        result['movies'].append({'id': str(movie.id), 'name': movie.name})
                if artist_obj:
                    for artist in artist_obj:
                        result['artists'].append({'id': str(artist.id), 'name': artist.name})  
                if movie_obj_partial:
                    for movie in movie_obj_partial:
                        suggestion['movies'].append({'id': str(movie.id), 'name': movie.name})
                if artist_obj_partial:
                    for artist in artist_obj_partial:
                        suggestion['artists'].append({'id': str(artist.id), 'name': artist.name})
            
            return jsonify({'success': True, 'result': result, 'suggestion': suggestion})
                

            
