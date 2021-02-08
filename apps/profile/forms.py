from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = TextField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class AddAdminRollForm(FlaskForm):
    username = TextField('Email', validators=[DataRequired()])
    