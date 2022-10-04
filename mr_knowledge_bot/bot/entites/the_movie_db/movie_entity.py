
import datetime

from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity
from mr_knowledge_bot.bot.entites.the_movie_db.genre_entity import GenreEntity


class TheMovieDBMovieEntity(TheMovieDBBaseEntity):

    def __init__(self, _id, name, release_date, genres, overview, popularity, rating, homepage, status, runtime):
        super().__init__(_id, name)
        self.release_date = release_date
        try:
            self.genres = [GenreEntity.from_response(
                genre) for genre in genres]
        except (TypeError, AttributeError):
            self.genres = genres
        self.overview = overview
        self.popularity = popularity
        self.rating = rating
        self.homepage = homepage
        self.status = status
        if runtime:
            self.runtime = str(datetime.timedelta(minutes=runtime))
        else:
            self.runtime = None

    @classmethod
    def from_response(cls, response: dict):
        return cls(
            _id=response.get('id'),
            name=response.get('title'),
            release_date=response.get('release_date'),
            genres=response.get('genre_ids') or response.get('genres'),
            overview=response.get('overview'),
            popularity=response.get('popularity'),
            rating=response.get('vote_average'),
            homepage=response.get('homepage'),
            status=response.get('status'),
            runtime=response.get('runtime')
        )
