import pytest

from ewtwitterbot.twitter_bot import format_quote_for_image


@pytest.mark.parametrize(
    "quote_to_test,expected_result",
    [
        (
            {
                "quote": "We've got 85,000 problems and no friends.",
                "quote_rendered": "<p>We've got 85,000 problems and no friends.</p>",
                "character": {
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
                "character": {
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
                "character": {
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
