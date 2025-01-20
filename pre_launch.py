from film_data_defaults import data_defaults as default
from film_data_defaults import get_film_details
from film_finder import read_data, log_film
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


def get_all_keywords():
    data = read_data()
    all_keywords = dict()
    for film_id, v in data.items():
        film_data = v
        for keyword in film_data['keywords']:
            if keyword not in all_keywords.keys():
                all_keywords[keyword] = 1
            else:
                count = all_keywords[keyword]
                all_keywords[keyword] = count+1
    all_keywords = dict(sorted(all_keywords.items(), key=lambda item: (-item[-1], item)))
    return all_keywords


def pre_launch_main():
    init_missing_data()
    asyncio.run(update_missing_values())


def pre_launch_viewer():
    keywords = get_all_keywords()
    return keywords


