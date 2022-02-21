# import tweepy
from typing import Dict, Union


def format_quote_for_image(quote: Dict[str, Union[str, int]]) -> str:
    """
    Given a dict represenation of a quote object, format it for our image generation.

    :param quote: dict representation of quote
    :return: str
    """
    return f"""\u201C{quote['quote']}\u201D\n\n \u2014{quote["character"]["name"]}, {quote['citation']}"""
