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

    def __str__(self):
        return ", ".join([f'{attr_name}={attr_value}' for attr_name, attr_value in self.to_dict().items()])

