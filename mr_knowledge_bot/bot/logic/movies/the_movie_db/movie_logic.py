import dateparser
from mr_knowledge_bot.bot.clients import MovieClient
from mr_knowledge_bot.bot.logic.movies.the_movie_db.base_movie_db_logic import TheMovieDBBaseLogic
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

    def discover(
        self,
        limit=20,
        sort_by=None,
        before_date=None,
        after_date=None,
        with_genres=None,
        without_genres=None,
        before_runtime=None,
        after_runtime=None
    ):
        """
        Find movies by filter parameters.
        """
        def genre_names_to_ids(requested_genres):
            return [
                available_genre for requested_genre in requested_genres for available_genre in self.genres
                if requested_genre.lower() == available_genre.get('name', '').lower()
            ]

        filters = {}
        if sort_by:
            filters['sort_by'] = sort_by

        if before_date:
            if parsed_before_data := dateparser.parse(before_date):
                # log out what the date is before and after parsing
                filters['primary_release_date.lte'] = parsed_before_data.strftime('%Y-%m-%d')

        if after_date:
            if parsed_after_date := dateparser.parse(before_date):
                # log out what the date is before and after parsing
                filters['primary_release_date.gte'] = parsed_after_date.strftime('%Y-%m-%d')

        if with_genres and (genre_ids := genre_names_to_ids(with_genres)):
            filters['with_genres'] = genre_ids

        if without_genres and (genre_ids := genre_names_to_ids(without_genres)):
            filters['without_genres'] = genre_ids

        if before_runtime:
            filters['with_runtime.lte'] = before_runtime

        if after_runtime:
            filters['with_runtime.gte'] = after_runtime

        movies = super().discover(**filters)
        if len(movies) > limit:
            movies = movies[:limit]

        return '\n'.join([movie.get('title') for movie in movies])

