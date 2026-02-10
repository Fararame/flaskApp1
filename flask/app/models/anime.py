from app import db
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime


anime_genres = db.Table('anime_genres',
   db.Column('anime_id', db.Integer, db.ForeignKey('animes.id'), primary_key=True),
   db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)




class Genre(db.Model, SerializerMixin):
   __tablename__ = 'genres'
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(50), unique=True, nullable=False)


   # Exclude animes from serialization to avoid recursion
   serialize_rules = ('-animes',)


   def __init__(self, name):
       self.name = name




class Anime(db.Model, SerializerMixin):
   __tablename__ = 'animes'
   id = db.Column(db.Integer, primary_key=True)
   mal_id = db.Column(db.Integer, unique=True)
   title_english = db.Column(db.String(255))
   image_url = db.Column(db.String(512))
   year = db.Column(db.Integer)
   episodes = db.Column(db.Integer)
   synopsis = db.Column(db.Text)
   score = db.Column(db.Float)
   my_rating = db.Column(db.Integer, default=0)
   deleted_at = db.Column(db.DateTime, nullable=True)
  
   # Many-to-Many relationship
   genres = db.relationship('Genre', secondary=anime_genres,
                            backref=db.backref('animes', lazy='dynamic'))


   # Exclude the complex relationship from default serialization to avoid recursion
   serialize_rules = ('-genres',)


   def __init__(self, mal_id, title_english, image_url, year, 
                episodes, synopsis, score, my_rating=0, deleted_at=None):
       self.mal_id = mal_id
       self.title_english = title_english
       self.image_url = image_url
       self.year = year
       self.episodes = episodes
       self.synopsis = synopsis
       self.score = score
       self.my_rating = my_rating
       self.deleted_at = deleted_at


   def to_dict(self, rules=None, **kwargs):
       # Override to_dict to return genres as a simple list of strings 
       # (matching JSON format)
       d = super().to_dict(rules=rules, **kwargs)
       d['genres'] = [g.name for g in self.genres]
       return d