from abc import ABC, abstractmethod


class BaseLogic(ABC):

    @abstractmethod
    def find_by_name(self, **kwargs):
        pass
