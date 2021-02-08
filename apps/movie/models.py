from mongoengine import Document, StringField, ReferenceField, ObjectIdField,\
                        ListField, FloatField, ImageField, EmbeddedDocumentField, EmbeddedDocument
from mongoengine.fields import DateTimeField
from apps.artist.models import Artist
from apps.profile.models import Profile
from datetime import datetime
from bson.objectid import ObjectId

class Genre(Document):
    genre_str = StringField(required = True)

class Movie(Document):
    name = StringField(required = True)
    director = ReferenceField(Artist, required = True)
    genre = ListField(ReferenceField(Genre), required = True)
    imdb_score = FloatField(required = True)
    summary = StringField()
    starring = ListField(ReferenceField(Artist))
    release_date = DateTimeField()
    name_lower = StringField()
    added_by = ReferenceField(Profile)
    last_changed_by = ReferenceField(Profile)
    images = ListField(ImageField())

    meta = {'ordering': ['-imdb_score']}

    def save(self, *args, **kwargs):
        if not self.name_lower:
            self.name_lower = self.name.lower().strip()
        return super(Movie, self).save(*args, **kwargs)

class MovieData(EmbeddedDocument):
    movie_id = ObjectIdField(required = True, unique = True)
    added_on = DateTimeField(default = datetime.now)

class WatchList(Document):
    owner = ReferenceField(Profile, required = True, unique = True)
    movie_list = ListField(EmbeddedDocumentField(MovieData))


class LikedList(Document):
    owner = ReferenceField(Profile, required = True, unique = True)
    movie_list = ListField(EmbeddedDocumentField(MovieData))
