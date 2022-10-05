from abc import ABC
from typing import Union
from mr_knowledge_bot.bot.entites.base_entity import BaseEntity


class TheMovieDBBaseEntity(BaseEntity, ABC):

    def __init__(self, _id, name):
        self.id = _id
        self.name = name

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_response(cls, response: Union[dict, list]):
        if isinstance(response, dict):
            return cls(_id=response.get('id'), name=response.get('name'))
        return [
            cls(_id=result.get('id'), name=result.get('name')) for result in response
        ]

    def __str__(self):
        return ", ".join([f'{attr_name}={attr_value}' for attr_name, attr_value in self.to_dict().items()])

