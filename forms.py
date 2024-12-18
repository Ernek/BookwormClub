from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional


# class CommentForm(FlaskForm):
#     """Form for adding/editing comments on specific books."""

#     text = TextAreaField('text', validators=[DataRequired()])

class BookAddForm(FlaskForm):
    """Form for books."""

    booktitle = StringField('BookTitle', validators=[DataRequired()])
    image_url = StringField('(Optional) Book Image URL')


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    # image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form for adding users."""

    username = StringField('New Username')
    email = StringField('New E-mail', validators=[Optional(), Email()])
    # image_url = StringField('(Optional) Image URL')
    # header_image_url = StringField('(Optional) Header Image URL')
    bio = StringField('(Optional) Bio')
    location = StringField('(Optional) Location')
    password = PasswordField('Password', validators=[Length(min=6)])
    
