from abc import ABC, abstractmethod
import logging
from json.decoder import JSONDecodeError
from types import SimpleNamespace


logger = logging.getLogger('knowledge-bot')


class ApiError(Exception):
    pass


class ApiResponse(SimpleNamespace):
    pass


def parse_http_response(expected_valid_code: int = 200, response_type: str = 'json'):
    """
    Parses the http response.

    Args:
        expected_valid_code (int): the expected http status code of success.
        response_type (str): what kind of response type to parse to, either json/response/class.

    Raises:
        ValueError: in case the response type is not valid.
        MovieClientApiError: in case the request didn't succeed.
    """

    # class - return a class where the attributes are the json response (including nested fields).
    # response - return the complete response object.
    # json - return a dict/list containing the response.

    response_types = {'class', 'response', 'json'}
    if response_type not in response_types:
        raise ValueError(
            f'Invalid response type ({response_type}) - should be one of ({",".join(response_types)})'
        )

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            # response type will override the response of the class.
            logger.debug(f'Sending HTTP request using function {func.__name__} with args: {args}, kwargs: {kwargs}')
            http_response = func(self, *args, **kwargs)
            if http_response.status_code != expected_valid_code:
                try:
                    response_as_json = http_response.json()
                except JSONDecodeError:
                    raise ApiError(f'Error: ({http_response.text})')
                raise ApiError(f'Error: ({response_as_json})')
            if response_type == 'class':
                return http_response.json(object_hook=lambda response: ApiResponse(**response))
            elif response_type == 'json':
                return http_response.json()
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
