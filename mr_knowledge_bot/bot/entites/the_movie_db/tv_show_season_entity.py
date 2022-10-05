

from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity


class TVShowSeasonEntity(TheMovieDBBaseEntity):

    def __init__(self, _id, name, overview, episode_count, release_date, season_number):
        super().__init__(_id, name)
        self.overview = overview
        self.episode_count = episode_count
        self.release_date = release_date
        self.season_number = season_number

    @classmethod
    def from_response(cls, response):
        return cls(
            name=response.get('name'),
            _id=response.get('id'),
            overview=response.get('overview'),
            episode_count=response.get('episode_count'),
            release_date=response.get('air_date'),
            season_number=response.get('season_number'),
        )
