import json

import pytest
import requests
from mr_knowledge_bot.bot.conversations import MovieConversation
from telegram.ext import ConversationHandler
from mr_knowledge_bot.bot.clients.base_client import response_to_movie_entities


BASE_URL = 'https://test_api.com/'


def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


@pytest.fixture()
def movie_conversation_no_repeat(mocker, telegram_context, telegram_update) -> MovieConversation:

    def get_movies_from_context_side_effect_with_no_repeat(key):
        if key == 'movies':
            return response_to_movie_entities(
                load_json('test_data/search_movies_response.json')[0]
            )
        return None

    mocker.patch.object(
        telegram_context.user_data, 'get', side_effect=get_movies_from_context_side_effect_with_no_repeat
    )
    return MovieConversation(telegram_update, telegram_context)


@pytest.fixture()
def movie_conversation_with_repeat(mocker, telegram_context, telegram_update) -> MovieConversation:
    def get_movies_from_context_side_effect_with_repeat(key):
        if key == 'movies':
            return response_to_movie_entities(
                load_json('test_data/search_movies_response.json')[0]
            )
        elif key == 'repeat':
            return True
        return None

    mocker.patch.object(
        telegram_context.user_data, 'get', side_effect=get_movies_from_context_side_effect_with_repeat
    )
    return MovieConversation(telegram_update, telegram_context)


def test_find_movies_by_name_command(mocker, movie_conversation_no_repeat):
    """
    Given:
     - api response with of two pages containing 20 movies each
     - limit = 5, sort_by = 'popularity'

    When:
     - executing the command '/find_movies_by-name',

    Then:
     - make sure movies were found and that only 5 were returned.
     - make sure the next stage in the conversation is the query movie details stage.
    """
    api_response = requests.Response()
    api_response.status_code = 200

    mocker.patch.object(api_response, 'json', side_effect=load_json('test_data/search_movies_response.json'))
    mocker.patch.object(requests, 'request', return_value=api_response)

    next_stage = movie_conversation_no_repeat.find_movies_by_name_command(name='escape', limit=5, sort_by='popularity')
    assert movie_conversation_no_repeat.update.effective_message.reply_text.called
    assert movie_conversation_no_repeat.update.effective_message.reply_text.call_args.kwargs['text'] == \
           'Found the following movies for you 😀\n\nThe Great Escape\nThe Great Escape\nEscape from Alcatraz' \
           '\nEscape from Alcatraz\nEscape from New York'
    assert movie_conversation_no_repeat.context.bot.send_message.called
    assert next_stage == movie_conversation_no_repeat.query_movie_details_stage


def test_find_movies_by_name_command_movies_not_found(mocker, movie_conversation_no_repeat):
    """
    Given:
     - api response indicating no movies were found.
     - limit = 5, sort_by = 'popularity'

    When:
     - executing the command '/find_movies_by-name',

    Then:
     - make sure no movies were found.
     - make sure the next stage in the conversation ConversationHandler.END
    """
    api_response = requests.Response()
    api_response.status_code = 200

    mocker.patch.object(api_response, 'json', return_value={'results': []})
    mocker.patch.object(requests, 'request', return_value=api_response)

    next_stage = movie_conversation_no_repeat.find_movies_by_name_command(name='escape', limit=5, sort_by='popularity')
    assert next_stage == ConversationHandler.END
    assert movie_conversation_no_repeat.update.effective_message.reply_text.call_args.kwargs['text'] == \
           'Could not find any movies for you 😞'


def test_query_movie_details_stage_with_yes_answer(movie_conversation_no_repeat):
    """
    Given:
     - 20 movies that were stored in the context
     - callback query = 'yes' for viewing movie details.

    When:
     - executing the query_movie_details method.

    Then:
     - make sure a message is sent indicating to choose a movie from a keyboard markup.
     - make sure the keyboard markup contains all the movies that was stored in the context.
     - make sure the next stage is to display the details of a movie.
    """
    movie_conversation_no_repeat.update.callback_query.data = 'y'

    next_stage = movie_conversation_no_repeat.query_movie_details()
    assert next_stage == movie_conversation_no_repeat.display_movie_details_stage
    assert len(movie_conversation_no_repeat.context.bot.send_message.call_args.kwargs['reply_markup'].keyboard) == 20
    assert movie_conversation_no_repeat.context.bot.send_message.call_args.kwargs['text'] == \
           'Please choose a movie from the list to get its overview 🎬'


def test_query_movie_details_stage_with_no_answer_with_no_repeat(movie_conversation_no_repeat):
    """
    Given:
    - answer indicating that user don't want to see movie details (which is not a repeat process)

    When:
    - executing the query_movie_details method.

    Then:
    - make sure the next stage is to query for the movie trailer.
    """
    movie_conversation_no_repeat.update.callback_query.data = 'n'
    next_stage = movie_conversation_no_repeat.query_movie_details()

    assert next_stage == movie_conversation_no_repeat.query_movie_for_trailer_stage


def test_query_movie_details_stage_with_repeat(movie_conversation_with_repeat):
    """
    Given:
    - answer indicating that user don't want to see movie details (which is a repeat process)

    When:
    - executing the query_movie_details method.

    Then:
    - make sure the next stage is ConversationHandler.END
    """
    movie_conversation_with_repeat.update.callback_query.data = 'n'
    next_stage = movie_conversation_with_repeat.query_movie_details()

    assert next_stage == ConversationHandler.END


def test_display_movie_with_valid_movie(mocker, movie_conversation_no_repeat):
    """
    Given:
    - movie details api response
    - valid movie that was chosen to get its details.

    When:
    - executing the query_movie_details method.

    Then:
    - make sure the next stage is to query movie trailer.
    """
    api_response = requests.Response()
    api_response.status_code = 200

    mocker.patch.object(api_response, 'json', return_value=load_json('test_data/movie_details_response.json'))
    mocker.patch.object(requests, 'request', return_value=api_response)

    movie_conversation_no_repeat.update.message.text = 'Escape Plan 2: Hades'
    next_stage = movie_conversation_no_repeat.display_movie_details()

    assert movie_conversation_no_repeat.update.effective_message.reply_text.call_args.kwargs['text'] == \
           "*Escape Plan 2: Hades - (Overview)*\n\nRay Breslin manages an elite team of security" \
           " specialists trained in the art of breaking people out of the world's most impenetrable" \
           " prisons. When his most trusted operative, Shu Ren, is kidnapped and disappears inside the" \
           " most elaborate prison ever built, Ray must track him down with the help of some of his former" \
           " friends.\n\n*Duration:* 1:36:00\n\n*Homepage:* https://www.escapeplan2.movie/\n\n*Status:* " \
           "Released\n\n*Release date:* 2018-06-05"

    assert next_stage == movie_conversation_no_repeat.query_movie_for_trailer_stage
