from film_data_defaults import data_defaults as default
from film_data_defaults import get_film_details
from film_finder import read_data, log_film
from pprint import pprint
from themoviedb import aioTMDb
from api_key import KEY
import asyncio


def init_missing_data():
    data = read_data()
    for film_id, v in data.items():
        film_data = v
        need_fix = default.keys() != film_data.keys()
        if need_fix:
            # add missing data from defaults
            for k2, v2 in default.items():
                if k2 in v.keys():
                    continue
                film_data[k2] = v2
            film_data = {film_id: film_data}
            log_film(film_data)


async def update_missing_values(ignore=()):
    tmdb = aioTMDb()
    tmdb.key = KEY
    data = read_data()
    for film_id, v in data.items():
        film_data = v
        for k2, v2 in film_data.items():
            if k2 in ignore:
                continue
            if v2 is None:
                _img, missing_data = await get_film_details(tmdb, film_id[5:])
                film_data = {film_id: film_data}
                film_data[film_id][k2] = missing_data[film_id][k2]
                log_film(film_data)


def pre_launch():
    init_missing_data()
    asyncio.run(update_missing_values())


