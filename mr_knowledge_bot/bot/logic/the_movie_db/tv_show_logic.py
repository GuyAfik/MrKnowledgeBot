from mr_knowledge_bot.bot.clients import TVShowsClient
from abc import ABC
from mr_knowledge_bot.bot.logic.the_movie_db.base_movie_db_logic import TheMovieDBBaseLogic


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
