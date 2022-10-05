
from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity
from mr_knowledge_bot.bot.entites.the_movie_db.genre_entity import GenreEntity
from mr_knowledge_bot.bot.entites.the_movie_db.tv_show_season_entity import TVShowSeasonEntity
from mr_knowledge_bot.utils import is_english_letters_movie

class TheMovieDBTVShowEntity(TheMovieDBBaseEntity):

    def __init__(
        self, _id, name, release_date, genres, overview, popularity, rating, status, seasons, number_of_episodes, homepage
    ):
        super().__init__(_id, name)
        self.release_date = release_date
        try:
            self.genres = [GenreEntity.from_response(genre) for genre in genres]
        except (TypeError, AttributeError):
            self.genres = genres
        self.overview = overview
        self.popularity = popularity
        self.rating = rating
        self.status = status
        self.seasons = [
            TVShowSeasonEntity.from_response(response) for response in seasons if response.get('season_number')
        ] if seasons else None
        self.number_of_episodes = number_of_episodes
        self.homepage = homepage

    @classmethod
    def from_response(cls, response: dict):
        if 'results' not in response:
            return cls(
                _id=response.get('id'),
                name=response.get('name'),
                release_date=response.get('first_air_date'),
                genres=response.get('genre_ids') or response.get('genres'),
                overview=response.get('overview'),
                popularity=response.get('popularity'),
                rating=response.get('vote_average'),
                status=response.get('status'),
                seasons=response.get('seasons'),
                number_of_episodes=response.get('number_of_episodes'),
                homepage=response.get('homepage')
            )

        results = response.get('results') or []

        return [
            cls(
                _id=result.get('id'),
                name=result.get('name'),
                release_date=result.get('first_air_date'),
                genres=result.get('genre_ids') or result.get('genres'),
                overview=result.get('overview'),
                popularity=result.get('popularity'),
                rating=result.get('vote_average'),
                status=result.get('status'),
                seasons=result.get('seasons'),
                number_of_episodes=result.get('number_of_episodes'),
                homepage=result.get('homepage')
            ) for result in results if is_english_letters_movie(result.get('name'))
        ]
