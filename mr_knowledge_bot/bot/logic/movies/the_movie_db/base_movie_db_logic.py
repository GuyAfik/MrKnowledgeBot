from abc import ABC
from mr_knowledge_bot.bot.logic.movies.base import BaseMoviesTVShowsLogic


class TheMovieDBBaseLogic(BaseMoviesTVShowsLogic, ABC):

    def __init__(self, client=None):
        self._client = client
        # self._genres = {genre.get('name'): genre.get('id') for genre in self._client.get_genres().get('genres') or []}
        self.genres = self._client.get_genres().get('genres') or []

    def find_by_name(self, **kwargs):
        return self._client.search(**kwargs)

    def discover(self, **kwargs):
        return self._client.discover(**kwargs)
