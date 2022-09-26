from mr_knowledge_bot.bot.clients import MovieClient
from mr_knowledge_bot.bot.logic.the_movie_db.base_movie_db_logic import TheMovieDBBaseLogic
from abc import ABC


class TheMovieDBMovieLogic(TheMovieDBBaseLogic, ABC):

    def __init__(self):
        super().__init__(client=MovieClient())

    def find_by_name(self, movie_name, limit, sort_by):
        """
        Find movies by name.
        """
        movies = super().find_by_name(movie_name=movie_name, limit=limit, sort_by=sort_by)

        if sort_by == 'rating':
            sort_by = 'vote_average'

        if len(movies) > limit:
            movies = sorted(movies, key=lambda d: d.get(sort_by), reverse=True)[:limit]

        return '\n'.join([movie.get('title') for movie in movies])
