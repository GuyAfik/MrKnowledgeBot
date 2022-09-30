import dateparser
from datetime import datetime
from mr_knowledge_bot.bot.clients import TVShowsClient
from abc import ABC
from mr_knowledge_bot.bot.logic.movies.the_movie_db.base_movie_db_logic import TheMovieDBBaseLogic


class TheMovieDBTVShowLogic(TheMovieDBBaseLogic, ABC):

    def __init__(self):
        super().__init__(client=TVShowsClient())

    def find_by_name(self, tv_show_name, limit, sort_by):
        """
        Find TV shows by name.
        """
        tv_shows = super().find_by_name(tv_show_name=tv_show_name, limit=limit, sort_by=sort_by)

        if sort_by == 'rating':
            sort_by = 'vote_average'
        elif sort_by == 'release_date':
            sort_by = 'first_air_date'

        if len(tv_shows) > limit:
            tv_shows = sorted(tv_shows, key=lambda d: d.get(sort_by), reverse=True)[:limit]

        return '\n'.join([tv_show.get('name') for tv_show in tv_shows])

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
        with_status=None,
        not_released=None
    ):

        filters = {"page": page}
        if sort_by:
            if sort_by == 'popularity':
                sort_by = 'popularity.desc'
            elif sort_by == 'first_air_date':
                sort_by = 'first_air_date.desc'
            elif sort_by == 'rating':
                sort_by = 'vote_average.desc'
            filters['sort_by'] = sort_by

        if before_date:
            if parsed_before_data := dateparser.parse(before_date):
                # log out what the date is before and after parsing
                filters['first_air_date.lte'] = parsed_before_data.strftime('%Y-%m-%d')

        if after_date:
            if parsed_after_date := dateparser.parse(after_date):
                # log out what the date is before and after parsing
                filters['first_air_date.gte'] = parsed_after_date.strftime('%Y-%m-%d')

        if with_genres and (genre_ids := self.genre_names_to_ids(with_genres)):
            filters['with_genres'] = genre_ids

        if without_genres and (genre_ids := self.genre_names_to_ids(without_genres)):
            filters['without_genres'] = genre_ids

        if before_runtime:
            filters['with_runtime.lte'] = before_runtime

        if after_runtime:
            filters['with_runtime.gte'] = after_runtime

        tv_shows = super().discover(**filters)
        if not not_released:  # remove movies which were not released yet.
            tv_shows = [
                tv_show for tv_show in tv_shows if tv_show.release_date and
                dateparser.parse(tv_show.release_date).strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d')
            ]
        if len(tv_shows) > limit:
            tv_shows = tv_shows[:limit]

        return '\n'.join([tv_show.name for tv_show in tv_shows])
