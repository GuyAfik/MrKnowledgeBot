import os
from abc import ABC, abstractmethod


class BaseBot(ABC):
    def __init__(self, token):
        self.token = token or os.getenv('BOT_TOKEN')

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def help_command(self):
        pass

    @abstractmethod
    def find_movies_by_name_command(self, *args, **kwargs):
        pass

    @abstractmethod
    def discover_movies_command(self, *args, **kwargs):
        pass

    @abstractmethod
    def find_tv_shows_by_name_command(self, *args, **kwargs):
        pass

    @abstractmethod
    def discover_tv_shows_command(self, *args, **kwargs):
        pass
