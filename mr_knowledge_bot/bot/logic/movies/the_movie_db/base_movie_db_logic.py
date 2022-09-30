from abc import ABC
from mr_knowledge_bot.bot.logic.movies.base import BaseMoviesTVShowsLogic


class TheMovieDBBaseLogic(BaseMoviesTVShowsLogic, ABC):

    def __init__(self, client=None):
        self._client = client
        self.genres = self._client.get_genres()

    def find_by_name(self, **kwargs):
        return self._client.search(**kwargs)

    def discover(self, **kwargs):
        return self._client.discover(**kwargs)

    def get_genres(self):
        return '\n'.join(genre.name for genre in self.genres)

    def genre_names_to_ids(self, requested_genres):
        names_to_ids = {genre.name: genre.id for genre in self.genres}
        return [names_to_ids.get(genre) for genre in requested_genres if names_to_ids.get(genre)]

