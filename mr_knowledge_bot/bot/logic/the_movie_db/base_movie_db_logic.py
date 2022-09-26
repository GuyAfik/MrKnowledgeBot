from mr_knowledge_bot.bot.clients import MovieClient
from abc import ABC, abstractmethod
from mr_knowledge_bot.bot.logic.base_logic import BaseLogic


class TheMovieDBBaseLogic(BaseLogic, ABC):

    def __init__(self, client=None):
        self._client = client

    def find_by_name(self, **kwargs):
        return self._client.search(**kwargs)
