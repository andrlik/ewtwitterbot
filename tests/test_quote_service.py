import os
from unittest import mock

import pytest
import requests_mock

from ewtwitterbot.quote_service import (
    QuoteServiceImproperlyConfigured,
    fetch_and_select_random_character,
    generate_sentence,
    get_random_quote,
    list_characters,
    make_headers,
)


def test_configuration_setup():
    names_to_remove = ["QS_TOKEN"]
    modified_environ = {k: v for k, v in os.environ.items() if k not in names_to_remove}
    with mock.patch.dict(os.environ, modified_environ, clear=True):
        with pytest.raises(QuoteServiceImproperlyConfigured):
            make_headers()


@pytest.mark.parametrize(
    "url_to_mock,character",
    [
        ("https://quoteservice.andrlik.org/api/groups/ew/get_random_quote/", None),
        (
            "https://quoteservice.andrlik.org/api/sources/ew-nix/get_random_quote/",
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
                "source": {
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
        ("https://quoteservice.andrlik.org/api/groups/ew/get_random_quote/", None),
        (
            "https://quoteservice.andrlik.org/api/sources/ew-nix/get_random_quote/",
            "Nix",
        ),
    ],
)
def test_request_quote_error(url_to_mock, character):
    with requests_mock.Mocker() as m:
        m.get(
            url_to_mock,
            status_code=404,
            json={"error": "No quotes found."},
        )
        r = get_random_quote(character)
        assert r == 404


@pytest.mark.parametrize(
    "url_to_mock,character",
    [
        ("https://quoteservice.andrlik.org/api/groups/ew/generate_sentence/", None),
        (
            "https://quoteservice.andrlik.org/api/sources/ew-nix/generate_sentence/",
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
        assert type(r) == str and r == "I am a wacky bot sentence!"


@pytest.mark.parametrize(
    "url_to_mock,character",
    [
        ("https://quoteservice.andrlik.org/api/groups/ew/generate_sentence/", None),
        (
            "https://quoteservice.andrlik.org/api/sources/ew-nix/generate_sentence/",
            "Nix",
        ),
    ],
)
def test_generate_sentence_error(url_to_mock, character):
    with requests_mock.Mocker() as m:
        m.get(
            url_to_mock,
            status_code=403,
            json={"error": "Markov generation not allowed."},
        )
        r = generate_sentence(character)
        assert r == 403


def test_list_characters():
    with requests_mock.Mocker() as m:
        m.get(
            "https://quoteservice.andrlik.org/api/sources/",
            status_code=200,
            json=[
                {
                    "name": "Nix",
                    "description": "Glaive",
                    "description_rendered": "<p>Glaive</p>",
                    "slug": "ew-nix",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "podcast",
                        "description_rendered": "<p>podcast</p>",
                    },
                },
                {
                    "name": "Dili",
                    "description": "Wright",
                    "description_rendered": "<p>Wright</p>",
                    "slug": "ew-dili",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "podcast",
                        "description_rendered": "<p>podcast</p>",
                    },
                },
                {
                    "name": "ChaCha",
                    "description": "Nano",
                    "description_rendered": "<p>Nano</p>",
                    "slug": "ew-chacha",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "podcast",
                        "description_rendered": "<p>podcast</p>",
                    },
                },
            ],
        )
        r = list_characters()
        assert len(r) == 3


def test_list_characters_error():
    with requests_mock.Mocker() as m:
        m.get(
            "https://quoteservice.andrlik.org/api/sources/",
            status_code=404,
            json={"error": "No sources found!"},
        )
        r = list_characters()
        assert r == 404


def test_character_to_use():
    with requests_mock.Mocker() as m:
        m.get(
            "https://quoteservice.andrlik.org/api/sources/",
            status_code=200,
            json=[
                {
                    "name": "Nix",
                    "description": "Glaive",
                    "description_rendered": "<p>Glaive</p>",
                    "slug": "ew-nix",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "podcast",
                        "description_rendered": "<p>podcast</p>",
                    },
                },
                {
                    "name": "Dili",
                    "description": "Wright",
                    "description_rendered": "<p>Wright</p>",
                    "slug": "ew-dili",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "podcast",
                        "description_rendered": "<p>podcast</p>",
                    },
                },
                {
                    "name": "ChaCha",
                    "description": "Nano",
                    "description_rendered": "<p>Nano</p>",
                    "slug": "ew-chacha",
                    "group": {
                        "name": "Explorers Wanted",
                        "slug": "ew",
                        "description": "podcast",
                        "description_rendered": "<p>podcast</p>",
                    },
                },
            ],
        )
        assert fetch_and_select_random_character() in [
            {"name": "Nix", "slug": "ew-nix"},
            {"name": "ChaCha", "slug": "ew-chacha"},
            {"name": "Dili", "slug": "ew-dili"},
        ]


def test_error_character_to_use():
    with requests_mock.Mocker() as m:
        m.get(
            "https://quoteservice.andrlik.org/api/sources/",
            status_code=404,
            json={"error": "No characters found!"},
        )
        assert fetch_and_select_random_character() is None
