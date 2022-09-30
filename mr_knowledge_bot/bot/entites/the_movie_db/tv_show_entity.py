
from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity


class TheMovieDBTVShowEntity(TheMovieDBBaseEntity):

    @classmethod
    def from_response(cls, response: dict):
        return cls(
            _id=response.get('id'),
            name=response.get('name'),
            release_date=response.get('first_air_date'),
            genre_ids=response.get('genre_ids'),
            overview=response.get('overview'),
            popularity=response.get('popularity'),
            rating=response.get('vote_average')
        )
