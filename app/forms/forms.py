from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, BooleanField,
                     RadioField, EmailField, PasswordField)
from wtforms.validators import InputRequired, Length, Email, EqualTo, Regexp


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),
                                             Length(min=10, max=100)])
    description = TextAreaField('Course Description',
                                validators=[InputRequired(),
                                            Length(max=200)])
    price = IntegerField('Price', validators=[InputRequired()])
    level = RadioField('Level',
                       choices=['Beginner', 'Intermediate', 'Advanced'],
                       validators=[InputRequired()])
    available = BooleanField('Available', default='checked')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(),
                                                   Length(min=2, max=100)])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Regexp(Regexp)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), 
                                                                     EqualTo('confirm', message='Passwords must match')])