import os
from unittest import mock

import pytest
import requests_mock

from ewtwitterbot.imagery import get_quote_image
from ewtwitterbot.mastodon_bot import (
    MastodonConfigurationError,
    MastodonMediaError,
    get_credentials_from_environ,
    get_last_toot_id,
    respond_to_toots,
    save_last_toot_id,
    upload_image_and_description,
)


@pytest.fixture
def save_a_toot_id():
    with open("test_last_toot.txt", "w") as f:
        f.write(str(14))


def test_retrieve_last_toot_id_saved(save_a_toot_id):
    assert get_last_toot_id("test_last_toot.txt") == 14


def test_save_toot_id():
    if os.path.exists("test_last_toot.txt"):
        os.remove("test_last_toot.txt")
    save_last_toot_id(40, "test_last_toot.txt")
    assert os.path.exists("test_last_toot.txt")
    assert get_last_toot_id("test_last_toot.txt") == 40


def test_retrieve_nonexistent_tweet_id():
    if os.path.exists("test_last_toot.txt"):
        os.remove("test_last_toot.txt")
    assert get_last_toot_id("test_last_toot.txt") == 1


def test_mastodon_configuration_checks():
    names_to_remove = [
        "MASTODON_CLIENT_SECRET_FILE",
        "MASTODON_USER_SECRET_FILE",
        "MASTODON_API_BASE_URL",
    ]
    modified_environ = {k: v for k, v in os.environ.items() if k not in names_to_remove}
    with mock.patch.dict(os.environ, modified_environ, clear=True):
        with pytest.raises(MastodonConfigurationError):
            get_credentials_from_environ()


@pytest.fixture
def mastodon_environ_patch():
    return {
        "MASTODON_API_BASE_URL": "https://botsin.space",
        "MASTODON_CLIENT_SECRET_FILE": "test_ewbot_clientcred.secret",
        "MASTODON_USER_SECRET_FILE": "test_ewbot_usercred.secret",
    }


def test_mastodon_media_upload_success(mastodon_environ_patch):
    with mock.patch.dict(os.environ, mastodon_environ_patch, clear=False):
        with requests_mock.Mocker() as m:
            m.post(
                "https://botsin.space/api/v1/media",
                status_code=200,
                json={
                    "id": "234567",
                    "type": "image",
                    "url": "https://files.botsin.space/media_attachments/files/022/033/641/original/quote_image.png",
                    "preview_url": "https://files.botsin.space/media_attachments/files/022/033/641/small/quote_image.png",  # noqa: E501
                    "remote_url": None,
                    "text_url": "https://botsin.space/media/4Zj6ewxzzzDi0g8JnZQ",
                    "meta": {
                        "focus": {"x": -0.69, "y": 0.42},
                        "original": {
                            "width": 640,
                            "height": 480,
                            "size": "640x480",
                            "aspect": 1.3333333333333333,
                        },
                        "small": {
                            "width": 461,
                            "height": 346,
                            "size": "461x346",
                            "aspect": 1.3323699421965318,
                        },
                    },
                    "description": "test uploaded via api",
                    "blurhash": "UFBWY:8_0Jxv4mx]t8t64.%M-:IUWGWAt6M}",
                },
            )
            get_quote_image("Hi There")
            assert (
                upload_image_and_description(
                    get_credentials_from_environ(),
                    "quote_image.png",
                    alt_text="Hi there",
                )
                == 234567
            )


def test_media_upload_error(mastodon_environ_patch):
    with mock.patch.dict(os.environ, mastodon_environ_patch, clear=False):
        with requests_mock.Mocker() as m:
            m.post(
                "https://botsin.space/api/v1/media",
                status_code=200,
                json={
                    "id": "234567",
                    "type": "unknown",
                    "url": "https://files.botsin.space/media_attachments/files/022/033/641/original/quote_image.png",
                    "preview_url": "https://files.botsin.space/media_attachments/files/022/033/641/small/quote_image.png",  # noqa: E501
                    "remote_url": None,
                    "text_url": "https://botsin.space/media/4Zj6ewxzzzDi0g8JnZQ",
                    "meta": {
                        "focus": {"x": -0.69, "y": 0.42},
                        "original": {
                            "width": 640,
                            "height": 480,
                            "size": "640x480",
                            "aspect": 1.3333333333333333,
                        },
                        "small": {
                            "width": 461,
                            "height": 346,
                            "size": "461x346",
                            "aspect": 1.3323699421965318,
                        },
                    },
                    "description": "test uploaded via api",
                    "blurhash": "UFBWY:8_0Jxv4mx]t8t64.%M-:IUWGWAt6M}",
                },
            )
            get_quote_image("Hi There")
            with pytest.raises(MastodonMediaError):
                upload_image_and_description(
                    get_credentials_from_environ(),
                    "quote_image.png",
                    alt_text="Hi there",
                )


