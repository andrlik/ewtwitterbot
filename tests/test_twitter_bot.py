import os
from unittest import mock

import pytest
import requests_mock

from ewtwitterbot.imagery import get_quote_image
from ewtwitterbot.twitter_bot import (
    TwitterImproperlyConfigured,
    get_credentials_from_environ,
    get_last_tweet_id,
    respond_to_tweets,
    save_last_tweet_id,
    upload_image_and_set_metadata,
)


@pytest.fixture
def save_a_tweet_id():
    with open("test_last_tweet.txt", "w") as f:
        f.write(str(14))


def test_retrieve_last_id_saved(save_a_tweet_id):
    assert get_last_tweet_id("test_last_tweet.txt") == 14


def test_save_tweet_id():
    if os.path.exists("test_last_tweet.txt"):
        os.remove("test_last_tweet.txt")
    save_last_tweet_id("test_last_tweet.txt", 40)
    assert os.path.exists("test_last_tweet.txt")
    assert get_last_tweet_id("test_last_tweet.txt") == 40


def test_retrieve_nonexistent_tweet_id():
    if os.path.exists("test_last_tweet.txt"):
        os.remove("test_last_tweet.txt")
    assert get_last_tweet_id("test_last_tweet.txt") == 1


def test_configuration_checks():
    names_to_remove = [
        "TWITTER_CONSUMER_KEY",
        "TWITTER_CONSUMER_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET",
    ]
    modified_environ = {k: v for k, v in os.environ.items() if k not in names_to_remove}
    with mock.patch.dict(os.environ, modified_environ, clear=True):
        with pytest.raises(TwitterImproperlyConfigured):
            get_credentials_from_environ()


@pytest.fixture
def twitter_environ_patch():
    return {
        "TWITTER_CONSUMER_KEY": "jdflkjsdfjdldfj",
        "TWITTER_CONSUMER_SECRET": "kdjsfdlkjldsjldks",
        "TWITTER_ACCESS_TOKEN": "jdjoidjfdijfjw",
        "TWITTER_ACCESS_TOKEN_SECRET": "jfeheheoiwifejofjewieojfwfjdo",
    }


def test_media_upload_success(twitter_environ_patch):
    with mock.patch.dict(os.environ, twitter_environ_patch, clear=False):
        with requests_mock.Mocker() as m:
            m.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                status_code=200,
                json={
                    "media_id": 710511363345354753,
                    "media_id_string": "710511363345354753",
                    "media_key": "3_710511363345354753",
                    "size": 11065,
                    "expires_after_secs": 86400,
                    "image": {"image_type": "image/jpeg", "w": 800, "h": 320},
                },
            )
            m.post(
                "https://upload.twitter.com/1.1/media/metadata/create.json",
                status_code=200,
            )
            get_quote_image("Hi there")
            assert (
                upload_image_and_set_metadata(
                    get_credentials_from_environ(),
                    "quote_image.png",
                    alt_text="Hi there",
                )
                == 710511363345354753
            )


