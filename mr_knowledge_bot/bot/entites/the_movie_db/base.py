from abc import ABC

from mr_knowledge_bot.bot.entites.base_entity import BaseEntity


class TheMovieDBBaseEntity(BaseEntity, ABC):

    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_response(cls, response: dict):
        return cls(_id=response.get('id'), name=response.get('name'))

    def __str__(self):
        return ", ".join([f'{attr_name}={attr_value}' for attr_name, attr_value in self.to_dict().items()])

