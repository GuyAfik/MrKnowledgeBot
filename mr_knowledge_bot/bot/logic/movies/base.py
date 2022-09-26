from abc import ABC, abstractmethod


class BaseMoviesTVShowsLogic(ABC):

    @abstractmethod
    def find_by_name(self, **kwargs):
        pass

    @abstractmethod
    def discover(self, **kwargs):
        pass
