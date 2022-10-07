
from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity
from mr_knowledge_bot.bot.entites.the_movie_db.genre_entity import GenreEntity
import datetime
from mr_knowledge_bot.utils import is_english_letters_movie


class TheMovieDBMovieEntity(TheMovieDBBaseEntity):

    def __init__(self, _id, name, release_date, genres, overview, popularity, rating, homepage, status, runtime):
        super().__init__(_id, name)
        self.release_date = release_date
        try:
            self.genres = [GenreEntity.from_response(genre) for genre in genres]
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
        if 'results' not in response:
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

        results = response.get('results') or []

        return [
            cls(
                _id=result.get('id'),
                name=result.get('title'),
                release_date=result.get('release_date'),
                genres=result.get('genre_ids') or result.get('genres'),
                overview=result.get('overview'),
                popularity=result.get('popularity'),
                rating=result.get('vote_average'),
                homepage=result.get('homepage'),
                status=result.get('status'),
                runtime=result.get('runtime')
            ) for result in results if is_english_letters_movie(result.get('title'))
        ]
