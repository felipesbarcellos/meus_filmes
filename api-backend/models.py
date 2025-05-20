from extensions import db
import datetime
import secrets
import string

LIST_ID_LENGTH = 10

def generate_random_list_id():
    alphabet = string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(LIST_ID_LENGTH))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class List(db.Model):
    id = db.Column(db.String(LIST_ID_LENGTH), primary_key=True, default=generate_random_list_id)
    name = db.Column(db.String(150), nullable=False)
    is_main = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('lists', lazy=True))

class MovieList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, nullable=False)
    list_id = db.Column(db.String(LIST_ID_LENGTH), db.ForeignKey('list.id'), nullable=False)
    lista = db.relationship('List', backref=db.backref('movies', lazy=True))

class Watched(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)
    watched_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.UTC))
    user = db.relationship('User', backref=db.backref('watched', lazy=True))

class Movie(db.Model):
    tmdb_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    overview = db.Column(db.Text, nullable=True)
    poster_path = db.Column(db.String(255), nullable=True)
    release_date = db.Column(db.Date, nullable=True)
    rating = db.Column(db.Float, nullable=True) # TMDB vote_average
    genres = db.Column(db.JSON, nullable=True) # Store as a list of genre objects or IDs

    def __repr__(self):
        return f'<Movie {self.tmdb_id} - {self.title}>'
