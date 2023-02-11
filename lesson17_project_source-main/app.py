from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


api = Api(app)
movie_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesViews(Resource):

    def get(self):
        movies_query = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id is not None:
            movies_query = movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies_query = movies_query.filter(Movie.genre_id == genre_id)

        if director_id is not None and genre_id is not None:
            movies_query = Movie.query.filter(Movie.director_id == director_id, Movie.genre_id == genre_id)

        return movies_schema.dump(movies_query.all()), 200

    def post(self):

        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)

        return "User is created", 201


@movie_ns.route('/<int:uid>')
class MoviesViews(Resource):
    def get(self, uid):

        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "User is not found", 404

        return movie_schema.dump(movie), 200

    def put(self, uid):

        add_rows = db.session.query(Movie).filter(Movie.id == uid).update(request.json)
        if add_rows != 1:
            return "User is not update", 400

        db.session.commit()

        return "User is updated", 204

    def delete(self, uid):

        movie = db.session.query(Movie).get(uid)
        if not movie:
            return "User is not found", 404
        db.session.delete(movie)
        db.session.commit()


@directors_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        db.session.add(new_director)
        db.session.commit()

        return "Director is created", 201


@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):

        director = db.session.query(Director).get(uid)
        if not director:
            return "Director is not found", 404
        all_movies = db.session.query(Movie).all()
        director_of_movie = []
        for mov in all_movies:
            if mov.genre_id == uid:
                director_of_movie.append(movie_schema.dump(mov))

        return [director_schema.dump(director), director_of_movie], 200

    def put(self, uid):

        director = Director.query.get(uid)
        if not director:
            return "Director is not found", 404
        req_json = request.json
        if "name" in req_json:
            director.id = req_json.get("id")
            director.name = req_json.get("name")
        db.session.add(Director)
        db.session.commit()

        return "Director is updated", 204

    def delete(self, uid):
        director = db.session.query(Director).get(uid)
        if not director:
            return "Director is not found", 404

        db.session.delete(director)
        db.session.commit()

        return "Director is deleted", 204


@genres_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        db.session.add(new_genre)
        db.session.commit()

        return "Genre is created", 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):
    def get(self, uid):

        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "Not found", 404
        all_movies = db.session.query(Movie).all()
        movie_in_genre = []
        for mov in all_movies:
            if mov.genre_id == uid:
                movie_in_genre.append(movie_schema.dump(mov))

        return [genre_schema.dump(genre), movie_in_genre], 200

    def put(self, uid):

        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "Not Found", 404
        req_json = request.json
        if "name" in req_json:
            genre.id = req_json.get("id")
            genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()

        return "Genre is updated", 204

    def delete(self, uid):

        genre = db.session.query(Genre).get(uid)
        if not genre:
            return "Not Found", 404
        db.session.delete(genre)
        db.session.commit()

        return "Genre is deleted", 201


if __name__ == '__main__':
    app.run(debug=True)
