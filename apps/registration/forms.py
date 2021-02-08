from flask import jsonify
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired
from apps.profile.models import Profile

class RegisterForm(FlaskForm):
    name = TextField('Full Name', validators=[DataRequired()])
    username = TextField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    display_picture = FileField('Display Picture', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])

    def validate_on_submit(self):
        if self.password.data != self.confirm_password.data:
            response = jsonify({'success': 'False', 'message': 'Password don\'t match'})
            response.status_code = 406
            return response
        return super(RegisterForm,self).validate_on_submit()