def test_mastodon_mention_cycle(mastodon_environ_patch):
    with mock.patch.dict(os.environ, mastodon_environ_patch, clear=False):
        with requests_mock.Mocker() as m:
            m.post(
                "https://botsin.space/api/v1/media",
                status_code=200,
                json={
                    "id": "234567",
                    "type": "image",
                    "url": "https://files.botsin.space/media_attachments/files/022/033/641/original/quote_image.png",
                    "preview_url": "https://files.botsin.space/media_attachments/files/022/033/641/small/quote_image.png",  # noqa: E501
                    # noqa: E501
                    "remote_url": None,
                    "text_url": "https://botsin.space/media/4Zj6ewxzzzDi0g8JnZQ",
                    "meta": {
                        "focus": {"x": -0.69, "y": 0.42},
                        "original": {
                            "width": 640,
                            "height": 480,
                            "size": "640x480",
                            "aspect": 1.3333333333333333,
                        },
                        "small": {
                            "width": 461,
                            "height": 346,
                            "size": "461x346",
                            "aspect": 1.3323699421965318,
                        },
                    },
                    "description": "test uploaded via api",
                    "blurhash": "UFBWY:8_0Jxv4mx]t8t64.%M-:IUWGWAt6M}",
                },
            )
            m.get(
                "https://botsin.space/api/v1/notifications",
                status_code=200,
                json=[
                    {
                        "id": 4772149,
                        "type": "mention",
                        "created_at": "2019-11-23T07:29:18.903Z",
                        "account": {
                            "id": 18639,
                            "username": "andrlik",
                            "acct": "andrlik@wandering.shop",
                            "display_name": "Daniel Andrlik",
                            "locked": True,
                            "bot": False,
                            "discoverable": True,
                            "group": False,
                            "created_at": "2019-11-23T07:29:18.903Z",
                            "note": '<p>Product exec, SFF Writer, Producer and GM of the Explorers Wanted actual play podcast. </p><p><a href="https://wandering.shop/tags/ActuallyAutistic" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>ActuallyAutistic</span></a>/ADHD, with a dash of GAD for spice.</p><p>He/him</p><p>Your mom loves me.</p><p>Location: secluded in a blanket fort</p>',  # noqa: E501
                            "url": "https://wandering.shop/@andrlik",
                            "avatar": "https://files.botsin.space/cache/accounts/avatars/000/018/639/original/91b7036b36a321fe.jpeg",  # noqa: E501
                            "avatar_static": "https://files.botsin.space/cache/accounts/avatars/000/018/639/original/91b7036b36a321fe.jpeg",  # noqa: E501
                            "header": "https://files.botsin.space/cache/accounts/headers/000/018/639/original/08dfb894386d40d0.jpeg",  # noqa: E501
                            "header_static": "https://files.botsin.space/cache/accounts/headers/000/018/639/original/08dfb894386d40d0.jpeg",  # noqa: E501
                            "followers_count": 81,
                            "following_count": 148,
                            "statuses_count": 869,
                            "last_status_at": "2019-11-23T07:29:18.903Z",
                            "emojis": [],
                            "fields": [
                                {
                                    "name": "Website",
                                    "value": '<a href="https://www.andrlik.org" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://www.</span><span class="">andrlik.org</span><span class="invisible"></span></a>',  # noqa: E501
                                    "verified_at": "2022-04-29T14:58:32.014+00:00",
                                },
                                {
                                    "name": "Twitter",
                                    "value": '<a href="https://twitter.com/andrlik" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">twitter.com/andrlik</span><span class="invisible"></span></a>',  # noqa: E501
                                    "verified_at": None,
                                },
                                {
                                    "name": "Github",
                                    "value": '<a href="https://github.com/andrlik" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">github.com/andrlik</span><span class="invisible"></span></a>',  # noqa: E501
                                    "verified_at": None,
                                },
                                {
                                    "name": "Podcast",
                                    "value": '<a href="https://www.explorerswanted.fm" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://www.</span><span class="">explorerswanted.fm</span><span class="invisible"></span></a>',  # noqa: E501
                                    "verified_at": None,
                                },
                            ],
                        },
                        "status": {
                            "id": 108216032166128570,
                            "created_at": "2019-11-23T07:29:18.903Z",
                            "in_reply_to_id": None,
                            "in_reply_to_account_id": None,
                            "sensitive": False,
                            "spoiler_text": "",
                            "visibility": "public",
                            "language": "en",
                            "uri": "https://wandering.shop/users/andrlik/statuses/108216031335496737",
                            "url": "https://wandering.shop/@andrlik/108216031335496737",
                            "replies_count": 0,
                            "reblogs_count": 0,
                            "favourites_count": 0,
                            "favourited": False,
                            "reblogged": False,
                            "muted": False,
                            "bookmarked": False,
                            "content": '<p><span class="h-card"><a href="https://botsin.space/@ewbot" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>ewbot</span></a></span> Quote please</p>',  # noqa: E501
                            "reblog": None,
                            "account": {
                                "id": 18639,
                                "username": "andrlik",
                                "acct": "andrlik@wandering.shop",
                                "display_name": "Daniel Andrlik",
                                "locked": True,
                                "bot": False,
                                "discoverable": True,
                                "group": False,
                                "created_at": "2019-11-23T07:29:18.903Z",
                                "note": '<p>Product exec, SFF Writer, Producer and GM of the Explorers Wanted actual play podcast. </p><p><a href="https://wandering.shop/tags/ActuallyAutistic" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>ActuallyAutistic</span></a>/ADHD, with a dash of GAD for spice.</p><p>He/him</p><p>Your mom loves me.</p><p>Location: secluded in a blanket fort</p>',  # noqa: E501
                                "url": "https://wandering.shop/@andrlik",
                                "avatar": "https://files.botsin.space/cache/accounts/avatars/000/018/639/original/91b7036b36a321fe.jpeg",  # noqa: E501
                                "avatar_static": "https://files.botsin.space/cache/accounts/avatars/000/018/639/original/91b7036b36a321fe.jpeg",  # noqa: E501
                                "header": "https://files.botsin.space/cache/accounts/headers/000/018/639/original/08dfb894386d40d0.jpeg",  # noqa: E501
                                "header_static": "https://files.botsin.space/cache/accounts/headers/000/018/639/original/08dfb894386d40d0.jpeg",  # noqa: E501
                                "followers_count": 81,
                                "following_count": 148,
                                "statuses_count": 869,
                                "last_status_at": "2019-11-23T07:29:18.903Z",
                                "emojis": [],
                                "fields": [
                                    {
                                        "name": "Website",
                                        "value": '<a href="https://www.andrlik.org" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://www.</span><span class="">andrlik.org</span><span class="invisible"></span></a>',  # noqa: E501
                                        "verified_at": "2022-04-29T14:58:32.014+00:00",
                                    },
                                    {
                                        "name": "Twitter",
                                        "value": '<a href="https://twitter.com/andrlik" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">twitter.com/andrlik</span><span class="invisible"></span></a>',  # noqa: E501
                                        "verified_at": None,
                                    },
                                    {
                                        "name": "Github",
                                        "value": '<a href="https://github.com/andrlik" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">github.com/andrlik</span><span class="invisible"></span></a>',  # noqa: E501
                                        "verified_at": None,
                                    },
                                    {
                                        "name": "Podcast",
                                        "value": '<a href="https://www.explorerswanted.fm" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://www.</span><span class="">explorerswanted.fm</span><span class="invisible"></span></a>',  # noqa: E501
                                        "verified_at": None,
                                    },
                                ],
                            },
                            "media_attachments": [],
                            "mentions": [
                                {
                                    "id": 108215876835523723,
                                    "username": "ewbot",
                                    "url": "https://botsin.space/@ewbot",
                                    "acct": "ewbot",
                                }
                            ],
                            "tags": [],
                            "emojis": [],
                            "card": None,
                            "poll": None,
                        },
                    }
                ],
            )
            m.post(
                "https://botsin.space/api/v1/statuses",
                status_code=200,
                json={
                    "id": 108216032166128570,
                    "created_at": "2019-11-23T07:29:18.903Z",
                    "in_reply_to_id": None,
                    "in_reply_to_account_id": None,
                    "sensitive": False,
                    "spoiler_text": "",
                    "visibility": "public",
                    "language": "en",
                    "uri": "https://wandering.shop/users/andrlik/statuses/108216031335496737",
                    "url": "https://wandering.shop/@andrlik/108216031335496737",
                    "replies_count": 0,
                    "reblogs_count": 0,
                    "favourites_count": 0,
                    "favourited": False,
                    "reblogged": False,
                    "muted": False,
                    "bookmarked": False,
                    "content": '<p><span class="h-card"><a href="https://botsin.space/@ewbot" class="u-url mention" rel="nofollow noopener noreferrer" target="_blank">@<span>ewbot</span></a></span> Quote please</p>',  # noqa: E501
                    "reblog": None,
                    "account": {
                        "id": 18639,
                        "username": "andrlik",
                        "acct": "andrlik@wandering.shop",
                        "display_name": "Daniel Andrlik",
                        "locked": True,
                        "bot": False,
                        "discoverable": True,
                        "group": False,
                        "created_at": "2019-11-23T07:29:18.903Z",
                        "note": '<p>Product exec, SFF Writer, Producer and GM of the Explorers Wanted actual play podcast. </p><p><a href="https://wandering.shop/tags/ActuallyAutistic" class="mention hashtag" rel="nofollow noopener noreferrer" target="_blank">#<span>ActuallyAutistic</span></a>/ADHD, with a dash of GAD for spice.</p><p>He/him</p><p>Your mom loves me.</p><p>Location: secluded in a blanket fort</p>',  # noqa: E501
                        "url": "https://wandering.shop/@andrlik",
                        "avatar": "https://files.botsin.space/cache/accounts/avatars/000/018/639/original/91b7036b36a321fe.jpeg",  # noqa: E501
                        "avatar_static": "https://files.botsin.space/cache/accounts/avatars/000/018/639/original/91b7036b36a321fe.jpeg",  # noqa: E501
                        "header": "https://files.botsin.space/cache/accounts/headers/000/018/639/original/08dfb894386d40d0.jpeg",  # noqa: E501
                        "header_static": "https://files.botsin.space/cache/accounts/headers/000/018/639/original/08dfb894386d40d0.jpeg",  # noqa: E501
                        "followers_count": 81,
                        "following_count": 148,
                        "statuses_count": 869,
                        "last_status_at": "2019-11-23T07:29:18.903Z",
                        "emojis": [],
                        "fields": [
                            {
                                "name": "Website",
                                "value": '<a href="https://www.andrlik.org" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://www.</span><span class="">andrlik.org</span><span class="invisible"></span></a>',  # noqa: E501
                                "verified_at": "2022-04-29T14:58:32.014+00:00",
                            },
                            {
                                "name": "Twitter",
                                "value": '<a href="https://twitter.com/andrlik" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">twitter.com/andrlik</span><span class="invisible"></span></a>',  # noqa: E501
                                "verified_at": None,
                            },
                            {
                                "name": "Github",
                                "value": '<a href="https://github.com/andrlik" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://</span><span class="">github.com/andrlik</span><span class="invisible"></span></a>',  # noqa: E501
                                "verified_at": None,
                            },
                            {
                                "name": "Podcast",
                                "value": '<a href="https://www.explorerswanted.fm" rel="nofollow noopener noreferrer" target="_blank"><span class="invisible">https://www.</span><span class="">explorerswanted.fm</span><span class="invisible"></span></a>',  # noqa: E501
                                "verified_at": None,
                            },
                        ],
                    },
                    "media_attachments": [],
                    "mentions": [
                        {
                            "id": 108215876835523723,
                            "username": "ewbot",
                            "url": "https://botsin.space/@ewbot",
                            "acct": "ewbot",
                        }
                    ],
                    "tags": [],
                    "emojis": [],
                    "card": None,
                    "poll": None,
                },
            )
            m.get(
                "https://quoteservice.andrlik.org/api/groups/ew/get_random_quote/",
                json={
                    "quote": "We always go right.",
                    "quote_rendered": "<p>We always go right.</p>",
                    "citation": "Episode 3",
                    "citation_url": "https://www.explorerswanted.fm/3",
                    "source": {
                        "name": "Nix",
                        "slug": "ew-nix",
                        "description": "Glaive",
                        "description_rendered": "<p>Glaive</p>",
                    },
                },
            )
            m.get(
                "https://quoteservice.andrlik.org/api/sources/",
                json=[{"name": "Nix", "slug": "ew-nix"}],
            )
            m.get(
                "https://quoteservice.andrlik.org/api/sources/ew-nix/generate_sentence/",
                json={"sentence": "fear the snek"},
            )
            respond_to_toots("test_last_toot.txt")
            assert get_last_toot_id("test_last_toot.txt") == 4772149
