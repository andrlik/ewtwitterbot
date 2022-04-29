import os
from typing import Any, Optional, Union

from loguru import logger
from mastodon import Mastodon, MastodonError

from ewtwitterbot.imagery import get_quote_image
from ewtwitterbot.status_processing import process_request


class MastodonConfigurationError(Exception):
    pass


class MastodonMediaError(Exception):
    pass


def get_credentials_from_environ() -> Mastodon:
    """
    Use environment variables and local files to retrieve Mastodon API instance.
    """
    client_secret: Union[str, Any] = os.environ.get(
        "MASTODON_CLIENT_SECRET_FILE", default=None
    )
    user_secret: Union[str, Any] = os.environ.get(
        "MASTODON_USER_SECRET_FILE", default=None
    )
    api_base_url: Union[str, Any] = os.environ.get(
        "MASTODON_API_BASE_URL", default=None
    )
    if client_secret is None or user_secret is None or api_base_url is None:
        raise MastodonConfigurationError
    return Mastodon(access_token=str(user_secret), api_base_url=str(api_base_url))


def get_last_toot_id(filename: str) -> int:
    """
    Given a filename, fetch the latest toot id, if any.

    :param filename: str
    :return: int
    """
    if os.path.exists(filename):
        with open(filename, "r") as f:
            last_id = int(f.read().strip())
            logger.debug(f"Fetched last id as {last_id}...")
        return last_id
    logger.debug("No saved toot id so returning 1 as error code.")
    return 1


def save_last_toot_id(last_id: int, filename: str) -> None:
    """
    Given an id and a filename, save the id to a file.

    :param last_id: int
    :param filename: str
    """
    with open(filename, "w") as f:
        f.write(str(last_id))
    logger.debug(f"Saved {last_id} to {filename}!")


def upload_image_and_description(
    api: Mastodon, img_filename: str, alt_text: str
) -> str:
    """
    Upload an image via the supplied api wrapper and alt text and retrieve the media id
    created for it as a str.

    :param api: Mastodon
    :param img_filename: str
    :param alt_text: str
    :return: str
    """
    response = api.media_post(media_file=img_filename, description=alt_text)
    if response["type"] != "image":
        raise MastodonMediaError
    return response["id"]


def respond_to_toots(filename: Optional[str] = "last_toot.txt") -> None:
    """
    Given the filename of the stored toot id respond to mastodon mentions.

    :param filename: str
    """
    try:
        api = get_credentials_from_environ()
    except MastodonConfigurationError:  # pragma: nocover
        logger.error("Mastodon is not configured correctly.")
        return
    last_id = get_last_toot_id(filename)

    mentions = api.notifications(mentions_only=True, since_id=last_id)

    if len(mentions) == 0:  # pragma: nocover
        logger.debug("No new mentions on Mastodon! Exiting...")
        return

    text_to_use: Optional[str]
    logger.info("Found notifications on Mastodon...")
    for mention in reversed(mentions):
        if mention["type"] == "mention":
            logger.info("Someone mentioned me on Mastodon...")
            logger.debug(
                f"Mention id is {mention['id']} and it looks like this {mention}"
            )
            logger.info(str(mention["id"]) + " - " + mention["status"]["content"])
            new_id = mention["id"]
            text_to_use, link_to_quote = process_request(
                mention["status"]["content"], "Mastodon"
            )
            if text_to_use is not None:
                logger.debug("Generating image for requested quote/sentence...")
                get_quote_image(text_to_use, filename="mastodon_quote_image.png")
                media_id = upload_image_and_description(
                    api=api,
                    img_filename="mastodon_quote_image.png",
                    alt_text=text_to_use,
                )
                if media_id is None:  # pragma: nocover
                    return
                try:
                    api.status_post(
                        in_reply_to_id=mention["status"]["id"],
                        media_ids=[media_id],
                        visibility="public",
                        status=f"@{mention['status']['account']['acct']} Here you go. Peaceful journeys. {link_to_quote}",  # noqa: E501
                    )
                except MastodonError as e:  # pragma: nocover
                    logger.error(f"Error while posting to Mastodon: {e}")
            save_last_toot_id(new_id, filename)


if __name__ == "__main__":
    respond_to_toots("last_toot.txt")  # pragma: nocover
