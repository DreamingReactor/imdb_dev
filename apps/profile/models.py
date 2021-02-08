from mongoengine import Document, StringField, BooleanField,\
                        ImageField
from mongoengine.fields import DateTimeField
from datetime import datetime

class Profile(Document):
    name = StringField(required = True)
    username = StringField(required = True, unique = True)
    password = StringField(required = True)
    display_picture = ImageField()
    is_admin = BooleanField(default = False)
    registeration_date = DateTimeField(default = datetime.now)
    last_login = DateTimeField()

