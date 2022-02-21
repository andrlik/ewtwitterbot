import os

import pytest

from ewtwitterbot.imagery import get_quote_image

# I don't know how to reliably test this function besides ensuring the file gets created. Pull requests to improve
# the reliability of this test with regard to the quality of the text layout would be very welcome.


@pytest.mark.parametrize(
    "quote_text",
    [
        """\u201CWe always go right\u201D\n\n \u2014Nix, Episode 300""",
        """\u201CI'm so fancy! Too fancy for just any podcast. Only EW will satisfy.\u201D\n\n \u2014Daniel, Episode 420""",  # noqa: E501
    ],
)
def test_generate_image(quote_text):
    if os.path.exists("quote_image.png"):
        os.remove("quote_image.png")
    get_quote_image(quote_text)
    assert os.path.exists("quote_image.png")
    os.remove("quote_image.png")
