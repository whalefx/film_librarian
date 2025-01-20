data_defaults = {
    'year': None,
    'genres': [None],
    'language': None,
    'country': [None],
    'actors': {None: None},
    'writers': [None],
    'directors': [None],
    'runtime': None,
    'tagline': None,
    'poster': None,
    'id': None,
    'title': None,
    'keywords': None,
    'format': 'dvd',
    'region': 2,
    'width': 14,
    'boxset': False
    }

from dataclasses import fields


async def get_film_details(tmdb, film_id):
    found_film = await tmdb.movie(film_id).details(append_to_response="credits,external_ids,images,keywords")
    img = found_film.poster_url()

    title = f'film_{film_id}'
    film_data = {title: {
        'year': found_film.year,
        'genres': [x.name for x in found_film.genres],
        'language': found_film.original_language,
        'country': [x.name for x in found_film.production_countries],
        'actors': {},
        'writers': [x.name for x in found_film.credits.crew if x.department == 'Writing'],
        'directors': [x.name for x in found_film.credits.crew if x.job == 'Director'],
        'runtime': found_film.runtime,
        'tagline': found_film.tagline,
        'poster': found_film.poster_url(),
        'id': film_id,
        'title': found_film.title,
        'keywords': []
        }
    }

    # assemble sub lists/dicts
    actors = {}

    for a in found_film.credits.cast:
        _actors = {a.name: a.character}
        actors.update(_actors)

    film_data[title]['actors'].update(actors)

    # assemble keywords list
    keywords = []

    for key in found_film.keywords.keywords:
        [keywords.append(getattr(key, x.name)) for x in fields(key) if x.name == 'name']

    film_data[title]['keywords'] = keywords

    return img, film_data
