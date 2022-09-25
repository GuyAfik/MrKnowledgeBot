import os
import requests

from mr_knowledge_bot.bot.clients.base_client import BaseClient
from abc import ABC, abstractmethod


def poll_movies_by_page(func):
    def wrapper(self, *args, **kwargs):
        page = 1
        all_movies = []
        kwargs['page'] = page
        current_movies_by_page = func(self, *args, **kwargs).get('results') or []
        while current_movies_by_page:
            page += 1
            kwargs['page'] = page
            all_movies.extend(current_movies_by_page)
            current_movies_by_page = func(self, *args, **kwargs).get('results') or []
        return all_movies

    return wrapper


class TheMovieDBBaseClient(BaseClient, ABC):
    BASE_URL = os.getenv('MOVIE_BASE_URL')

    def __init__(self, token=None, base_url=None, verify=True):
        super().__init__(
            token=token or os.getenv('API_MOVIE_TOKEN'), base_url=base_url or self.BASE_URL, verify=verify
        )

    def get(self, url, params=None):
        if not params:
            params = {}
        params.update({'api_key': self.token})
        return requests.request('GET', f'{self.base_url}{url}', params=params, verify=self.verify)

    @abstractmethod
    def search(self, **kwargs):
        pass

    @abstractmethod
    def get_genres(self):
        pass

    @abstractmethod
    def discover(self, **kwargs):
        pass
