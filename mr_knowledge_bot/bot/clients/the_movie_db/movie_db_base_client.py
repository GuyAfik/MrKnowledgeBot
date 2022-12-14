import os
import requests
from abc import ABC, abstractmethod

from mr_knowledge_bot.bot.clients.base_client import BaseClient
from mr_knowledge_bot.bot.entites.the_movie_db.genre_entity import GenreEntity
from mr_knowledge_bot.bot.entites.the_movie_db.video_entity import VideoEntity
from mr_knowledge_bot.bot.clients.base_client import parse_http_response


def poll_by_page_and_limit(limit=500):
    """
    Args:
        limit (int): the maximum number of records to query from the api.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            objects, page = [], 1
            kwargs['page'] = page

            while current_objects_by_page := func(self, *args, **kwargs):
                objects.extend(current_objects_by_page)
                if len(objects) > limit:
                    break
                page += 1
                kwargs['page'] = page
            return objects[:limit]

        return wrapper
    return decorator


class TheMovieDBBaseClient(BaseClient, ABC):
    BASE_URL = os.getenv('THE_MOVIE_DB_BASE_URL')
    genre_entity = GenreEntity
    video_entity = VideoEntity

    def __init__(self, token=None, base_url=None, verify=True):
        super().__init__(
            token=token or os.getenv('THE_MOVIE_DB_API_TOKEN'), base_url=base_url or self.BASE_URL, verify=verify
        )

    def get(self, url, params=None):
        if not params:
            params = {}
        params.update({'api_key': self.token})
        return requests.request('GET', f'{self.base_url}{url}', params=params, verify=self.verify)

    @parse_http_response(_class_type=video_entity)
    def get_videos(self, _id, _type):
        if _type not in ('movie', 'tv'):
            raise ValueError(f'{_type} can be only "movie" or "tv"')
        return self.get(url=f'/{_type}/{_id}/videos')

    def get_details(self, _id, _type):
        if _type not in ('movie', 'tv'):
            raise ValueError(f'{_type} can be only "movie" or "tv"')
        return self.get(url=f'/{_type}/{_id}')

    @abstractmethod
    def search(self, **kwargs):
        pass

    @abstractmethod
    def get_genres(self):
        pass

    @abstractmethod
    def discover(self, **kwargs):
        pass

