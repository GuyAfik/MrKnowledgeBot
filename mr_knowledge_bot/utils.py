from typing import Optional, Any


def is_english_letters_movie(name: str):
    try:
        name.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


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