import pytest
import requests_mock

from ewtwitterbot.status_processing import process_request


@pytest.mark.parametrize(
    "tweet_text,url_to_mock,mocked_status_code,mocked_response,expected_result,expected_link_url,character_override",
    [
        (
            "@somebot I love your show",
            "https://www.google.com",
            200,
            {},
            None,
            None,
            None,
        ),
        (
            "@somebot #quote",
            "https://quoteservice.andrlik.org/api/groups/ew/get_random_quote/",
            200,
            {
                "id": 4,
                "quote": "I ate too much pie.",
                "quote_rendered": "<p>I ate too much pie.</p>",
                "citation": "Episode 3",
                "citation_url": "https://www.explorerswanted.fm/3",
                "source": {
                    "id": 4,
                    "name": "Nix",
                    "slug": "ew-nix",
                    "description": "Glaive",
                    "description_rendered": "<p>Glaive</p>",
                },
            },
            """\u201CI ate too much pie.\u201D\n\n \u2014Nix, Episode 3""",
            "https://www.explorerswanted.fm/3",
            None,
        ),
        (
            "@somebot #quote",
            "https://quoteservice.andrlik.org/api/groups/ew/get_random_quote/",
            404,
            {"error": "No quote found for this group."},
            None,
            None,
            None,
        ),
        (
            "@somebot #markov",
            "https://quoteservice.andrlik.org/api/sources/ew-nix/generate_sentence/",
            200,
            {"sentence": "The snek was in me all along."},
            """\u201CThe snek was in me all along.\u201D\n\n \u2014NixBot, Twitter""",
            "https://www.explorerswanted.fm",
            {"name": "Nix", "slug": "ew-nix"},
        ),
        (
            "@somebot #markov",
            "https://quoteservice.andrlik.org/api/sources/ew-nix/generate_sentence/",
            403,
            {"error": "This character does not allow sentence generation."},
            None,
            None,
            {"name": "Nix", "slug": "ew-nix"},
        ),
    ],
)
def test_process_tweet(
    tweet_text,
    url_to_mock,
    mocked_status_code,
    mocked_response,
    expected_result,
    expected_link_url,
    character_override,
):
    with requests_mock.Mocker() as m:
        m.get(url_to_mock, status_code=mocked_status_code, json=mocked_response)
        result, link_url = process_request(
            tweet_text, "Twitter", character_to_use=character_override
        )
        assert result == expected_result
        assert link_url == expected_link_url
