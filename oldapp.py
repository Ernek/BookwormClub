import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from forms import UserAddForm, LoginForm, UserEditForm
from models import db, connect_db, User, Book, Read

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///bookclub'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                # image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    do_logout()
    flash("You have successfully logged out", "success")
    return redirect("/login")   


##############################################################################
# General user routes:
# This route uses "index.html" and can be loaded by typing the route /users only 
@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    # if not search:
    users = User.query.all()
    # print(users)
    # else:
    #     users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""
    if g.user.id != user_id:
        flash(f"You are not User {user_id}, you are User {g.user.id}", "danger")
        return redirect('/')
    else:
        user = User.query.get_or_404(user_id)
        books = Book.query.all()
    return render_template('users/show.html', user=user, books=books)


# Profile page 
@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""
    #Check if user is logged on correctly
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = UserEditForm()
    
    if form.validate_on_submit():

        user = User.authenticate(g.user.username,
                                 form.password.data)

        if not user:
        # if g.user.password != form.password.data:
            flash("Password does not match", "danger")
            # I prefered that we stay in the same form and just flag the error
            # on the password so one can retype it correctly 
            return render_template('users/edit.html', form=form)

        if form.username.data and (form.username.data != g.user.username):
            if (db.session.query(User).filter_by(username=form.username.data).count() > 0):
                flash("Username already taken", 'danger')
                return render_template('users/edit.html', form=form)
        if form.username.data and (form.email.data != g.user.email):
            if (db.session.query(User).filter_by(email=form.email.data).count() > 0):   
                flash("Email already taken", 'danger')
                return render_template('users/edit.html', form=form)

        try:
            if form.username.data:
                g.user.username = form.username.data
            if form.email.data:
                g.user.email = form.email.data
            if form.location.data:
                g.user.location = form.location.data
            if form.bio.data:
                g.user.bio = form.bio.data

            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/edit.html', form=form)


        return render_template('users/show.html', user=g.user)

    return render_template('users/edit.html', form=form)
        


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")

##############################################################################
# Books routes:
@app.route('/users/books/addread/<int:book_id>', methods=['POST'])
def add_book_to_read(book_id):
    """Add a book from the book club suggestions to reads"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_object = Book.query.get_or_404(book_id)
    
    read_entry = Read(user_id=g.user.id, book_id=book_object.id)
    g.user.reads.append(read_entry)
    db.session.add(g.user)
    db.session.commit()

    return redirect(f"/")

@app.route('/users/books/deleteread/<int:book_id>', methods=['POST'])
def delete_book_to_read(book_id):
    """Delete a book from your reads"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    read_object = db.session.query(Read).filter_by(user_id=g.user.id, book_id=book_id).first()
    if read_object:
        db.session.delete(read_object)
        db.session.commit()
    else:
        flash("No matching row found to delete.", "danger")

    return redirect(f"/")

@app.route('/booksread/add', methods=['POST'])
def add_bookread():
    """Add any book to the books read"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if request.method == 'POST':
        title = request.form['booktitle']
        imgurl = request.form['bookimage']
        
        if title and imgurl:
            book_object = Book(booktitle=title, bookimag_url=imgurl)
            db.session.add(book_object)
            db.session.commit()
            read_entry = Read(user_id=g.user.id, book_id=book_object.id)
            g.user.reads.append(read_entry)

            db.session.add(g.user)
            db.session.commit()

            return redirect(f"/")
        elif title: # Title is mandatory
            book_object = Book(booktitle=title)
            db.session.add(book_object)
            db.session.commit()
    
            read_entry = Read(user_id=g.user.id, book_id=book_object.id)
            g.user.reads.append(read_entry)

            db.session.add(g.user)
            db.session.commit()
        else:
            flash("Need to add a booktitle", "danger")
    
    return redirect(f"/")

@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book_from_database(book_id):
    """Delete a book from the database"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    book_object = Book.query.get_or_404(book_id)
    if book_object:
        db.session.delete(book_object)
        db.session.commit()
    else:
        flash("No matching row found to delete.", "danger")

    return redirect(f"/")

##############################################################################
# Comments routes:

# @app.route('/comments/new', methods=["GET", "POST"])
# def messages_add():
#     """Add a comment on a book:

#     Show form if GET. If valid, update message and redirect to user page.
#     """

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     form = CommentForm()

#     if form.validate_on_submit():
#         comment = Comment(text=form.text.data)
#         g.user.comments.append(comment)
#         db.session.commit()

#         return redirect(f"/users/{g.user.id}")

#     return render_template('comments/new.html', form=form)


# @app.route('/messages/<int:message_id>/delete', methods=["POST"])
# def messages_destroy(message_id):
#     """Delete a message."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     msg = Message.query.get(message_id)
#     db.session.delete(msg)
#     db.session.commit()

#     return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:
    """

    if g.user:
        # Query Books table using the database library
        books_table = db.session.query(Book).all()

        # Store the data in g 
        g.books_table = books_table

        g.user_reads = db.session.query(Read).filter_by(user_id=g.user.id).all()
        
        read_book_ids = [] 
        for read in g.user_reads:
            read_book_ids.append(read.book_id)
        print(read_book_ids)
        g.read_book_ids = read_book_ids
        # print(g.user_reads)
        # print(g.user.reads)
        # messages = (Message
        #             .query
        #             .filter(Message.user_id.in_([g.user.id] + [f.id for f in g.user.following]))
        #             .order_by(Message.timestamp.desc())
        #             .limit(100)
        #             .all())




        return render_template('home.html')

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
