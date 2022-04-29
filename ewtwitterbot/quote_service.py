import os
import random
from typing import Any, Dict, List, Optional, Union

import requests
from loguru import logger


class QuoteServiceImproperlyConfigured(Exception):
    pass


def make_headers() -> Dict[str, str]:
    qs_token = os.environ.get("QS_TOKEN", default=None)
    if qs_token is None:
        raise QuoteServiceImproperlyConfigured
    return {"Authorization": f"Token {qs_token}"}


def get_random_quote(character: Optional[str] = None) -> Union[Dict[str, Any], int]:
    """
    Fetch a quote from the quoteservice backend.

    :param character: An optional string representing a specific character, e.g. 'nix'
    :return: A dict representation of the quote object, or an int representing an error code.
    """
    hostname = "https://quoteservice.andrlik.org/api/"
    url = f"{hostname}groups/ew/get_random_quote/"
    if character is not None:
        url = f"{hostname}sources/ew-{character.lower()}/get_random_quote/"
    r = requests.get(url, headers=make_headers())
    if r.status_code != 200:
        return r.status_code
    return r.json()


def generate_sentence(character: Optional[str] = None) -> Union[str, int]:
    """
    Request a generated sentence via markov chain from the quoteservice.

    :param character: An optional string representing a character, e.g. 'nix'
    :return: str representing the sentence or an int representing an error code.
    """
    hostname = "https://quoteservice.andrlik.org/api/"
    url = f"{hostname}groups/ew/generate_sentence/"
    if character is not None:
        url = f"{hostname}sources/ew-{character.lower()}/generate_sentence/"
    r = requests.get(url, headers=make_headers())
    if r.status_code != 200:
        return r.status_code
    return r.json()["sentence"]


def list_characters() -> Union[List[Dict[str, str]], int]:
    """
    Fetch a list of valid characters from the quote server.

    :return: Either a list of dict representations of the characters and their slugs, or an int error code.
    """
    url = "https://quoteservice.andrlik.org/api/sources/"
    r = requests.get(url, headers=make_headers())
    if r.status_code != 200:
        return r.status_code
    return [
        {"name": character["name"], "slug": character["slug"]} for character in r.json()
    ]


def fetch_and_select_random_character() -> Optional[Dict[str, Any]]:
    """
    Fetch a list of characters and return a random one as a dict of name and slug.
    We separate this function to help with unit testing.
    :return: dict object
    """
    character_result = list_characters()
    if type(character_result) == int:
        logger.error(
            f"The QuoteService responded to a character request with error {character_result}"
        )
        return None
    return random.choice(character_result)