def test_twitter_mention_cycle(twitter_environ_patch):
    with mock.patch.dict(os.environ, twitter_environ_patch, clear=False):
        with requests_mock.Mocker() as m:
            m.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                status_code=200,
                json={
                    "media_id": 710511363345354753,
                    "media_id_string": "710511363345354753",
                    "media_key": "3_710511363345354753",
                    "size": 11065,
                    "expires_after_secs": 86400,
                    "image": {"image_type": "image/jpeg", "w": 800, "h": 320},
                },
            )
            m.post(
                "https://upload.twitter.com/1.1/media/metadata/create.json",
                status_code=200,
            )
            m.get(
                "https://api.twitter.com/1.1/statuses/mentions_timeline.json",
                status_code=200,
                json=[
                    {
                        "coordinates": None,
                        "favorited": False,
                        "truncated": False,
                        "created_at": "Mon Sep 03 13:24:14 +0000 2012",
                        "id_str": "242613977966850048",
                        "entities": {
                            "urls": [],
                            "hashtags": [],
                            "user_mentions": [
                                {
                                    "name": "Jason Costa",
                                    "id_str": "14927800",
                                    "id": 14927800,
                                    "indices": [0, 11],
                                    "screen_name": "jasoncosta",
                                },
                                {
                                    "name": "Matt Harris",
                                    "id_str": "777925",
                                    "id": 777925,
                                    "indices": [12, 26],
                                    "screen_name": "themattharris",
                                },
                                {
                                    "name": "ThinkWall",
                                    "id_str": "117426578",
                                    "id": 117426578,
                                    "indices": [109, 119],
                                    "screen_name": "thinkwall",
                                },
                            ],
                        },
                        "in_reply_to_user_id_str": "14927800",
                        "contributors": None,
                        "full_text": "@somebot markov",
                        "retweet_count": 0,
                        "in_reply_to_status_id_str": None,
                        "id": 242613977966850048,
                        "geo": None,
                        "retweeted": False,
                        "in_reply_to_user_id": 14927800,
                        "place": None,
                        "user": {
                            "profile_sidebar_fill_color": "EEEEEE",
                            "profile_sidebar_border_color": "000000",
                            "profile_background_tile": False,
                            "name": "Andrew Spode Miller",
                            "profile_image_url": "http://a0.twimg.com/profile_images/1227466231/spode-balloon-medium_normal.jpg",  # noqa: E501
                            "created_at": "Mon Sep 22 13:12:01 +0000 2008",
                            "location": "London via Gravesend",
                            "follow_request_sent": False,
                            "profile_link_color": "F31B52",
                            "is_translator": False,
                            "id_str": "16402947",
                            "entities": {
                                "url": {
                                    "urls": [
                                        {
                                            "expanded_url": None,
                                            "url": "http://www.linkedin.com/in/spode",
                                            "indices": [0, 32],
                                        }
                                    ]
                                },
                                "description": {"urls": []},
                            },
                            "default_profile": False,
                            "contributors_enabled": False,
                            "favourites_count": 16,
                            "url": "http://www.linkedin.com/in/spode",
                            "profile_image_url_https": "https://si0.twimg.com/profile_images/1227466231/spode-balloon-medium_normal.jpg",  # noqa: E501
                            "utc_offset": 0,
                            "id": 16402947,
                            "profile_use_background_image": False,
                            "listed_count": 129,
                            "profile_text_color": "262626",
                            "lang": "en",
                            "followers_count": 2013,
                            "protected": False,
                            "notifications": None,
                            "profile_background_image_url_https": "https://si0.twimg.com/profile_background_images/16420220/twitter-background-final.png",  # noqa: E501
                            "profile_background_color": "FFFFFF",
                            "verified": None,
                            "geo_enabled": True,
                            "time_zone": "London",
                            "description": "Co-Founder/Dev (PHP/jQuery) @justFDI. Run @thinkbikes and @thinkwall for events. Ex tech journo, helps run @uktjpr. Passion for Linux and customises everything.",  # noqa: E501
                            "default_profile_image": False,
                            "profile_background_image_url": "http://a0.twimg.com/profile_background_images/16420220/twitter-background-final.png",  # noqa: E501
                            "statuses_count": 11550,
                            "friends_count": 770,
                            "following": None,
                            "show_all_inline_media": True,
                            "screen_name": "spode",
                        },
                        "in_reply_to_screen_name": "jasoncosta",
                        "source": "JournoTwit",
                        "in_reply_to_status_id": None,
                    },
                    {
                        "coordinates": {
                            "coordinates": [121.0132101, 14.5191613],
                            "type": "Point",
                        },
                        "favorited": False,
                        "truncated": False,
                        "created_at": "Mon Sep 03 08:08:02 +0000 2012",
                        "id_str": "242534402280783873",
                        "entities": {
                            "urls": [],
                            "hashtags": [{"text": "twitter", "indices": [49, 57]}],
                            "user_mentions": [
                                {
                                    "name": "Jason Costa",
                                    "id_str": "14927800",
                                    "id": 14927800,
                                    "indices": [14, 25],
                                    "screen_name": "jasoncosta",
                                }
                            ],
                        },
                        "in_reply_to_user_id_str": None,
                        "contributors": None,
                        "full_text": "@somebot quote",
                        "retweet_count": 0,
                        "in_reply_to_status_id_str": None,
                        "id": 242534402280783873,
                        "geo": {
                            "coordinates": [14.5191613, 121.0132101],
                            "type": "Point",
                        },
                        "retweeted": False,
                        "in_reply_to_user_id": None,
                        "place": None,
                        "user": {
                            "profile_sidebar_fill_color": "EFEFEF",
                            "profile_sidebar_border_color": "EEEEEE",
                            "profile_background_tile": True,
                            "name": "Mikey",
                            "profile_image_url": "http://a0.twimg.com/profile_images/1305509670/chatMikeTwitter_normal.png",  # noqa: E501
                            "created_at": "Fri Jun 20 15:57:08 +0000 2008",
                            "location": "Singapore",
                            "follow_request_sent": False,
                            "profile_link_color": "009999",
                            "is_translator": False,
                            "id_str": "15181205",
                            "entities": {
                                "url": {
                                    "urls": [
                                        {
                                            "expanded_url": None,
                                            "url": "http://about.me/michaelangelo",
                                            "indices": [0, 29],
                                        }
                                    ]
                                },
                                "description": {"urls": []},
                            },
                            "default_profile": False,
                            "contributors_enabled": False,
                            "favourites_count": 11,
                            "url": "http://about.me/michaelangelo",
                            "profile_image_url_https": "https://si0.twimg.com/profile_images/1305509670/chatMikeTwitter_normal.png",  # noqa: E501
                            "utc_offset": 28800,
                            "id": 15181205,
                            "profile_use_background_image": True,
                            "listed_count": 61,
                            "profile_text_color": "333333",
                            "lang": "en",
                            "followers_count": 577,
                            "protected": False,
                            "notifications": None,
                            "profile_background_image_url_https": "https://si0.twimg.com/images/themes/theme14/bg.gif",
                            "profile_background_color": "131516",
                            "verified": False,
                            "geo_enabled": False,
                            "time_zone": "Hong Kong",
                            "description": "Android Applications Developer,  Studying Martial Arts, Plays MTG, Food and movie junkie",  # noqa: E501
                            "default_profile_image": False,
                            "profile_background_image_url": "http://a0.twimg.com/images/themes/theme14/bg.gif",
                            "statuses_count": 11327,
                            "friends_count": 138,
                            "following": None,
                            "show_all_inline_media": True,
                            "screen_name": "mikedroid",
                        },
                        "in_reply_to_screen_name": None,
                        "source": "Twitter for Android",
                        "in_reply_to_status_id": None,
                    },
                ],
            )
            # TODO: Add tweet reply mock here so that test can be wrapped up.
            m.post(
                "https://api.twitter.com/1.1/statuses/update.json",
                status_code=200,
                json={
                    "created_at": "Wed Oct 10 20:19:24 +0000 2018",
                    "id": 1050118621198921700,
                    "id_str": "1050118621198921728",
                    "text": "To make room for more expression, we will now count all emojis as equal???including those with gender????????? ??????and skin t??? https://t.co/MkGjXf9aXm",  # noqa: E501
                    "source": '<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>',
                    "truncated": True,
                    "in_reply_to_status_id": None,
                    "in_reply_to_status_id_str": None,
                    "in_reply_to_user_id": None,
                    "in_reply_to_user_id_str": None,
                    "in_reply_to_screen_name": None,
                    "user": {
                        "id": 6253282,
                        "id_str": "6253282",
                        "name": "Twitter API",
                        "screen_name": "TwitterAPI",
                        "location": "San Francisco, CA",
                        "url": "https://developer.twitter.com",
                        "description": "The Real Twitter API. Tweets about API changes, service issues and our Developer Platform. Don't get an answer? It's on my website.",  # noqa: E501
                        "translator_type": "null",
                        "derived": {
                            "locations": [
                                {
                                    "country": "United States",
                                    "country_code": "US",
                                    "locality": "San Francisco",
                                    "region": "California",
                                    "sub_region": "San Francisco County",
                                    "full_name": "San Francisco, California, United States",
                                    "geo": {
                                        "coordinates": [-122.41942, 37.77493],
                                        "type": "point",
                                    },
                                }
                            ]
                        },
                        "protected": False,
                        "verified": True,
                        "followers_count": 6172196,
                        "friends_count": 12,
                        "listed_count": 13003,
                        "favourites_count": 31,
                        "statuses_count": 3650,
                        "created_at": "Wed May 23 06:01:13 +0000 2007",
                        "utc_offset": None,
                        "time_zone": None,
                        "geo_enabled": False,
                        "lang": "en",
                        "contributors_enabled": False,
                        "is_translator": None,
                        "profile_background_color": "null",
                        "profile_background_image_url": "null",
                        "profile_background_image_url_https": "null",
                        "profile_background_tile": None,
                        "profile_link_color": "null",
                        "profile_sidebar_border_color": "null",
                        "profile_sidebar_fill_color": "null",
                        "profile_text_color": "null",
                        "profile_use_background_image": None,
                        "profile_image_url": "null",
                        "profile_image_url_https": "https://pbs.twimg.com/profile_images/942858479592554497/BbazLO9L_normal.jpg",  # noqa: E501
                        "profile_banner_url": "https://pbs.twimg.com/profile_banners/6253282/1497491515",
                        "default_profile": False,
                        "default_profile_image": False,
                        "following": None,
                        "follow_request_sent": None,
                        "notifications": None,
                    },
                    "geo": None,
                    "coordinates": None,
                    "place": None,
                    "contributors": None,
                    "is_quote_status": False,
                    "extended_tweet": {
                        "full_text": "To make room for more expression, we will now count all emojis as equal???including those with gender????????? ??????and skin tone modifiers ????????????????????????. This is now reflected in Twitter-Text, our Open Source library. nnUsing Twitter-Text? See the forum post for detail: https://t.co/Nx1XZmRCXA",  # noqa: E501
                        "display_text_range": [0, 277],
                        "entities": {
                            "hashtags": [],
                            "urls": [
                                {
                                    "url": "https://t.co/Nx1XZmRCXA",
                                    "expanded_url": "https://twittercommunity.com/t/new-update-to-the-twitter-text-library-emoji-character-count/114607",  # noqa: E501
                                    "display_url": "twittercommunity.com/t/new-update-t???",
                                    "unwound": {
                                        "url": "https://twittercommunity.com/t/new-update-to-the-twitter-text-library-emoji-character-count/114607",  # noqa: E501
                                        "status": 200,
                                        "title": "New update to the Twitter-Text library: Emoji character count",
                                        "description": "Over the years, we have made several updates to the way that people can communicate on Twitter. One of the more notable changes made last year was to increase the number of characters per Tweet from 140 to 280 characters. Today, we continue to expand people???s ability to express themselves by announcing a change to the way that we count emojis. Due to the differences in the way written text and emojis are encoded, many emojis (including emojis where you can apply gender and skin tone) have count...",  # noqa: E501
                                    },
                                    "indices": [254, 277],
                                }
                            ],
                            "user_mentions": [],
                            "symbols": [],
                        },
                    },
                    "quote_count": 0,
                    "reply_count": 0,
                    "retweet_count": 0,
                    "favorite_count": 0,
                    "entities": {
                        "hashtags": [],
                        "urls": [
                            {
                                "url": "https://t.co/MkGjXf9aXm",
                                "expanded_url": "https://twitter.com/i/web/status/1050118621198921728",
                                "display_url": "twitter.com/i/web/status/1???",
                                "indices": [117, 140],
                            }
                        ],
                        "user_mentions": [],
                        "symbols": [],
                    },
                    "favorited": False,
                    "retweeted": False,
                    "possibly_sensitive": False,
                    "filter_level": "low",
                    "lang": "en",
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
            respond_to_tweets("test_last_tweet.txt")
            assert get_last_tweet_id("test_last_tweet.txt") == 242613977966850048
