import dateparser
from datetime import datetime

from telegram.ext import CallbackContext

from mr_knowledge_bot.bot.clients import TVShowsClient
from abc import ABC
from mr_knowledge_bot.bot.services.the_movie_db.base_movie_db_service import TheMovieDBBaseService


class TheMovieDBTVShowService(TheMovieDBBaseService, ABC):

    def __init__(self, tv_shows=None):
        super().__init__(client=TVShowsClient())
        self.tv_shows = tv_shows

    @classmethod
    def from_context(cls, context: CallbackContext):
        return cls(tv_shows=context.user_data.get('tv_shows'))

    def find_by_name(self, tv_show_name, limit, sort_by):
        """
        Find TV shows by name.
        """
        tv_shows = super().find_by_name(tv_show_name=tv_show_name, limit=limit, sort_by=sort_by)

        if len(tv_shows) > limit:
            if sort_by == 'popularity':
                tv_shows = sorted(
                    tv_shows, key=lambda tv_show: (tv_show.release_date, tv_show.release_date is not None)
                )
            elif sort_by == 'release_date':
                tv_shows = sorted(
                    tv_shows, key=lambda tv_show: (tv_show.release_date, tv_show.release_date is not None)
                )
            elif sort_by == 'tv_shows':
                tv_shows = sorted(tv_shows, key=lambda tv_show: (tv_show.rating, tv_show.rating is not None))

            tv_shows = tv_shows[:limit]

        return tv_shows

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
        def _set_up_body_request():
            _filters = {'page': page}
            if sort_by:
                if sort_by == 'popularity':
                    sort_by_value = 'popularity.desc'
                elif sort_by == 'first_air_date':
                    sort_by_value = 'first_air_date.desc'
                else:  # sort_by == 'rating'
                    sort_by_value = 'vote_average.desc'
                _filters['sort_by'] = sort_by_value

            if before_date:
                if parsed_before_data := dateparser.parse(before_date):
                    # log out what the date is before and after parsing
                    _filters['first_air_date.lte'] = parsed_before_data.strftime('%Y-%m-%d')

            if after_date:
                if parsed_after_date := dateparser.parse(after_date):
                    # log out what the date is before and after parsing
                    _filters['first_air_date.gte'] = parsed_after_date.strftime('%Y-%m-%d')

            if with_genres and (genre_ids := self.genre_names_to_ids(with_genres)):
                _filters['with_genres'] = genre_ids

            if without_genres and (genre_ids := self.genre_names_to_ids(without_genres)):
                _filters['without_genres'] = genre_ids

            if before_runtime:
                _filters['with_runtime.lte'] = before_runtime

            if after_runtime:
                _filters['with_runtime.gte'] = after_runtime

            return _filters

        tv_shows = super().discover(**_set_up_body_request())

        if not not_released:  # remove tv-shows which were not released yet or don't have any release-date.
            tv_shows = [
                tv_show for tv_show in tv_shows if tv_show.release_date and
                dateparser.parse(tv_show.release_date).strftime('%Y-%m-%d') < datetime.now().strftime('%Y-%m-%d')
            ]

        if sort_by == 'popularity':
            tv_shows = sorted(tv_shows, key=lambda tv_show: (tv_show.release_date, tv_show.release_date is not None))
        elif sort_by == 'first_air_date':
            tv_shows = sorted(tv_shows, key=lambda tv_show: (tv_show.release_date, tv_show.release_date is not None))
        elif sort_by == 'rating':
            tv_shows = sorted(tv_shows, key=lambda tv_show: (tv_show.rating, tv_show.rating is not None))

        if len(tv_shows) > limit:
            tv_shows = tv_shows[:limit]

        return '\n'.join([tv_show.name for tv_show in tv_shows])

    def get_details(self, chosen_tv_show):
        for tv_show in self.tv_shows:
            if chosen_tv_show == tv_show.name:
                return super().get_details(_id=tv_show.id)
        return None

    def get_tv_seasons(self, chosen_tv_show):
        tv_show = self.get_details(chosen_tv_show)
        return tv_show.seasons

    def get_tv_show_season(self, chosen_tv_show, chosen_tv_season):
        tv_show_seasons = self.get_tv_seasons(chosen_tv_show)
        for season in tv_show_seasons:
            if season.season_number == chosen_tv_season:
                return season
        return None

    def get_trailer(self, chosen_tv_show):
        """
        Returns a trailer of a movie.
        """
        for tv_show in self.tv_shows:
            if chosen_tv_show == tv_show.name:
                for video in self._client.get_videos(_id=tv_show.id):
                    if trailer_video := str(video):
                        return trailer_video
            return ''
        return None

