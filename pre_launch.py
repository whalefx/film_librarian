from film_data_defaults import data_defaults as default
from film_finder import read_data, log_film
from pprint import pprint
from themoviedb import aioTMDb
from api_key import KEY
import asyncio


def init_missing_data():
    data = read_data()
    for k, v in data.items():
        film_data = v
        need_fix = default.keys() != film_data.keys()
        if need_fix:
            # add missing data from defaults
            for k2, v2 in default.items():
                if k2 in v.keys():
                    continue
                film_data[k2] = v2
            film_data = {k: film_data}
            log_film(film_data)


def update_missing_values(ignore=('keywords')):
    data = read_data()
    for k, v in data.items():
        film_data = v
        for k2, v2 in film_data.items():
            if k2 in ignore:
                continue
            if v2 is not None:
                # TODO: get missing data
                # will need to find a way to get film by film id and fill in missing data here
                pass


async def foo():
    _tmdb = aioTMDb()
    _tmdb.key = KEY
    film = await _tmdb.movie(241848).credits()
    print(film)


def pre_launch():
    init_missing_data()


# asyncio.run(foo())
