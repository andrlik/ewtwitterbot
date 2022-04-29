import os
from typing import Any, Optional, Union

import tweepy
from loguru import logger

from ewtwitterbot.imagery import get_quote_image
from ewtwitterbot.status_processing import process_request


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
    logger.info("Someone mentioned me on Twitter.")
    for mention in reversed(mentions):
        logger.info(str(mention.id) + "-" + mention.full_text)
        new_id = mention.id
        text_to_use, link_to_quote = process_request(mention.full_text, "Twitter")
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
