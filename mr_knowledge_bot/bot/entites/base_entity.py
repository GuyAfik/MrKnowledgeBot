from abc import abstractmethod


class BaseEntity:

    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_response(cls, response: dict):
        pass
