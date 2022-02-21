import pytest
import requests_mock

from ewtwitterbot.quote_service import generate_sentence, get_random_quote


@pytest.mark.parametrize(
    "url_to_mock,character",
    [
        ("https://quoteservice.andrlik.org/api/groups/ew/get_random_quote/", None),
        (
            "https://quoteservice.andrlik.org/api/characters/ew-nix/get_random_quote/",
            "Nix",
        ),
    ],
)
def test_request_quote(url_to_mock, character):
    with requests_mock.Mocker() as m:
        m.get(
            url_to_mock,
            status_code=200,
            json={
                "id": 4,
                "quote": "I ate too much pie.",
                "quote_rendered": "<p>I ate too much pie.</p>",
                "citation": "some episode num",
                "citation_url": "https://www.explorerswanted.fm/3",
                "character": {
                    "id": 4,
                    "name": "Nix",
                    "slug": "ew-nix",
                    "description": "Glaive",
                    "description_rendered": "<p>Glaive</p>",
                },
            },
        )
        r = get_random_quote(character)
        assert r["quote"] == "I ate too much pie."


@pytest.mark.parametrize(
    "url_to_mock,character",
    [
        ("https://quoteservice.andrlik.org/api/groups/ew/generate_sentence/", None),
        (
            "https://quoteservice.andrlik.org/api/characters/ew-nix/generate_sentence/",
            "Nix",
        ),
    ],
)
def test_generate_sentence(url_to_mock, character):
    with requests_mock.Mocker() as m:
        m.get(
            url_to_mock,
            status_code=200,
            json={"sentence": "I am a wacky bot sentence!"},
        )
        r = generate_sentence(character)
        assert r == "I am a wacky bot sentence!"
