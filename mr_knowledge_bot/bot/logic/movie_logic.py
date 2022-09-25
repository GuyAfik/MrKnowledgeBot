from mr_knowledge_bot.bot.clients import MovieClient
from abc import ABC, abstractmethod


class MovieCommandsBaseLogic(ABC):
    """
    Base class for the movies based commands.
    """
    def __init__(self):
        self._movie_client = MovieClient()

    @abstractmethod
    def get_movies_by_name(self, movie_name, limit, sort_by):
        pass


class TheMovieDBLogic(MovieCommandsBaseLogic, ABC):

    def get_movies_by_name(self, movie_name, limit, sort_by):
        if sort_by == 'rating':
            sort_by = 'vote_average'

        movies = self._movie_client.search(movie_name=movie_name)
        if len(movies) > limit:
            movies = sorted(movies, key=lambda d: d.get(sort_by), reverse=True)[:limit]

        return '\n'.join([movie.get('title') for movie in movies])
