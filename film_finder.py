import os
import json
import asyncio
from themoviedb import aioTMDb
from api_key import KEY

# init variables for json path
# TODO: Have custom path option for the library file?
_dir = os.path.dirname(os.path.abspath(__file__))
_data_name = 'list_data.json'
json_path = os.path.join(_dir, _data_name)


def initialize_json():
    """
    Checks for the existence of the json file and (re)creates it as necessary

    :return:
        None
    """
    # check for json file
    format_file = True
    if os.path.isfile(json_path):
        # check if json is formatted correctly
        with open(json_path, 'r') as file:
            data = json.load(file)
            format_file = not isinstance(data, dict)

            if format_file:
                print('Library file not formatted correctly. Reinitializing file.')
            else:
                print('Library file found!')
    else:
        print('No library file found. Initializing file.')

    if format_file:
        # create json file as an empty dictionary
        with open(json_path, 'w') as data:
            init = dict()
            json.dump(init, data)
            print(f'File initialized at {json_path}.')


async def search_film(film, list_item=0):
    """
    Searches themoviedb.org for a film and returns its poster and film data

    :param film:
        The name of the film being searched for
    :param list_item:
        Which film in the list of results to return
    :return:
        img as a string linking to the image url
        film_data as a dictionary containing relevant film information
    """
    tmdb = aioTMDb()
    tmdb.key = KEY
    films = await tmdb.search().movies(film)

    # check if found film is correct
    try:
        film_id = films[list_item].id
    except IndexError:
        print(f'No other films names {film} found!')
        return None, None

    found_film = await tmdb.movie(film_id).details(append_to_response="credits,external_ids,images")

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
        'title': found_film.title
        }
    }

    # assemble sub lists/dicts
    actors = {}

    for a in found_film.credits.cast:
        _actors = {a.name: a.character}
        actors.update(_actors)

    film_data[title]['actors'].update(actors)

    return img, film_data


def search_film_async(film, list_item=0):
    """
    Dummy method to easily call the async search_film method inside Qt

    :param film:
        The name of the film being searched for
    :param list_item:
        Which film in the list of results to return
    :return:
        img as a string linking to the image url
        film_data as a dictionary containing relevant film information
    """
    img, film_data = asyncio.run(search_film(film, list_item))
    return img, film_data


def log_film(film_data):
    """
    Loads in the saved library data and writes the chosen film to its database

    :param film_data:
        A dictionary containing relevant film information
    :return:
        None
    """
    # write data to json
    with open(json_path, 'r+') as file:
        data = json.load(file)
        data.update(film_data)

    with open(json_path, 'w') as file:
        data = dict(sorted(data.items(), key=lambda item: (item[1]['title'], item[1]['year'])))
        json.dump(data, file, indent=6)
    print('film logged!')


def read_data():
    """
    Loads the json file into data.

    :return:
        data as the film library dictionary information.
    """
    with open(json_path, 'r+') as file:
        data = json.load(file)
        return data
