import os
import random
from typing import Any, Dict, Optional, Tuple, Union

import tweepy
from loguru import logger

from ewtwitterbot.imagery import get_quote_image
from ewtwitterbot.quote_service import (
    generate_sentence,
    get_random_quote,
    list_characters,
)


class TwitterImproperlyConfigured(Exception):
    pass


def get_credentials_from_environ() -> tweepy.API:
    """
    Sets our credentials from the environment variables.
    """
    consumer_key: Union[str, Any] = os.environ.get("TWITTER_CONSUMER_KEY", default=None)
    consumer_secret: Union[str, Any] = os.environ.get(
        "TWITTER_CONSUMER_SECRET", default=None
    )
    access_token: Union[str, Any] = os.environ.get("TWITTER_ACCESS_TOKEN", default=None)
    access_token_secret: Union[str, Any] = os.environ.get(
        "TWITTER_ACCESS_TOKEN_SECRET", default=None
    )

    if (
        consumer_key is None
        or consumer_secret is None
        or access_token is None
        or access_token_secret is None
    ):
        raise TwitterImproperlyConfigured
    auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def format_quote_for_image(quote: Dict[str, Any]) -> str:
    """
    Given a dict representation of a quote object, format it for our image generation.

    :param quote: dict representation of quote
    :return: str
    """
    return f"""\u201C{quote['quote']}\u201D\n\n \u2014{quote["character"]["name"]}, {quote['citation']}"""


def format_sentence_for_image(sentence: str, character_name: str) -> str:
    """
    Given the sentence and character name, form the string to write upon the quote image.

    :param sentence: str
    :param character_name: str
    :return: str
    """
    return f"""\u201C{sentence}\u201D\n\n \u2014{character_name}Bot, Twitter"""


def get_last_tweet_id(filename: str) -> int:
    """
    Get the stored last tweet id that we responded to.

    :param filename: str representation of path to filename.
    :return: int representation of tweet id.
    """
    if os.path.exists(filename):
        with open(filename, "r") as f:
            last_id = int(f.read().strip())
            logger.debug(f"Fetched last tweet id as {last_id}.")
        return last_id
    logger.debug("No previous tweet id saved. Returning 1 as error code.")
    return 1  # if no id checked yet, provide the earliest ever, and it becomes our error code.


def save_last_tweet_id(filename: str, tweet_id: int) -> None:
    """
    Save the last tweet id we replied to in a file.

    :param filename: str representation of path to file
    :param tweet_id: The int representation of the tweet id.
    :return:
    """
    with open(filename, "w") as f:
        f.write(str(tweet_id))
    logger.info(f"Saved last tweet responded to as {tweet_id}")


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


def process_tweet_request(
    mention: str, character_to_use: Optional[Dict[str, str]] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Given the full text of a twitter mention, return the text to use or None.

    :param mention: str
    :param character_to_use: dict of character and slug. Mostly for testing.
    :return: str or None for both image text to use and citation url.
    """
    if "quote" in mention.lower():
        logger.info("They appear to be asking for a random quote.")
        quote_result = get_random_quote()
        if type(quote_result) == int:
            logger.error(
                f"This quote request resulted in an error {quote_result} from QuoteServer."
            )
            return None, None
        return format_quote_for_image(quote_result), quote_result["citation_url"]
    if "markov" in mention.lower():
        logger.info("They appear to be asking for a markov generated sentence.")
        if character_to_use is None:  # pragma: no cover
            character_to_use = fetch_and_select_random_character()
        if (
            character_to_use is None
        ):  # pragma: no cover This is already tested in other methods.
            return None, None
        sentence_result = generate_sentence(character_to_use["slug"][3:])
        if type(sentence_result) == int:
            logger.error(
                f"The sentence request to the QuoteServer responded with code {sentence_result}."
            )
            return None, None
        return (
            format_sentence_for_image(sentence_result, character_to_use["name"]),
            "https://www.explorerswanted.fm",
        )
    return None, None


def upload_image_and_set_metadata(
    api: tweepy.API, image_filename: str, alt_text: str
) -> Optional[int]:
    """
    Given a filename, upload it to twitter, set the alt text, and return the media object for use later.

    :param api: An instance of an authenticated tweepy.API
    :param image_filename: str
    :param alt_text: str
    :return: media_id, or None on a failure.
    """
    try:
        media = api.media_upload(image_filename)
        api.create_media_metadata(media.media_id, alt_text=alt_text)
    except tweepy.errors.TweepyException as e:  # pragma: no cover
        logger.error(f"Error trying to upload media to twitter. {e}")
        return None
    return media.media_id


def respond_to_tweets(filename: Optional[str] = "last_tweet.txt") -> None:
    """
    Respond to recent mentions that include one of the command words.

    :param filename: str representation of path to filename for last tweet id
    :return:
    """
    api = get_credentials_from_environ()
    last_id = get_last_tweet_id(filename)

    mentions = api.mentions_timeline(since_id=last_id, tweet_mode="extended")

    if len(mentions) == 0:  # pragma: nocover
        logger.debug("No new mentions! Exiting...")
        return
    text_to_use: Optional[str]
    logger.info("Someone mentioned me.")
    for mention in reversed(mentions):
        logger.info(str(mention.id) + "-" + mention.full_text)
        new_id = mention.id
        text_to_use, link_to_quote = process_tweet_request(mention.full_text)
        if text_to_use is not None:
            logger.debug("Creating image for requested quote/sentence...")
            get_quote_image(text_to_use)
            media_id = upload_image_and_set_metadata(
                api,
                "quote_image.png",
                alt_text=f"White text on purple background reads: {text_to_use}",
            )
            if media_id is None:  # pragma: nocover
                return
            try:
                api.update_status(
                    status=f"@{mention.user.screen_name} Here you go. Peaceful journeys. {link_to_quote}",
                    in_reply_to_status_id=mention.id,
                    media_ids=[media_id],
                )
            except tweepy.errors.TweepyException:  # pragma: nocover
                logger.info(f"Already replied to {mention.id}")
        save_last_tweet_id(filename, new_id)


if __name__ == "__main__":  # pragma: nocover
    respond_to_tweets("last_tweet.txt")