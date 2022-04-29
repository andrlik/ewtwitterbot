import os

import pytest

from ewtwitterbot.imagery import (
    format_quote_for_image,
    format_sentence_for_image,
    get_quote_image,
)

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


@pytest.mark.parametrize(
    "quote_to_test,expected_result",
    [
        (
            {
                "quote": "We've got 85,000 problems and no friends.",
                "quote_rendered": "<p>We've got 85,000 problems and no friends.</p>",
                "source": {
                    "name": "Nix",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "An **awesome** podcast featuring an actual play of Numenera. [Find out more!](https://www.explorerswanted.fm)",  # noqa: E501
                        "description_rendered": '<p>An <strong>awesome</strong> podcast featuring an actual play of Numenera. <a href="https://www.explorerswanted.fm">Find out more!</a></p>',  # noqa: E501
                    },
                    "slug": "ew-nix",
                    "description": "A **Confident Glaive** Who **Needs No Weapons**",
                    "description_rendered": "<p>A <strong>Confident Glaive</strong> Who <strong>Needs No Weapons</strong></p>",  # noqa: E501
                },
                "citation": "Episode 111",
                "citation_url": "https://www.explorerswanted.fm/111",
            },
            """\u201CWe've got 85,000 problems and no friends.\u201D\n\n \u2014Nix, Episode 111""",
        ),
        (
            {
                "quote": "Are your organs inside?",
                "quote_rendered": "<p>Are your organs inside?</p>",
                "source": {
                    "name": "Dili",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "An **awesome** podcast featuring an actual play of Numenera. [Find out more!](https://www.explorerswanted.fm)",  # noqa: E501
                        "description_rendered": '<p>An <strong>awesome</strong> podcast featuring an actual play of Numenera. <a href="https://www.explorerswanted.fm">Find out more!</a></p>',  # noqa: E501
                    },
                    "slug": "ew-dili",
                    "description": "An **Intelligent Wright** Who **Crafts Illusions**",
                    "description_rendered": "<p>An <strong>Intelligent Wright</strong> Who <strong>Crafts Illusions</strong></p>",  # noqa: E501
                },
                "citation": "Episode 109",
                "citation_url": "https://www.explorerswanted.fm/109",
            },
            """\u201CAre your organs inside?\u201D\n\n \u2014Dili, Episode 109""",
        ),
        (
            {
                "quote": 'We said, "more cardio," Dili! This is why you can\'t keep up.',
                "quote_rendered": '<p>We said, "more cardio," Dili! This is why you can\'t keep up.</p>',
                "source": {
                    "name": "ChaCha",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "An **awesome** podcast featuring an actual play of Numenera. [Find out more!](https://www.explorerswanted.fm)",  # noqa: E501
                        "description_rendered": '<p>An <strong>awesome</strong> podcast featuring an actual play of Numenera. <a href="https://www.explorerswanted.fm">Find out more!</a></p>',  # noqa: E501
                    },
                    "slug": "ew-chacha",
                    "description": "A **Passionate Nano** Who **Sees Beyond**.",
                    "description_rendered": "<p>A <strong>Passionate Nano</strong> Who <strong>Sees Beyond</strong>.</p>",  # noqa: E501
                },
                "citation": "Episode 109",
                "citation_url": "https://www.explorerswanted.fm/109",
            },
            """\u201CWe said, "more cardio," Dili! This is why you can't keep up.\u201D\n\n \u2014ChaCha, Episode 109""",  # noqa: E501
        ),
    ],
)
def test_quote_formatting(quote_to_test, expected_result):
    result = format_quote_for_image(quote_to_test)
    assert result == expected_result


@pytest.mark.parametrize(
    "sentence_to_test,character,service_name,expected_result",
    [
        (
            "I'm a robot snek.",
            "Nix",
            "Twitter",
            """\u201CI'm a robot snek.\u201D\n\n \u2014NixBot, Twitter""",  # noqa: E501
        ),
        (
            "This is Other Hand.",
            "ChaCha",
            "Twitter",
            """\u201CThis is Other Hand.\u201D\n\n \u2014ChaChaBot, Twitter""",
        ),
        (
            "I'm a robot snek.",
            "Nix",
            "Mastodon",
            """\u201CI'm a robot snek.\u201D\n\n \u2014NixBot, Mastodon""",  # noqa: E501
        ),
        (
            "This is Other Hand.",
            "ChaCha",
            "Mastodon",
            """\u201CThis is Other Hand.\u201D\n\n \u2014ChaChaBot, Mastodon""",
        ),
    ],
)
def test_sentence_formatting(
    sentence_to_test, character, service_name, expected_result
):
    assert (
        format_sentence_for_image(sentence_to_test, character, service_name)
        == expected_result
    )
