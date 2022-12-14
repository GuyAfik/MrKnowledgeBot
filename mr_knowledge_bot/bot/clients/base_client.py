from abc import ABC, abstractmethod
import logging
from json.decoder import JSONDecodeError
from mr_knowledge_bot.bot.entites.base_entity import BaseEntity
from typing import Type, Optional
from mr_knowledge_bot.utils import dict_get_nested_fields


logger = logging.getLogger(__name__)


class ApiError(Exception):
    pass


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
                return _class_type.from_response(http_response.json())
            elif response_type == 'json':
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
