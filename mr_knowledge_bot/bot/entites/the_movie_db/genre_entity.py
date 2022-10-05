from mr_knowledge_bot.bot.entites.the_movie_db.base import TheMovieDBBaseEntity


class GenreEntity(TheMovieDBBaseEntity):

    @classmethod
    def from_response(cls, response: dict):
        return super().from_response(response.get('genres') or [])
