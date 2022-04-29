import textwrap
from typing import Any, Dict, Optional

from PIL import Image, ImageDraw, ImageFont

# With thanks and apologies to Apoorv Tyagi: https://auth0.com/blog/how-to-make-a-twitter-bot-in-python-using-tweepy/


def get_quote_image(
    quote_text: str,
    font_path: Optional[str] = "Raleway/Raleway-Regular.ttf",
    bgcolor: Optional[tuple] = (126, 47, 139),
    txtcolor: Optional[tuple] = (255, 255, 255),
    filename: Optional[str] = "quote_image.png",
) -> None:
    """
    Given a quote as text, generate an image with the text on it.

    :param quote_text: The quote text.
    :param font_path: Relative path from `fonts` to the ttf font file.
    :param bgcolor: Tuple representation of RGB color to use on background.
    :param txtcolor: Tuple representation of RGB color to use for text.
    :param filename: Filename for generated image.
    :return: str representation of path to generated image.
    """
    image = Image.new("RGB", (800, 400), color=bgcolor)
    font = ImageFont.truetype(f"ewtwitterbot/fonts/{font_path}", 40)
    text_start_height = 100
    draw_text_on_image(image, quote_text, font, txtcolor, text_start_height)
    image.save(filename)


def draw_text_on_image(
    image: Image, text: str, font: ImageFont, text_color: tuple, text_start_height: int
) -> None:
    """
    Given an image, draw the fed text onto it.

    :param image: An instance of PIL.Image
    :param text: Text to draw onto the image.
    :param font: An instance of PIL.ImageFont
    :param text_color: The color to use for the text as an RGB tuple.
    :param text_start_height: int representing the starting height of the text.
    :return: None since it transforms the image in place.
    """
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = text.splitlines()
    for line in lines:
        wrapped_lines = textwrap.wrap(line, width=40, replace_whitespace=True)
        for wline in wrapped_lines:
            line_width, line_height = font.getsize(wline)
            draw.text(
                ((image_width - line_width) / 2, y_text),
                wline,
                font=font,
                align="center",
                fill=text_color,
            )
            y_text += line_height


def format_quote_for_image(quote: Dict[str, Any]) -> str:
    """
    Given a dict representation of a quote object, format it for our image generation.

    :param quote: dict representation of quote
    :return: str
    """
    return f"""\u201C{quote['quote']}\u201D\n\n \u2014{quote["source"]["name"]}, {quote['citation']}"""


def format_sentence_for_image(
    sentence: str, character_name: str, service_name: str
) -> str:
    """
    Given the sentence, character name, and service name, e.g. "Twitter", form the string
    to write upon the quote image.

    :param sentence: str
    :param character_name: str
    :param service_name: str
    :return: str
    """
    return f"""\u201C{sentence}\u201D\n\n \u2014{character_name}Bot, {service_name}"""
