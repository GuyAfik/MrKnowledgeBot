from abc import ABC
from mr_knowledge_bot.bot.clients.base_client import parse_http_response
from mr_knowledge_bot.bot.clients.the_movie_db.movie_db_base_client import TheMovieDBBaseClient


class TheMovieDBTVShowsClient(TheMovieDBBaseClient, ABC):

    def search(self, **kwargs):
        pass

    def discover(self, **kwargs):
        pass

    def get_genres(self):
        pass
