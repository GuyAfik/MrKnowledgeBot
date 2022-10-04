
from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity


class TheMovieDBTVShowEntity(TheMovieDBBaseEntity):

    def __init__(self, _id, name, release_date, genre_ids, overview, popularity, rating):
        super().__init__(_id, name)
        self.release_date = release_date
        self.genre_ids = genre_ids
        self.overview = overview
        self.popularity = popularity
        self.rating = rating

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
