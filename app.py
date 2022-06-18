from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema

from db_create import create_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.url_map.strict_slashes = False
db = SQLAlchemy(app)

create_db()


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


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Str()
    genre_id = fields.Str()
    director_id = fields.Str()


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()
genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()
directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()

api = Api(app)
api.app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 4}
movies_ns = api.namespace('movies')
director_ns = api.namespace('director')
genres_ns = api.namespace('genres')


@movies_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        movies = Movie.query
        if director_id:
            movies = Movie.query.filter(Movie.director_id == director_id)
        if genre_id:
            movies = Movie.query.filter(Movie.genre_id == genre_id)
        res = movies.all()

        return movies_schema.dump(movies), 200


    def post(self):
        def post(self):
            res = request.json

            new_movie = Movie(**res)
            with db.session.begin():
                db.session.add(new_movie)

            return "", 201


@movies_ns.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        res = db.session.query(Movie).filter(Movie.id == mid).one()
        if not res:
            return '', 404
        return movie_schema.dump(res), 200

    def put(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return '', 404

        req_json = request.json

        movie.id = req_json.get('id')
        movie.title = req_json.get('title')
        movie.description = req_json.get('description')
        movie.trailer = req_json.get('trailer')
        movie.year = req_json.get('year')
        movie.rating = req_json.get('rating')
        movie.genre_id = req_json.get('genre_id')
        movie.director_id = req_json.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return '', 200

    def delete(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return '', 404

        db.session.delete(movie)
        db.session.commit()

        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
