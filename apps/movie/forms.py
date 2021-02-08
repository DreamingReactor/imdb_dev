from flask import jsonify, Flask
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectMultipleField, FieldList, TextAreaField, DateField
from wtforms.validators import DataRequired
from mongoengine import connect
from .models import Genre, Movie
from apps.artist.models import Artist
from flask_mongoengine import MongoEngine
from datetime import date

def get_genre_choices():
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        'db': 'fynd_imdb',
        # 'username':'root',
        # 'password':'root'
    }
    MongoEngine(app)
    genre_obj = Genre.objects.filter()
    genre_choices = [(i.id, i.genre_str) for i in genre_obj]

    return genre_choices

class MovieAddForm(FlaskForm):

    name = StringField('Movie Name', validators=[DataRequired()])
    director = StringField('Director', validators=[DataRequired()])
    genre = SelectMultipleField('Genre', validators=[DataRequired()], choices = get_genre_choices())
    imdb_score = DecimalField('IMDB Rating', validators=[DataRequired()])
    summary = TextAreaField('Movie Summary')
    release_date = DateField('Release Date(DD-MM-YYYY)', format = '%d-%m-%Y')
    method_name = StringField(validators=[DataRequired()], default = 'post')

    def validate_on_submit(self):
        if not self.imdb_score.data or self.imdb_score.data < 0 or self.imdb_score.data > 10:
            response = jsonify({'success': 'False', 'message': 'IMDB Rating should be between 1 and 10'})
            response.status_code = 406
            return response
        if not isinstance(self.release_date.data, date):
            response = jsonify({'success': 'False', 'message': 'Date format incorrect'})
            response.status_code = 406
            return response
        return super(MovieAddForm,self).validate_on_submit()

