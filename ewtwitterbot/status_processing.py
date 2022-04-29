from typing import Dict, Optional, Tuple

from loguru import logger

from ewtwitterbot.imagery import format_quote_for_image, format_sentence_for_image
from ewtwitterbot.quote_service import (
    fetch_and_select_random_character,
    generate_sentence,
    get_random_quote,
)


def process_request(
    mention: str, service_name: str, character_to_use: Optional[Dict[str, str]] = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Given the full text of a mention, and a service name, e.g. 'Twitter',
    return the text to use or None.

    :param mention: str
    :param service_name: str
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
            format_sentence_for_image(
                sentence_result, character_to_use["name"], service_name
            ),
            "https://www.explorerswanted.fm",
        )
    return None, None
