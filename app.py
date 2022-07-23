#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from pkg_resources import require
from forms import *
from flask_migrate import Migrate
from model import app, db, Venue, Artist, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database

migrate = Migrate(app,db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # Queries the database to render the view point a display of venues within
  query_table = Venue.query.distinct(Venue.city, Venue.state).all()
  data = []
  for view in query_table:
    new = Venue.query.filter(Venue.state == view.state).filter(Venue.city == view.city).all()
    new_data = []
    for result in new:
          new_data.append({
            'id': result.id,
            'name': result.name,
            'num_upcoming_shows': len(db.session.query(Show).filter(Show.start_time > datetime.now()).all())
          })
    data.append({
      'city': view.city,
      'state': view.state,
      'venues': new_data
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  value_gotten = request.form.get('search_term') # receives search value from the user
  response = []
  print(value_gotten)
  value_to_query = '%{}%'.format(value_gotten) # converts the value received to a string
  raw_data = db.session.query(Venue).filter(Venue.name.ilike( value_to_query)).all() # queries the database 
  for data in raw_data:
    print(value_to_query, data)

    response.append({
        'id': data.id,
        'name': data.name,
        'num_upcoming_shows':len(db.session.query(Show).filter(Show.venue_id == data.id).filter(Show.start_time > datetime.now()).all())
    })
    # returns query response from the database
  pro_data = {
    'count': len(raw_data),
    'data': response
  }
  
  
  return render_template('pages/search_venues.html', results=pro_data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  show_venue = Venue.query.get(venue_id)
  upcoming_show = db.session.query(Show).join(Artist).filter(Show.venue_id ==venue_id).filter(Show.start_time > datetime.now()).all()
  print(upcoming_show)
  data_for_upcoming = []
  for show in upcoming_show:
    data_for_upcoming.append({
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time
    })
    print(data_for_upcoming)
  print(sys.exc_info)
  data_for_past =[]
  past_show = db.session.query(Show).join(Artist).filter(Show.venue_id ==venue_id).filter(Show.start_time < datetime.now()).all()
  for show in past_show:
        data_for_past.append({
          "artist_id": show.artist_id,
          "artist_name": show.Artist.name,
          "artist_image_link": show.Artist.image_link,
          "start_time": show.start_time
        })
        # returns data to the view after querying the venue_id
  output = {
        "id": show_venue.id,
        "name": show_venue.name,
        "genres": [show_venue.genres],
        "city": show_venue.city,
        "address": show_venue.address,
        "state": show_venue.state,
        "phone": show_venue.phone,
        "website": show_venue.website_link,
        "facebook_link": show_venue.facebook_link,
        "seeking_talent": show_venue.seeking_talent,
        "seeking_description": show_venue.seeking_description,
        "image_link": show_venue.image_link,
        "past_shows": data_for_past,
        "past_shows_count":len(data_for_past),
        "upcoming_shows": data_for_upcoming,
        "upcoming_shows_count": len(data_for_upcoming),
  }
 
  return render_template('pages/show_venue.html', venue=output)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  # receives form data from the view to be committed to the database
  try:
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data,
                facebook_link=form.facebook_link.data, website_link=form.website_link.data, seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data)
    db.session.add(venue)
    db.session.commit()
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    # if an error undo add and display an error message
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    # when done close
    db.session.close()
  
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  # deletes a venue from the database
  try:
    Venue.query.filter(Venue.id==venue_id).delete()
    db.session.commit()
    flash('Successfully removed')
  except:
    db.session.rollback()
    flash('An eror occurred while deleting')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  value_gotten = request.form.get('search_term') # receives search value from user
  print(value_gotten)
  response = []
  value_to_query = '%{}%'.format(value_gotten) # converts value received to string
  raw_data = db.session.query(Artist).filter(Artist.name.ilike( value_to_query)).all() # queries the database
  for data in raw_data:
    print(value_to_query, data)
    # returns result to the view
    response.append({
        'id': data.id,
        'name': data.name,
        'num_upcoming_shows':len(db.session.query(Show).filter(Show.venue_id == data.id).filter(Show.start_time > datetime.now()).all())
    })
  pro_data = {
    'count': len(raw_data),
    'data': response
  }
  return render_template('pages/search_artists.html', results=pro_data, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  show_artist = db.session.query(Artist).get(artist_id)
  upcoming_show = db.session.query(Show).join(Venue).filter(Show.artist_id ==artist_id).filter(Show.start_time > datetime.now()).all()
  print(upcoming_show)
  data_for_upcoming = []
  for show in upcoming_show:
    data_for_upcoming.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "venue_image_link": show.Venue.image_link,
      "start_time": show.start_time
    })
    print(data_for_upcoming)
  print(sys.exc_info)
  data_for_past =[]
  past_show = db.session.query(Show).join(Venue).filter(Show.artist_id ==artist_id).filter(Show.start_time < datetime.now()).all()
  for show in past_show:
        data_for_past.append({
          "venue_id": show.venue_id,
          "venue_name": show.Venue.name,
          "venue_image_link": show.Venue.image_link,
          "start_time": show.start_time
        })
       # returns data to the view after querying the venue_id  
  output = {
        "id": show_artist.id,
        "name": show_artist.name,
        "genres": [show_artist.genres],
        "city": show_artist.city,
        "state": show_artist.state,
        "phone": show_artist.phone,
        "website": show_artist.website_link,
        "facebook_link": show_artist.facebook_link,
        "seeking_venue": show_artist.seeking_venue,
        "seeking_description": show_artist.seeking_description,
        "image_link": show_artist.image_link,
        "past_shows": data_for_past,
        "past_shows_count":len(data_for_past),
        "upcoming_shows": data_for_upcoming,
        "upcoming_shows_count": len(data_for_upcoming),
  }
 
  return render_template('pages/show_artist.html', artist=output)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists = Artist.query.get(artist_id)
  artist={
    "id": artist_id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website_link,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)
  

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  try:
    venue = Artist(name=form.name.data, city=form.city.data, state=form.state.data,
                    phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data, facebook_link=form.facebook_link.data,
                    website_link=form.website_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data)
    edit = Artist.query.get(artist_id)
    edit.name = venue.name
    edit.city = venue.city
    edit.state = venue.state
    edit.genres = venue.genres
    edit.phone = venue.phone
    edit.website_link = venue.website_link
    edit.facebook_link = venue.facebook_link
    edit.seeking_venue = venue.seeking_venue
    edit.seeking_description = venue.seeking_description
    edit.image_link = venue.image_link
    db.session.commit()
    flash('Successfully updated!')
  except:
    # if unsuccessful, flash an error instead
    db.session.rollback()
    print(sys.exc_info)
    flash('An error occurred. Change could not take effect.')
  finally:
    # when done close
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  venue={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm()
  try:
    venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, address=form.address.data,
                  phone=form.phone.data, image_link=form.image_link.data, genres=form.genres.data, facebook_link=form.facebook_link.data,
                  website_link=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
    edit = Venue.query.get(venue_id)
    edit.name = venue.name
    edit.city = venue.city
    edit.state = venue.state
    edit.genres = venue.genres
    edit.phone = venue.phone
    edit.website_link = venue.website_link
    edit.facebook_link = venue.facebook_link
    edit.seeking_talent = venue.seeking_talent
    edit.seeking_description = venue.seeking_description
    edit.image_link = venue.image_link
    db.session.commit()
    flash('Successfully updated!')
  except:
    # if unsuccessful, flash an error instead
    db.session.rollback()
    print(sys.exc_info)
    flash('An error occurred. Change could not take effect.')
  finally:
    # when done close
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm()
  try:
    artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=form.phone.data,
                    image_link=form.image_link.data, genres=form.genres.data, facebook_link=form.facebook_link.data,
                    website_link=form.website_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data)
    db.session.add(artist)
    db.session.commit()
            # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
     # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    # when done close
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data=[]
  for show in shows:
   # returns values of show afther querying the database
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.Venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link,
      "start_time": show.start_time
    })
      
    
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  try:
    shows = Show(artist_id=form.artist_id.data,
                 venue_id=form.venue_id.data,
                 start_time=form.start_time.data)
    db.session.add(shows)
    db.session.commit()
      # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
