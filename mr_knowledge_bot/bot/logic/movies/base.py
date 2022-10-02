from abc import ABC, abstractmethod
from telegram.ext import CallbackContext


class BaseMoviesTVShowsCommand(ABC):

    @abstractmethod
    def find_by_name(self, **kwargs):
        pass

    @abstractmethod
    def discover(self, **kwargs):
        pass

    @abstractmethod
    def get_genres(self):
        pass

    @classmethod
    def from_context(cls, context: CallbackContext):
        pass
