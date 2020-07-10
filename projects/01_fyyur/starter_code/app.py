# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

# import json
from datetime import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request,\
                  Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
# from flask_wtf import Form
from flask_migrate import Migrate

from forms import ShowForm, VenueForm, ArtistForm

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=True)
    shows = db.relationship('Show', backref='venues', lazy=True)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venu = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String, nullable=True)
    shows = db.relationship('Show', backref='artists', lazy=True)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
    start_time = db.Column(db.Date)

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    venues = Venue.query.all()
    data = []
    upcoming_shows = []

    current_time = datetime.now()

    for venue in venues:
        upcoming_shows = db.session.query(Show).join(
            Venue
        ).filter(
           Show.venue_id == venue.id
        ).filter(Show.start_time > current_time).all()

        data.append({
            'city': venue.city,
            'state': venue.state,
            'venues': [{
                'id': venue.id,
                'name': venue.name,
                'num_upcoming_shows': len(upcoming_shows)
            }]
        })

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    data = []
    search = request.form.get('search_term')
    venues = Venue.query.all()

    for venue in venues:
        if search.lower() in venue.name.lower():
            data.append(venue)

    response = {
        'count': len(data),
        'data': data,
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', ''),
    )


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    past_shows = []
    upcoming_shows = []
    venue = Venue.query.get(venue_id)

    current_time = datetime.now()

    past_shows = db.session.query(Show).join(
        Venue
       ).filter(
           Show.venue_id == venue_id
       ).filter(Show.start_time < current_time).all()

    upcoming_shows = db.session.query(Show).join(
        Venue
       ).filter(
           Show.venue_id == venue_id
       ).filter(Show.start_time > current_time).all()

    data = {
        'id': venue_id,
        'name': venue.name,
        'genres': venue.genres,
        'address': venue.address,
        'city': venue.city,
        'state': venue.state,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }

    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    venue_data = {}
    venue_data['name'] = request.form.get('name')
    venue_data['city'] = request.form.get('city')
    venue_data['state'] = request.form.get('state')
    venue_data['address'] = request.form.get('address')
    venue_data['genres'] = request.form.getlist('genres')
    venue_data['phone'] = request.form.get('phone')
    venue_data['facebook_link'] = request.form.get('facebook_link')
    try:
        venue = Venue(
            name=venue_data['name'],
            city=venue_data['city'],
            state=venue_data['state'],
            address=venue_data['address'],
            genres=venue_data['genres'],
            phone=venue_data['phone'],
            facebook_link=venue_data['facebook_link']
        )
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' was unsuccessfully listed!')
        print(ex)
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception as ex:
        db.session.rollback()
        print(ex)
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to
    #                  delete a Venue on a Venue Page, have it so that
    #                  clicking that button delete it from the db then
    #                  redirect the user to the homepage
    return Response(response=None, status=200)


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append(
            {
                'id': artist.id,
                'name': artist.name
            }
        )
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    data = []
    search = request.form.get('search_term')
    artists = Artist.query.all()

    for artist in artists:
        if search.lower() in artist.name:
            data.append(artist)

    response = {
        'count': len(data),
        'data': data,
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', ''),
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    past_shows = []
    upcoming_shows = []
    artist = Artist.query.get(artist_id)

    current_time = datetime.now()

    past_shows = db.session.query(Show).join(
        Venue
       ).filter(
           Show.artist_id == artist_id
       ).filter(Show.start_time < current_time).all()

    upcoming_shows = db.session.query(Show).join(
        Venue
       ).filter(
           Show.artist_id == artist_id
       ).filter(Show.start_time > current_time).all()

    data = {
        'id': artist_id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_talent': artist.seeking_venu,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)

    artist_data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website': artist.website,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venu,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link
    }

    return render_template(
        'forms/edit_artist.html',
        form=form,
        artist=artist_data
    )


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    data = {}
    data['name'] = request.form.get('name')
    data['city'] = request.form.get('city')
    data['state'] = request.form.get('state')
    data['phone'] = request.form.get('phone')
    data['genres'] = request.form.getlist('genres')
    data['facebook_link'] = request.form.get('facebook_link')

    artist = Artist.query.get(artist_id)

    try:
        artist.name = data['name']
        artist.city = data['city']
        artist.state = data['state']
        artist.phone = data['phone']
        artist.genres = data['genres']
        artist.facebook_link = data['facebook_link']
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception as ex:
        db.session.rollback()
        flash('Artist ' +
              request.form['name']
              + ' was unsuccessfully updated!')
        print(ex)
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)

    venue_data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'website': venue.website,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link
    }

    return render_template(
        'forms/edit_venue.html',
        form=form,
        venue=venue_data
    )


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    data = {}
    data['name'] = request.form.get('name')
    data['city'] = request.form.get('city')
    data['state'] = request.form.get('state')
    data['address'] = request.form.get('address')
    data['phone'] = request.form.get('phone')
    data['genres'] = request.form.getlist('genres')
    data['facebook_link'] = request.form.get('facebook_link')

    venue = Venue.query.get(venue_id)

    try:
        venue.name = data['name']
        venue.city = data['city']
        venue.state = data['state']
        venue.adderss = data['adderss']
        venue.phone = data['phone']
        venue.genres = data['genres']
        venue.facebook_link = data['facebook_link']
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except Exception as ex:
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' was unsuccessfully updated!')
        print(ex)
    finally:
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
    artist_data = {}
    artist_data['name'] = request.form.get('name')
    artist_data['city'] = request.form.get('city')
    artist_data['state'] = request.form.get('state')
    artist_data['genres'] = request.form.getlist('genres')
    artist_data['phone'] = request.form.get('phone')
    artist_data['facebook_link'] = request.form.get('facebook_link')
    try:
        artist = Artist(
            name=artist_data['name'],
            city=artist_data['city'],
            state=artist_data['state'],
            genres=artist_data['genres'],
            phone=artist_data['phone'],
            facebook_link=artist_data['facebook_link']
        )
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception as ex:
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' was unsuccessfully listed!')
        print(ex)
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    data = []
    shows = Show().query.all()
    for show in shows:
        venue = Venue.query.get(show.venue_id)
        artist = Artist.query.get(show.artist_id)
        show_data = {
            'venue_id': show.venue_id,
            'venue_name': venue.name,
            'artist_id': show.artist_id,
            'artist_name': artist.name,
            'artist_image_link': artist.image_link,
            'start_time': show.start_time
        }
        data.append(show_data)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    show_data = {}
    show_data['artist_id'] = request.form.get('artist_id')
    show_data['venue_id'] = request.form.get('venue_id')
    show_data['start_time'] = request.form.get('start_time')

    try:
        show = Show(
            artist_id=show_data['artist_id'],
            venue_id=show_data['venue_id'],
            start_time=show_data['start_time']
        )
        db.session.add(show)
        db.session.commit()
        flash('Show successfully listed!')
    except Exception as ex:
        db.session.rollback()
        flash('Show unsuccessfully listed!')
        print(ex)
    finally:
        db.session.close()

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
        Formatter('%(asctime)s %(levelname)s: %(message)s\
            [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
