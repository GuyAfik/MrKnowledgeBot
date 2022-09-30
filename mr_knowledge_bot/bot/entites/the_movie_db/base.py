from abc import ABC

from mr_knowledge_bot.bot.entites.base_entity import BaseEntity


class TheMovieDBBaseEntity(BaseEntity, ABC):

    def __init__(self, _id, name, release_date=None, genre_ids=None, overview=None, popularity=None, rating=None):
        self.id = _id
        self.name = name
        self.release_date = release_date
        self.genre_ids = genre_ids
        self.overview = overview
        self.popularity = popularity
        self.rating = rating

    def to_dict(self):
        return self.__dict__

    def __lt__(self, other, sort_by):
        if sort_by == 'vote_average':
            return self.rating < other.rating
        elif sort_by == 'popularity':
            return self.popularity < other.popularity
        else:  # sort_by = release_date
            return self.release_date < other.release_date
