from abc import ABC, abstractmethod
import logging
from json.decoder import JSONDecodeError
from types import SimpleNamespace
from mr_knowledge_bot.bot.entites.the_movie_db.tv_show_entity import TheMovieDBTVShowEntity
from mr_knowledge_bot.bot.entites.the_movie_db.movie_entity import TheMovieDBMovieEntity
from mr_knowledge_bot.bot.entites.the_movie_db.genre_entity import GenreEntity
from mr_knowledge_bot.bot.entites.the_movie_db.video_entity import VideoEntity
from mr_knowledge_bot.bot.entites.base_entity import BaseEntity
from typing import Type, Optional, Any

logger = logging.getLogger('knowledge-bot')


class ApiError(Exception):
    pass


class ApiResponse(SimpleNamespace):
    pass


def is_english_letters_movie(name: str):
    try:
        name.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def response_to_tv_show_entities(response: dict):
    if 'results' not in response:
        return TheMovieDBTVShowEntity.from_response(response)
    results = response.get('results') or []
    return [
        TheMovieDBTVShowEntity.from_response(result)
        for result in results if is_english_letters_movie(result.get('name'))
    ]


def response_to_movie_entities(response: dict):
    if 'results' not in response:
        return TheMovieDBMovieEntity.from_response(response)
    results = response.get('results') or []
    return [TheMovieDBMovieEntity.from_response(result) for result in results]


def response_to_video_entities(response: dict):
    results = response.get('results')
    return [VideoEntity.from_response(result) for result in results]


def response_to_genre_entity(response: dict):
    genres = response.get('genres')
    return [GenreEntity.from_response(genre) for genre in genres]


def dict_get_nested_fields(dictionary: dict, keys: Optional[list], default: Any = None):
    if not keys:
        return dictionary

    result = dictionary

    for key in keys:
        try:
            result = result[key]
        except (KeyError, TypeError, IndexError, AttributeError):
            result = default

    return result


def parse_http_response(
    _class_type: Optional[Type[BaseEntity]] = None,
    expected_valid_code: int = 200,
    response_type: str = 'class',
    keys: Optional[list] = None
):
    """
    Parses the http response.

    Args:
        _class_type (BaseEntity): an entity class to parse the response. (any class inherits from BaseEntity)
        expected_valid_code (int): the expected http status code of success.
        response_type (str): what kind of response type to parse to, either json/response/class.
        keys (list): a list of keys to get the response from, each value is for the next nested key in a dict,
                if None will bring the entire response back.

    Raises:
        ValueError: in case the response type is not valid.
        ApiError: in case the request didn't succeed.
    """

    # class - return a class where the attributes are the json response (including nested fields).
    # response - return the complete response object.
    # json - return a dict/list containing the response.

    response_types = {'class', 'response', 'json'}
    if response_type not in response_types:
        raise ValueError(
            f'Invalid response type ({response_type}) - should be one of ({",".join(response_types)})'
        )

    if response_type == 'class' and not _class_type:
        raise ValueError('_class_type must be provided when "response_type" = class')

    _class_type_to_entity = {
        TheMovieDBTVShowEntity: response_to_tv_show_entities,
        TheMovieDBMovieEntity: response_to_movie_entities,
        GenreEntity: response_to_genre_entity,
        VideoEntity: response_to_video_entities
    }

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # response type will override the response of the class.
            logger.debug(f'Sending HTTP request using function {func.__name__} with {args=}, {kwargs=}')
            http_response = func(self, *args, **kwargs)

            if http_response.status_code != expected_valid_code:
                try:
                    response_as_json = http_response.json()
                except JSONDecodeError:
                    raise ApiError(f'Error: ({http_response.text})')
                raise ApiError(f'Error: ({response_as_json})')
            if response_type == 'class':
                return _class_type_to_entity[_class_type](http_response.json())
            elif response_type == 'json':
                print(http_response.json())
                return dict_get_nested_fields(dictionary=http_response.json(), keys=keys)
            else:  # in case the entire response object is needed
                return http_response
        return wrapper
    return decorator


class BaseClient(ABC):

    def __init__(self, token=None, base_url=None, verify=True):
        self.token = token
        self.base_url = base_url
        self.verify = verify

    @abstractmethod
    def get(self, url, params=None):
        pass
