import json
from app import app, errors
from app.functions import *
from flask import render_template, request, session, redirect
from werkzeug.contrib.cache import SimpleCache

from libz.ticketmaster import Ticketmaster
from libz.spotify import Spotify

spotifyObject = Spotify()
ticketmasterObject = Ticketmaster()
simpleCacheObject = SimpleCache()


@app.route('/')
@app.route('/home')
def home():
    if not spotifyObject.client_id or not spotifyObject.client_secret or not spotifyObject.redirect_uri:
        raise errors.EventLocatorException("Some of the core values are missing. Contact the admin.")

    if is_logged_in():
        all_artists = get_artists(spotifyObject)
        return render_template("main.html", username=session['username'], all_artists=all_artists)

    return render_template('login.html', auth_spotify_url=spotifyObject.get_authorisation_url())


@app.route('/login')
def login():
    if 'code' in request.args.keys():
        code = request.args['code']
        spotifyObject.set_token_info(code)
        spotifyObject.store_token_info()

        user = spotifyObject.get_user_information()
        username = user['display_name']
        session['username'] = username
    elif 'error' in request.args.keys():
        error = request.args['error']
        return render_template("login.html", error=error)

    return redirect('/home')


@app.route('/logout')
def logout():
    session['username'] = None
    spotifyObject.clear_cache()
    return redirect('/home')


@app.route('/concerts')
def concerts():
    if is_logged_in() is None:
        return redirect('/home')

    latitude = session.get('latitude', '')
    longitude = session.get('longitude', '')

    country_code = get_country_code(latitude, longitude)

    if country_code is None:
        raise errors.EventLocatorException('Location was not identified. Cannot find events.'
                                           'Please, check your browser settings.')

    all_artists = get_artists(spotifyObject)
    artist_names = [artist['name'].replace(' ', '+') for artist in all_artists]

    events = ticketmasterObject.get_events(artist_names, country_code)
    if events is None:
        raise errors.EventLocatorException('Cannot find any events nearby')

    return render_template('concerts.html', events=events)


@app.route('/store_location', methods=['POST'])
def store_location():

    if request.method == 'POST':
        latitude = request.form.get('latitude', '')
        longitude= request.form.get('longitude', '')

        if latitude and longitude:
            status = 'ok'
            message = ''
            session['latitude'] = latitude
            session['longitude'] = longitude
        else:
            status = 'nok'
            message = "Something went wrong. Couldn't find location."

        return json.dumps({'status': status, 'message': message})