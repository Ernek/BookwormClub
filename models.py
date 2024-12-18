"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()


class Book(db.Model):
    """A Book read by the BookClub members."""

    __tablename__ = 'books'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    booktitle = db.Column(
        db.String(200),
        nullable=False,
    )
    bookauthor = db.Column(
        db.String(200),
    )

    bookimag_url = db.Column(
        db.Text,
        default="/static/images/book_logo.png",
    )

    users_read = db.relationship('Read', cascade="all, delete-orphan")

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )
    
    reads = db.relationship('Read', back_populates='user', cascade="all, delete-orphan")


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"


    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        
        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    @property
    def books_read(self):
        """Get all books read by the user."""
        return [read.book for read in self.reads]

class Read(db.Model):
    """Accounts of books read by each user."""

    __tablename__ = 'reads'

    id = db.Column(
        db.Integer, 
        primary_key=True)
    
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade'),
        nullable=False,
    )
    
    book_id = db.Column(
        db.Integer,
        db.ForeignKey('books.id', ondelete='cascade'),
        nullable=False,
    )

    user = db.relationship('User')
    book = db.relationship('Book')

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)
