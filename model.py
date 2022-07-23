
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


db = SQLAlchemy(app)
# Schema models for both the Venue, Artist and Show('also an association model)
class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    Show = db.relationship('Show', backref='Venue', lazy=True, cascade="all, delete, delete-orphan")

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    def __repr__(self):
           return f'<Venue ID: {self.id} name: {self.name} city: {self.city} state: {self.state} address: {self.address} phone: {self.phone} image_link: {self.image_link} facebook_link: {self.facebook_link} genres: {self.genres} website_link: {self.website_link} seeking_talent: {self.seeking_talent} seeking_description: {self.seeking_description}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    Show = db.relationship('Show', backref='Artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    def __repr__(self):
           return f'<Artist ID: {self.id} name: {self.name} city: {self.city} state: {self.state} phone: {self.phone} genres: {self.genres} image_link: {self.image_link} facebook_link: {self.facebook_link} website_link: {self.website_link} seeking_venue: {self.seeking_venue} seeking_description: {self.seeking_description}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
      __tablename__ = 'Show'
      
      id = db.Column(db.Integer, primary_key=True)
      artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
      venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
      start_time = db.Column(db.DateTime)
      
      def __repr__(self):
             return f'<Show ID: {self.id} artist_id: {self.artist_id} venue_id: {self.venue_id} start_time: {self.start_time}>'
      
      
