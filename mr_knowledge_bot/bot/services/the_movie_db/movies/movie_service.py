import dateparser
from datetime import datetime
from mr_knowledge_bot.bot.clients import MovieClient
from mr_knowledge_bot.bot.services.the_movie_db.base_movie_db_service import TheMovieDBBaseService
from abc import ABC
from telegram.ext import CallbackContext


class TheMovieDBMovieService(TheMovieDBBaseService, ABC):

    def __init__(self, movies=None):
        super().__init__(client=MovieClient())
        self.movies = movies

    @classmethod
    def from_context(cls, context: CallbackContext):
        return cls(movies=context.user_data.get('movies'))

    def find_by_name(self, movie_name, limit, sort_by):
        """
        Find movies by name.
        """
        if sort_by == 'rating':
            sort_by = 'vote_average'

        movies = super().find_by_name(movie_name=movie_name, limit=limit, sort_by=sort_by)
        if len(movies) > limit:
            if sort_by == 'popularity':
                movies = sorted(movies, key=lambda movie: (movie.release_date, movie.release_date is not None))
            elif sort_by == 'release_date':
                movies = sorted(movies, key=lambda movie: (movie.release_date, movie.release_date is not None))
            elif sort_by == 'rating':
                movies = sorted(movies, key=lambda movie: (movie.rating, movie.rating is not None))

            movies = movies[:limit]

        return movies

    def discover(
        self,
        limit=20,
        page=1,
        sort_by=None,
        before_date=None,
        after_date=None,
        with_genres=None,
        without_genres=None,
        before_runtime=None,
        after_runtime=None,
        not_released=None
    ):
        """
        Find movies by filter parameters.
        """
        def _set_up_body_reqeust():
            _filters = {'page': page}
            if sort_by:
                if sort_by == 'popularity':
                    sort_by_value = 'popularity.desc'
                elif sort_by == 'release_date':
                    sort_by_value = 'release_date.desc'
                else:  # sort_by == 'rating'
                    sort_by_value = 'vote_average.desc'
                _filters['sort_by'] = sort_by_value

            if before_date:
                if parsed_before_data := dateparser.parse(before_date):
                    # log out what the date is before and after parsing
                    _filters['primary_release_date.lte'] = parsed_before_data.strftime('%Y-%m-%d')

            if after_date:
                if parsed_after_date := dateparser.parse(after_date):
                    # log out what the date is before and after parsing
                    _filters['primary_release_date.gte'] = parsed_after_date.strftime('%Y-%m-%d')

            if with_genres and (genre_ids := self.genre_names_to_ids(with_genres)):
                _filters['with_genres'] = genre_ids

            if without_genres and (genre_ids := self.genre_names_to_ids(without_genres)):
                _filters['without_genres'] = genre_ids

            if before_runtime:
                _filters['with_runtime.lte'] = before_runtime

            if after_runtime:
                _filters['with_runtime.gte'] = after_runtime

            return _filters

        movies = super().discover(**_set_up_body_reqeust())
        if not not_released:  # remove movies which were not released yet or don't have any release-date
            movies = [
                movie for movie in movies if movie.release_date and
                dateparser.parse(movie.release_date).strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d')
            ]

        if sort_by == 'popularity':
            movies = sorted(movies, key=lambda movie: (movie.release_date, movie.release_date is not None))
        elif sort_by == 'release_date':
            movies = sorted(movies, key=lambda movie: (movie.release_date, movie.release_date is not None))
        elif sort_by == 'rating':
            movies = sorted(movies, key=lambda movie: (movie.rating, movie.rating is not None))

        if len(movies) > limit:
            movies = movies[:limit]

        return movies

    def get_trailer(self, chosen_movie):
        """
        Returns a trailer of a movie.
        """
        for movie in self.movies:
            if chosen_movie == movie.name:
                for video in self._client.get_videos(_id=movie.id):
                    if trailer_video := str(video):
                        return trailer_video
                return ''
        return None

    def get_details(self, chosen_movie):
        for movie in self.movies:
            if chosen_movie == movie.name:
                return super().get_details(_id=movie.id)
        return None
