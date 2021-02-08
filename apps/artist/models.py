from werkzeug.wrappers import ETagRequestMixin
from mongoengine import Document, StringField, ReferenceField,\
                        ListField, ImageField
from mongoengine.fields import DateTimeField

class Profession(Document):
    profession_name = StringField(required = True)

class Artist(Document):
    name = StringField(required = True)
    profession = ListField(ReferenceField(Profession), required = True)
    date_of_birth = DateTimeField()
    display_picture = ImageField()
    name_lower = StringField()

    def save(self, *args, **kwargs):
        if not self.name_lower:
            self.name_lower = self.name.lower().strip()
        return super(Artist, self).save(*args, **kwargs)
