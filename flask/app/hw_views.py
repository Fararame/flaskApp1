# Maythanan Ladee (Frame)
# 670510722
# sec001
import datetime
import json
from urllib.request import urlopen
from urllib.parse import quote
from flask import (jsonify, render_template, request)
from app import app, db
from app.models.anime import Anime
from app import csrf
from flask_wtf.csrf import CSRFProtect
import os

DEBUG = False

@app.route('/anivault')
def anivault_mylist():
    return render_template('anivault/index.html', active_tab='search')


@app.route('/anivault/fetch')
def anivault_fetch():
    return render_template('anivault/fetch.html', active_tab='fetch')


@app.route('/anivault/api/list')
def anivault_api_list():
    """Returns all anime entries as JSON for the Grid.js table."""
    raw_json = read_file(os.path.join(app.root_path, 'data', 'anime_list.json'))
    anime_list = json.loads(raw_json)
    # Filter out soft-deleted entries
    anime_list = [a for a in anime_list if a.get('deleted_at') is None]
    # Sort by title, then by year (None years sort to end)
    anime_list = sorted(anime_list, key=lambda x: (x.get('title', '') or x.get('title_english', ''), x.get('year') or float('inf')))
    return jsonify(anime_list)


@app.route('/anivault/api/jikan')
def anivault_api_jikan():
    """Searches the Jikan API (MyAnimeList) and returns mapped results."""
    
    # Get search parameters from query string
    name = request.args.get('name', '')
    year = request.args.get('year', '')

    if not name or not year:
        return jsonify([])

    # Build the Jikan API URL
    start_date = f"{year}-01-01"
    quoted_name = quote(name)  # URL-encode the search term
    url = f"https://api.jikan.moe/v4/anime?q={quoted_name}&start_date={start_date}"

    # Fetch and process API response
    try:
        with urlopen(url) as response:
            res_data = json.loads(response.read().decode())

            # Map Jikan response to our simplified format
            jikan_data = res_data.get('data', [])
            mapped_data = []
            for item in jikan_data:
                mapped_item = {
                    "mal_id": item['mal_id'],
                    "title_english": item['title_english'],
                    "image_url": item['images']['jpg']['image_url'],
                    "year": item.get('year') or item.get('aired', {}).get('prop', {}).get('from', {}).get('year'),
                    "episodes": item['episodes'],
                    "synopsis": item['synopsis'],
                    "score": item['score'],
                    "genres": [g['name'] for g in item['genres']]
                }
                mapped_data.append(mapped_item)

            return jsonify(mapped_data)
    except Exception as e:
        app.logger.error(f"Jikan API Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/anivault/api/add', methods=['POST'])
def anivault_api_add():
    """Adds a new anime to the collection from form data."""
    
    # Receive form data
    new_anivault = request.form.to_dict()
    if not new_anivault:
        return jsonify({'success': False, 'message': 'No data received'}), 400

    # Convert string values to appropriate types
    for key in new_anivault:
        try:
            if key in ["mal_id", "year", "episodes"]:
                new_anivault[key] = int(new_anivault[key])
            elif key == "score":
                new_anivault[key] = float(new_anivault[key])
            elif key == "genres":
                new_anivault[key] = new_anivault[key].split(',') if new_anivault[key] else []
        except ValueError:
            new_anivault[key] = 'N/A'

    # Load existing anime list
    path = os.path.join(app.root_path, 'data', 'anime_list.json')
    try:
        raw_json = read_file(path)
        anime_list = json.loads(raw_json)
    except Exception:
        anime_list = []

    # Check for duplicates and find insertion position
    new_id = new_anivault.get('mal_id')
    insert_index = len(anime_list)
    existing_anime = None
    existing_index = None

    if new_id and new_id != 'N/A':
        for i, anime in enumerate(anime_list):
            curr_id = anime.get('mal_id')

            # Check if entry already exists
            if curr_id == new_id:
                existing_anime = anime
                existing_index = i
                break

            # Find insertion point to maintain sorted order by mal_id
            try:
                curr_id_val = int(curr_id) if curr_id is not None else 0
                if curr_id_val > new_id:
                    insert_index = i
                    break
            except (ValueError, TypeError):
                continue

    # Handle existing entries (restore if soft-deleted, reject if active)
    if existing_anime:
        if existing_anime.get('deleted_at') is not None:
            anime_list[existing_index]['deleted_at'] = None
            write_file(path, json.dumps(anime_list, indent=4))
            return jsonify({'success': True, 'message': 'Anime restored to your vault!'})
        else:
            return jsonify({'success': False, 'message': 'This anime is already in your vault!'}), 400

    # Add required fields and insert new entry
    new_anivault['my_rating'] = 0
    new_anivault['deleted_at'] = None
    anime_list.insert(insert_index, new_anivault)

    # Save and return success
    write_file(path, json.dumps(anime_list, indent=4))
    return jsonify({'success': True, 'message': 'Successfully added to vault!'})


def read_file(filename, mode="rt"):
    with open(filename, mode, encoding='utf-8') as fin:
        return fin.read()


def write_file(filename, contents, mode="wt"):
    with open(filename, mode, encoding="utf-8") as fout:
        fout.write(contents)
@app.route('/anivault/api/rate', methods=['POST'])
# @csrf.exempt
def anivault_api_rate():
   """
   Updates the user rating for an anime.
   """
   # 1. Extract data
   data = request.get_json()
   # 2. Validate fields: Check [mal_id] and [rating] exist
   for ani in data:
       mal_id = data["mal_id"]
       rating = data["my_rating"]

       if mal_id is None or rating is None:
        return jsonify({'success': False,
                        'message': 'Missing mal_id or rating'}), 400
        # 3. Find anime
        anime = Anime.query.filter_by(mal_id=mal_id).first()

        if not anime:
            return jsonify({'success': False,
                            'message': 'Anime not found'}), 404
            
        if anime is not None:
            anime.my_rating = rating
            db.session.commit()
            return jsonify({'success': True, 'message': 'Rating updated!'}), 200
        
def anivault_api_delete():
    data = request.get_json()
    mal_id = data["mal_id"]
       
    if mal_id is None:
         return jsonify({'success': False, 'message': 'Missing mal_id'}), 400
       
    if (anime := Anime.query.filter_by(mal_id=mal_id).first()) is None:
        return jsonify({'success': False, 'message': 'Anime not found'}), 404
       
    if anime is not None:
        anime.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Anime removed from collection'}), 200