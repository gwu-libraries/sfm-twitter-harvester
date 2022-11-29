#!/usr/bin/env python
# -*- coding: utf-8 -*-
import copy

def join_tweets(*tweets):
    res = {}
    for tweet in tweets:
        for k in ('data', 'errors', 'includes', 'meta'):
            if k not in tweet:
                continue
            c = copy.deepcopy(tweet[k])
            if k not in res:
                res[k] = c
            elif k == 'meta':
                pass
            elif k == 'includes':
                for kk in c:
                    if kk not in res['includes']:
                        res[k][kk] = c[kk]
                    else:
                        for i in c[kk]:
                            res[k][kk].append(i)
            else:
                for i in c:
                    res[k].append(i)
    return res

tweet1 = {
    "created_at": "Tue Jun 02 13:22:55 +0000 2015",
    "id": 605726286741434400,
    "id_str": "605726286741434368",
    "text": "At LC for @archemail today:  Thinking about overlap between email archiving, web archiving, and social media archiving.",
    "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
    "truncated": False,
    "in_reply_to_status_id": None,
    "in_reply_to_status_id_str": None,
    "in_reply_to_user_id": None,
    "in_reply_to_user_id_str": None,
    "in_reply_to_screen_name": None,
    "user": {
        "id": 481186914,
        "id_str": "481186914",
        "name": "Justin Littman",
        "screen_name": "justin_littman",
        "location": "",
        "description": "",
        "url": None,
        "entities": {
            "description": {
                "urls": []
            }
        },
        "protected": False,
        "followers_count": 45,
        "friends_count": 47,
        "listed_count": 5,
        "created_at": "Thu Feb 02 12:19:18 +0000 2012",
        "favourites_count": 34,
        "utc_offset": -14400,
        "time_zone": "Eastern Time (US & Canada)",
        "geo_enabled": True,
        "verified": False,
        "statuses_count": 72,
        "lang": "en",
        "contributors_enabled": False,
        "is_translator": False,
        "is_translation_enabled": False,
        "profile_background_color": "C0DEED",
        "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
        "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
        "profile_background_tile": False,
        "profile_image_url": "http://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
        "profile_image_url_https": "https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
        "profile_link_color": "0084B4",
        "profile_sidebar_border_color": "C0DEED",
        "profile_sidebar_fill_color": "DDEEF6",
        "profile_text_color": "333333",
        "profile_use_background_image": True,
        "has_extended_profile": False,
        "default_profile": True,
        "default_profile_image": False,
        "following": False,
        "follow_request_sent": False,
        "notifications": False
    },
    "geo": None,
    "coordinates": None,
    "place": {
        "id": "01fbe706f872cb32",
        "url": "https://api.twitter.com/1.1/geo/id/01fbe706f872cb32.json",
        "place_type": "city",
        "name": "Washington",
        "full_name": "Washington, DC",
        "country_code": "US",
        "country": "United States",
        "contained_within": [],
        "bounding_box": {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -77.119401,
                        38.801826
                    ],
                    [
                        -76.909396,
                        38.801826
                    ],
                    [
                        -76.909396,
                        38.9953797
                    ],
                    [
                        -77.119401,
                        38.9953797
                    ]
                ]
            ]
        },
        "attributes": {}
    },
    "contributors": None,
    "is_quote_status": False,
    "retweet_count": 0,
    "favorite_count": 0,
    "entities": {
        "hashtags": [],
        "symbols": [],
        "user_mentions": [],
        "urls": []
    },
    "favorited": False,
    "retweeted": False,
    "lang": "en"
}

# tweet2 has a url
tweet2 = {
    "created_at": "Fri Oct 30 12:06:15 +0000 2015",
    "id": 660065173563158500,
    "id_str": "660065173563158529",
    "text": "My new blog post on techniques for harvesting social media to WARCs: https://t.co/OHZki6pXEe",
    "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
    "truncated": False,
    "in_reply_to_status_id": None,
    "in_reply_to_status_id_str": None,
    "in_reply_to_user_id": None,
    "in_reply_to_user_id_str": None,
    "in_reply_to_screen_name": None,
    "user": {
        "id": 481186914,
        "id_str": "481186914",
        "name": "Justin Littman",
        "screen_name": "justin_littman",
        "location": "",
        "description": "",
        "url": None,
        "entities": {
            "description": {
                "urls": []
            }
        },
        "protected": False,
        "followers_count": 52,
        "friends_count": 50,
        "listed_count": 5,
        "created_at": "Thu Feb 02 12:19:18 +0000 2012",
        "favourites_count": 50,
        "utc_offset": -18000,
        "time_zone": "Eastern Time (US & Canada)",
        "geo_enabled": True,
        "verified": False,
        "statuses_count": 85,
        "lang": "en",
        "contributors_enabled": False,
        "is_translator": False,
        "is_translation_enabled": False,
        "profile_background_color": "C0DEED",
        "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
        "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
        "profile_background_tile": False,
        "profile_image_url": "http://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
        "profile_image_url_https": "https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
        "profile_link_color": "0084B4",
        "profile_sidebar_border_color": "C0DEED",
        "profile_sidebar_fill_color": "DDEEF6",
        "profile_text_color": "333333",
        "profile_use_background_image": True,
        "has_extended_profile": False,
        "default_profile": True,
        "default_profile_image": False,
        "following": False,
        "follow_request_sent": False,
        "notifications": False
    },
    "geo": None,
    "coordinates": None,
    "place": None,
    "contributors": None,
    "is_quote_status": False,
    "retweet_count": 10,
    "favorite_count": 9,
    "entities": {
        "hashtags": [],
        "symbols": [],
        "user_mentions": [],
        "urls": [
            {
                "url": "https://t.co/OHZki6pXEe",
                "expanded_url": "http://bit.ly/1ipwd0B",
                "display_url": "bit.ly/1ipwd0B",
                "indices": [
                    69,
                    92
                ]
            }
        ]
    },
    "favorited": False,
    "retweeted": False,
    "possibly_sensitive": False,
    "possibly_sensitive_appealable": False,
    "lang": "en"
}

# tweet3 has an extended entity.
tweet3 = {
    "contributors": None,
    "truncated": False,
    "text": "Test tweet 9. Tweet with a GIF. https://t.co/x6AYFg3REg",
    "is_quote_status": False,
    "in_reply_to_status_id": None,
    "id": 727894186415013888,
    "favorite_count": 0,
    "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
    "retweeted": False,
    "coordinates": None,
    "entities": {
        "symbols": [],
        "user_mentions": [],
        "hashtags": [],
        "urls": [],
        "media": [{
            "expanded_url": "http://twitter.com/jlittman_dev/status/727894186415013888/photo/1",
            "display_url": "pic.twitter.com/x6AYFg3REg",
            "url": "https://t.co/x6AYFg3REg",
            "media_url_https": "https://pbs.twimg.com/tweet_video_thumb/Chn_42fWwAASuva.jpg",
            "id_str": "727894166961831936",
            "sizes": {
                "large": {
                    "h": 230,
                    "resize": "fit",
                    "w": 300
                },
                "small": {
                    "h": 230,
                    "resize": "fit",
                    "w": 300
                },
                "medium": {
                    "h": 230,
                    "resize": "fit",
                    "w": 300
                },
                "thumb": {
                    "h": 150,
                    "resize": "crop",
                    "w": 150
                }
            },
            "indices": [32, 55],
            "type": "photo",
            "id": 727894166961831936,
            "media_url": "http://pbs.twimg.com/tweet_video_thumb/Chn_42fWwAASuva.jpg"
        }]
    },
    "in_reply_to_screen_name": None,
    "in_reply_to_user_id": None,
    "retweet_count": 0,
    "id_str": "727894186415013888",
    "favorited": False,
    "user": {
        "follow_request_sent": False,
        "has_extended_profile": False,
        "profile_use_background_image": True,
        "default_profile_image": True,
        "id": 2875189485,
        "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
        "verified": False,
        "profile_text_color": "333333",
        "profile_image_url_https": "https://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
        "profile_sidebar_fill_color": "DDEEF6",
        "entities": {
            "description": {
                "urls": []
            }
        },
        "followers_count": 0,
        "profile_sidebar_border_color": "C0DEED",
        "id_str": "2875189485",
        "profile_background_color": "C0DEED",
        "listed_count": 0,
        "is_translation_enabled": False,
        "utc_offset": None,
        "statuses_count": 9,
        "description": "",
        "friends_count": 0,
        "location": "",
        "profile_link_color": "0084B4",
        "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
        "following": False,
        "geo_enabled": True,
        "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
        "screen_name": "jlittman_dev",
        "lang": "en",
        "profile_background_tile": False,
        "favourites_count": 0,
        "name": "Justin Littman dev",
        "notifications": False,
        "url": None,
        "created_at": "Thu Nov 13 15:49:55 +0000 2014",
        "contributors_enabled": False,
        "time_zone": None,
        "protected": False,
        "default_profile": True,
        "is_translator": False
    },
    "geo": None,
    "in_reply_to_user_id_str": None,
    "possibly_sensitive": False,
    "lang": "en",
    "created_at": "Wed May 04 16:14:32 +0000 2016",
    "in_reply_to_status_id_str": None,
    "place": None,
    "extended_entities": {
        "media": [{
            "expanded_url": "http://twitter.com/jlittman_dev/status/727894186415013888/photo/1",
            "display_url": "pic.twitter.com/x6AYFg3REg",
            "url": "https://t.co/x6AYFg3REg",
            "media_url_https": "https://pbs.twimg.com/tweet_video_thumb/Chn_42fWwAASuva.jpg",
            "video_info": {
                "aspect_ratio": [30, 23],
                "variants": [{
                    "url": "https://pbs.twimg.com/tweet_video/Chn_42fWwAASuva.mp4",
                    "bitrate": 0,
                    "content_type": "video/mp4"
                }]
            },
            "id_str": "727894166961831936",
            "sizes": {
                "large": {
                    "h": 230,
                    "resize": "fit",
                    "w": 300
                },
                "small": {
                    "h": 230,
                    "resize": "fit",
                    "w": 300
                },
                "medium": {
                    "h": 230,
                    "resize": "fit",
                    "w": 300
                },
                "thumb": {
                    "h": 150,
                    "resize": "crop",
                    "w": 150
                }
            },
            "indices": [32, 55],
            "type": "animated_gif",
            "id": 727894166961831936,
            "media_url": "http://pbs.twimg.com/tweet_video_thumb/Chn_42fWwAASuva.jpg"
        }]
    }
}

# tweet4 has a quoted_status
tweet4 = {
    "contributors": None,
    "truncated": False,
    "text": "Test 10. Retweet. https://t.co/tBu6RRJoKr",
    "is_quote_status": True,
    "in_reply_to_status_id": None,
    "id": 727930772691292161,
    "favorite_count": 0,
    "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
    "quoted_status_id": 503873833213104128,
    "retweeted": False,
    "coordinates": None,
    "quoted_status": {
        "contributors": None,
        "truncated": False,
        "text": "First day at Gelman Library. First tweet. http://t.co/Gz5ybAD6os",
        "is_quote_status": False,
        "in_reply_to_status_id": None,
        "id": 503873833213104128,
        "favorite_count": 4,
        "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>",
        "retweeted": False,
        "coordinates": None,
        "entities": {
            "symbols": [],
            "user_mentions": [],
            "hashtags": [],
            "urls": [],
            "media": [{
                "expanded_url": "http://twitter.com/justin_littman/status/503873833213104128/photo/1",
                "display_url": "pic.twitter.com/Gz5ybAD6os",
                "url": "http://t.co/Gz5ybAD6os",
                "media_url_https": "https://pbs.twimg.com/media/Bv4ekbqIYAAcmXY.jpg",
                "id_str": "503873819560665088",
                "sizes": {
                    "large": {
                        "h": 576,
                        "resize": "fit",
                        "w": 1024
                    },
                    "small": {
                        "h": 191,
                        "resize": "fit",
                        "w": 340
                    },
                    "medium": {
                        "h": 338,
                        "resize": "fit",
                        "w": 600
                    },
                    "thumb": {
                        "h": 150,
                        "resize": "crop",
                        "w": 150
                    }
                },
                "indices": [42, 64],
                "type": "photo",
                "id": 503873819560665088,
                "media_url": "http://pbs.twimg.com/media/Bv4ekbqIYAAcmXY.jpg"
            }]
        },
        "in_reply_to_screen_name": None,
        "in_reply_to_user_id": None,
        "retweet_count": 0,
        "id_str": "503873833213104128",
        "favorited": False,
        "user": {
            "follow_request_sent": False,
            "has_extended_profile": False,
            "profile_use_background_image": True,
            "default_profile_image": False,
            "id": 481186914,
            "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
            "verified": False,
            "profile_text_color": "333333",
            "profile_image_url_https": "https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
            "profile_sidebar_fill_color": "DDEEF6",
            "entities": {
                "description": {
                    "urls": []
                }
            },
            "followers_count": 113,
            "profile_sidebar_border_color": "C0DEED",
            "id_str": "481186914",
            "profile_background_color": "C0DEED",
            "listed_count": 9,
            "is_translation_enabled": False,
            "utc_offset": -14400,
            "statuses_count": 260,
            "description": "",
            "friends_count": 64,
            "location": "",
            "profile_link_color": "0084B4",
            "profile_image_url": "http://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
            "following": False,
            "geo_enabled": True,
            "profile_banner_url": "https://pbs.twimg.com/profile_banners/481186914/1460820528",
            "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
            "screen_name": "justin_littman",
            "lang": "en",
            "profile_background_tile": False,
            "favourites_count": 117,
            "name": "Justin Littman",
            "notifications": False,
            "url": None,
            "created_at": "Thu Feb 02 12:19:18 +0000 2012",
            "contributors_enabled": False,
            "time_zone": "Eastern Time (US & Canada)",
            "protected": False,
            "default_profile": True,
            "is_translator": False
        },
        "geo": None,
        "in_reply_to_user_id_str": None,
        "possibly_sensitive": False,
        "lang": "en",
        "created_at": "Mon Aug 25 11:57:38 +0000 2014",
        "in_reply_to_status_id_str": None,
        "place": None,
        "extended_entities": {
            "media": [{
                "expanded_url": "http://twitter.com/justin_littman/status/503873833213104128/photo/1",
                "display_url": "pic.twitter.com/Gz5ybAD6os",
                "url": "http://t.co/Gz5ybAD6os",
                "media_url_https": "https://pbs.twimg.com/media/Bv4ekbqIYAAcmXY.jpg",
                "id_str": "503873819560665088",
                "sizes": {
                    "large": {
                        "h": 576,
                        "resize": "fit",
                        "w": 1024
                    },
                    "small": {
                        "h": 191,
                        "resize": "fit",
                        "w": 340
                    },
                    "medium": {
                        "h": 338,
                        "resize": "fit",
                        "w": 600
                    },
                    "thumb": {
                        "h": 150,
                        "resize": "crop",
                        "w": 150
                    }
                },
                "indices": [42, 64],
                "type": "photo",
                "id": 503873819560665088,
                "media_url": "http://pbs.twimg.com/media/Bv4ekbqIYAAcmXY.jpg"
            }]
        }
    },
    "entities": {
        "symbols": [],
        "user_mentions": [],
        "hashtags": [],
        "urls": [{
            "url": "https://t.co/tBu6RRJoKr",
            "indices": [18, 41],
            "expanded_url": "https://twitter.com/justin_littman/status/503873833213104128",
            "display_url": "twitter.com/justin_littman\u2026"
        },
        {
            "url": "https://t.co/6zD9PKIhKP",
            "expanded_url": "http://bit.ly/1NoNeBF",
            "display_url": "bit.ly/1NoNeBF",
            "indices": [
                41,
                64
            ]
        }
        ]
    },
    "in_reply_to_screen_name": None,
    "in_reply_to_user_id": None,
    "retweet_count": 0,
    "id_str": "727930772691292161",
    "favorited": False,
    "user": {
        "follow_request_sent": False,
        "has_extended_profile": False,
        "profile_use_background_image": True,
        "default_profile_image": True,
        "id": 2875189485,
        "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
        "verified": False,
        "profile_text_color": "333333",
        "profile_image_url_https": "https://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
        "profile_sidebar_fill_color": "DDEEF6",
        "entities": {
            "description": {
                "urls": []
            }
        },
        "followers_count": 0,
        "profile_sidebar_border_color": "C0DEED",
        "id_str": "2875189485",
        "profile_background_color": "C0DEED",
        "listed_count": 0,
        "is_translation_enabled": False,
        "utc_offset": None,
        "statuses_count": 10,
        "description": "",
        "friends_count": 0,
        "location": "",
        "profile_link_color": "0084B4",
        "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
        "following": False,
        "geo_enabled": True,
        "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
        "screen_name": "jlittman_dev",
        "lang": "en",
        "profile_background_tile": False,
        "favourites_count": 0,
        "name": "Justin Littman dev",
        "notifications": False,
        "url": None,
        "created_at": "Thu Nov 13 15:49:55 +0000 2014",
        "contributors_enabled": False,
        "time_zone": None,
        "protected": False,
        "default_profile": True,
        "is_translator": False
    },
    "geo": None,
    "in_reply_to_user_id_str": None,
    "possibly_sensitive": False,
    "lang": "en",
    "created_at": "Wed May 04 18:39:55 +0000 2016",
    "quoted_status_id_str": "503873833213104128",
    "in_reply_to_status_id_str": None,
    "place": None
}

# tweet5 has a retweet_status
tweet5 = {
    "contributors": None,
    "truncated": False,
    "text": "RT @justin_littman: Ahh ... so in the context of web crawling, that's what a \"frontier\" means: https://t.co/6oDZe03LsV",
    "is_quote_status": False,
    "in_reply_to_status_id": None,
    "id": 727933040803057667,
    "favorite_count": 0,
    "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
    "retweeted": False,
    "coordinates": None,
    "entities": {
        "symbols": [],
        "user_mentions": [{
            "id": 481186914,
            "indices": [3, 18],
            "id_str": "481186914",
            "screen_name": "justin_littman",
            "name": "Justin Littman"
        }],
        "hashtags": [],
        "urls": [{
            "url": "https://t.co/6oDZe03LsV",
            "indices": [95, 118],
            "expanded_url": "http://nlp.stanford.edu/IR-book/html/htmledition/the-url-frontier-1.html",
            "display_url": "nlp.stanford.edu/IR-book/html/h\u2026"
        }]
    },
    "in_reply_to_screen_name": None,
    "in_reply_to_user_id": None,
    "retweet_count": 2,
    "id_str": "727933040803057667",
    "favorited": False,
    "retweeted_status": {
        "contributors": None,
        "truncated": False,
        "text": "Ahh ... so in the context of web crawling, that's what a \"frontier\" means: https://t.co/6oDZe03LsV",
        "is_quote_status": False,
        "in_reply_to_status_id": None,
        "id": 725271102444953601,
        "favorite_count": 2,
        "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
        "retweeted": False,
        "coordinates": None,
        "entities": {
            "symbols": [],
            "user_mentions": [],
            "hashtags": [],
            "urls": [{
                "url": "https://t.co/6oDZe03LsV",
                "indices": [75, 98],
                "expanded_url": "http://nlp.stanford.edu/IR-book/html/htmledition/the-url-frontier-1.html",
                "display_url": "nlp.stanford.edu/IR-book/html/h\u2026"
            }]
        },
        "in_reply_to_screen_name": None,
        "in_reply_to_user_id": None,
        "retweet_count": 2,
        "id_str": "725271102444953601",
        "favorited": False,
        "user": {
            "follow_request_sent": False,
            "has_extended_profile": False,
            "profile_use_background_image": True,
            "default_profile_image": False,
            "id": 481186914,
            "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
            "verified": False,
            "profile_text_color": "333333",
            "profile_image_url_https": "https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
            "profile_sidebar_fill_color": "DDEEF6",
            "entities": {
                "description": {
                    "urls": []
                }
            },
            "followers_count": 113,
            "profile_sidebar_border_color": "C0DEED",
            "id_str": "481186914",
            "profile_background_color": "C0DEED",
            "listed_count": 9,
            "is_translation_enabled": False,
            "utc_offset": -14400,
            "statuses_count": 260,
            "description": "",
            "friends_count": 64,
            "location": "",
            "profile_link_color": "0084B4",
            "profile_image_url": "http://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg",
            "following": False,
            "geo_enabled": True,
            "profile_banner_url": "https://pbs.twimg.com/profile_banners/481186914/1460820528",
            "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
            "screen_name": "justin_littman",
            "lang": "en",
            "profile_background_tile": False,
            "favourites_count": 117,
            "name": "Justin Littman",
            "notifications": False,
            "url": None,
            "created_at": "Thu Feb 02 12:19:18 +0000 2012",
            "contributors_enabled": False,
            "time_zone": "Eastern Time (US & Canada)",
            "protected": False,
            "default_profile": True,
            "is_translator": False
        },
        "geo": None,
        "in_reply_to_user_id_str": None,
        "possibly_sensitive": False,
        "lang": "en",
        "created_at": "Wed Apr 27 10:31:20 +0000 2016",
        "in_reply_to_status_id_str": None,
        "place": {
            "full_name": "Centreville, VA",
            "url": "https://api.twitter.com/1.1/geo/id/ffcc53c4a4e7a620.json",
            "country": "United States",
            "place_type": "city",
            "bounding_box": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-77.479597, 38.802143],
                        [-77.397429, 38.802143],
                        [-77.397429, 38.880183],
                        [-77.479597, 38.880183]
                    ]
                ]
            },
            "contained_within": [],
            "country_code": "US",
            "attributes": {},
            "id": "ffcc53c4a4e7a620",
            "name": "Centreville"
        }
    },
    "user": {
        "follow_request_sent": False,
        "has_extended_profile": False,
        "profile_use_background_image": True,
        "default_profile_image": True,
        "id": 2875189485,
        "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
        "verified": False,
        "profile_text_color": "333333",
        "profile_image_url_https": "https://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
        "profile_sidebar_fill_color": "DDEEF6",
        "entities": {
            "description": {
                "urls": []
            }
        },
        "followers_count": 0,
        "profile_sidebar_border_color": "C0DEED",
        "id_str": "2875189485",
        "profile_background_color": "C0DEED",
        "listed_count": 0,
        "is_translation_enabled": False,
        "utc_offset": None,
        "statuses_count": 11,
        "description": "",
        "friends_count": 0,
        "location": "",
        "profile_link_color": "0084B4",
        "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
        "following": False,
        "geo_enabled": True,
        "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
        "screen_name": "jlittman_dev",
        "lang": "en",
        "profile_background_tile": False,
        "favourites_count": 0,
        "name": "Justin Littman dev",
        "notifications": False,
        "url": None,
        "created_at": "Thu Nov 13 15:49:55 +0000 2014",
        "contributors_enabled": False,
        "time_zone": None,
        "protected": False,
        "default_profile": True,
        "is_translator": False
    },
    "geo": None,
    "in_reply_to_user_id_str": None,
    "possibly_sensitive": False,
    "lang": "en",
    "created_at": "Wed May 04 18:48:55 +0000 2016",
    "in_reply_to_status_id_str": None,
    "place": None
}

# tweet6 has an extended tweet (Stream API)
tweet6 = {
  "contributors": None,
  "truncated": True,
  "text": "@justin_littman Some of the changes went live. This is going to be an example for a blog post I'm writing that will… https://t.co/Hq4h61I3FX",
  "is_quote_status": False,
  "in_reply_to_status_id": 839526473534959600,
  "id": 847804888365117400,
  "favorite_count": 0,
  "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
  "retweeted": False,
  "coordinates": None,
  "timestamp_ms": "1490967411496",
  "entities": {
    "user_mentions": [
      {
        "id": 481186914,
        "indices": [
          0,
          15
        ],
        "id_str": "481186914",
        "screen_name": "justin_littman",
        "name": "Justin Littman"
      }
    ],
    "symbols": [],
    "hashtags": [],
    "urls": [
      {
        "url": "https://t.co/Hq4h61I3FX",
        "indices": [
          117,
          140
        ],
        "expanded_url": "https://twitter.com/i/web/status/847804888365117440",
        "display_url": "twitter.com/i/web/status/8…"
      }
    ]
  },
  "in_reply_to_screen_name": "justin_littman",
  "id_str": "847804888365117440",
  "display_text_range": [
    16,
    140
  ],
  "retweet_count": 0,
  "in_reply_to_user_id": 481186914,
  "favorited": False,
  "user": {
    "follow_request_sent": None,
    "profile_use_background_image": True,
    "default_profile_image": True,
    "id": 2875189485,
    "verified": False,
    "profile_image_url_https": "https://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
    "profile_sidebar_fill_color": "DDEEF6",
    "profile_text_color": "333333",
    "followers_count": 0,
    "profile_sidebar_border_color": "C0DEED",
    "id_str": "2875189485",
    "profile_background_color": "C0DEED",
    "listed_count": 3,
    "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
    "utc_offset": None,
    "statuses_count": 21,
    "description": None,
    "friends_count": 0,
    "location": None,
    "profile_link_color": "1DA1F2",
    "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
    "following": None,
    "geo_enabled": True,
    "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
    "name": "Justin Littman dev",
    "lang": "en",
    "profile_background_tile": False,
    "favourites_count": 0,
    "screen_name": "jlittman_dev",
    "notifications": None,
    "url": None,
    "created_at": "Thu Nov 13 15:49:55 +0000 2014",
    "contributors_enabled": False,
    "time_zone": None,
    "protected": False,
    "default_profile": True,
    "is_translator": False
  },
  "geo": None,
  "in_reply_to_user_id_str": "481186914",
  "possibly_sensitive": False,
  "lang": "en",
  "extended_tweet": {
    "display_text_range": [
      16,
      156
    ],
    "entities": {
      "user_mentions": [
        {
          "id": 481186914,
          "indices": [
            0,
            15
          ],
          "id_str": "481186914",
          "screen_name": "justin_littman",
          "name": "Justin Littman"
        }
      ],
      "symbols": [],
      "hashtags": [],
      "urls": [
        {
          "url": "https://t.co/MfQy5wTWBc",
          "indices": [
            133,
            156
          ],
          "expanded_url": "https://gwu-libraries.github.io/sfm-ui/posts/2017-03-31-extended-tweets",
          "display_url": "gwu-libraries.github.io/sfm-ui/posts/2…"
        }
      ]
    },
    "full_text": "@justin_littman Some of the changes went live. This is going to be an example for a blog post I'm writing that will be available at: https://t.co/MfQy5wTWBc"
  },
  "created_at": "Fri Mar 31 13:36:51 +0000 2017",
  "filter_level": "low",
  "in_reply_to_status_id_str": "839526473534959617",
  "place": None
}

# tweet 7 is an extended tweet from the REST API
tweet7 = {
  "contributors": None,
  "truncated": False,
  "is_quote_status": False,
  "in_reply_to_status_id": 839526473534959600,
  "id": 847804888365117400,
  "favorite_count": 0,
  "full_text": "@justin_littman Some of the changes went live. This is going to be an example for a blog post I'm writing that will be available at: https://t.co/MfQy5wTWBc",
  "source": "<a href=\"http://twitter.com\" rel=\"nofollow\">Twitter Web Client</a>",
  "retweeted": False,
  "coordinates": None,
  "entities": {
    "symbols": [],
    "user_mentions": [
      {
        "id": 481186914,
        "indices": [
          0,
          15
        ],
        "id_str": "481186914",
        "screen_name": "justin_littman",
        "name": "Justin Littman"
      }
    ],
    "hashtags": [],
    "urls": [
      {
        "url": "https://t.co/MfQy5wTWBc",
        "indices": [
          133,
          156
        ],
        "expanded_url": "https://gwu-libraries.github.io/sfm-ui/posts/2017-03-31-extended-tweets",
        "display_url": "gwu-libraries.github.io/sfm-ui/posts/2…"
      }
    ]
  },
  "in_reply_to_screen_name": "justin_littman",
  "in_reply_to_user_id": 481186914,
  "display_text_range": [
    16,
    156
  ],
  "retweet_count": 0,
  "id_str": "847804888365117440",
  "favorited": False,
  "user": {
    "follow_request_sent": False,
    "has_extended_profile": False,
    "profile_use_background_image": True,
    "default_profile_image": True,
    "id": 2875189485,
    "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme1/bg.png",
    "verified": False,
    "translator_type": "none",
    "profile_text_color": "333333",
    "profile_image_url_https": "https://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
    "profile_sidebar_fill_color": "DDEEF6",
    "entities": {
      "description": {
        "urls": []
      }
    },
    "followers_count": 0,
    "profile_sidebar_border_color": "C0DEED",
    "id_str": "2875189485",
    "profile_background_color": "C0DEED",
    "listed_count": 3,
    "is_translation_enabled": False,
    "utc_offset": None,
    "statuses_count": 21,
    "description": "",
    "friends_count": 0,
    "location": "",
    "profile_link_color": "1DA1F2",
    "profile_image_url": "http://abs.twimg.com/sticky/default_profile_images/default_profile_0_normal.png",
    "following": False,
    "geo_enabled": True,
    "profile_background_image_url": "http://abs.twimg.com/images/themes/theme1/bg.png",
    "screen_name": "jlittman_dev",
    "lang": "en",
    "profile_background_tile": False,
    "favourites_count": 0,
    "name": "Justin Littman dev",
    "notifications": False,
    "url": None,
    "created_at": "Thu Nov 13 15:49:55 +0000 2014",
    "contributors_enabled": False,
    "time_zone": None,
    "protected": False,
    "default_profile": True,
    "is_translator": False
  },
  "geo": None,
  "in_reply_to_user_id_str": "481186914",
  "possibly_sensitive": False,
  "lang": "en",
  "created_at": "Fri Mar 31 13:36:51 +0000 2017",
  "in_reply_to_status_id_str": "839526473534959617",
  "place": None
}

# tweet 8 is a quote tweet nested in a retweet
tweet8 = {
  "created_at": "Fri Oct 13 07:11:19 +0000 2017",
  "id": 918735887264972800,
  "id_str": "918735887264972800",
  "full_text": "RT @ClimateCentral: Wildfire season in the American West is now two and a half months longer than it was 40 years ago. Our wildfire report…",
  "truncated": False,
  "display_text_range": [
    0,
    139
  ],
  "entities": {
    "hashtags": [],
    "symbols": [],
    "user_mentions": [
      {
        "screen_name": "ClimateCentral",
        "name": "Climate Central",
        "id": 15463610,
        "id_str": "15463610",
        "indices": [
          3,
          18
        ]
      }
    ],
    "urls": []
  },
  "source": "<a href=\"http://twitter.com/download/iphone\" rel=\"nofollow\">Twitter for iPhone</a>",
  "in_reply_to_status_id": None,
  "in_reply_to_status_id_str": None,
  "in_reply_to_user_id": None,
  "in_reply_to_user_id_str": None,
  "in_reply_to_screen_name": None,
  "user": {
    "id": 1074184813,
    "id_str": "1074184813",
    "name": "DamonSmolderhalder😈",
    "screen_name": "DElenaTimeless",
    "location": "The Universe",
    "description": "#Damon #TVD #Delena #IanSomerhalder #NikkiReed #SOMEREED #Baby 👶🏻 #BeautifulHumans ❤️#ISF 🐶🐱 #KatGraham #Riverdale #Yoga 🙏🏼",
    "url": None,
    "entities": {
      "description": {
        "urls": []
      }
    },
    "protected": False,
    "followers_count": 1899,
    "friends_count": 906,
    "listed_count": 61,
    "created_at": "Wed Jan 09 16:04:14 +0000 2013",
    "favourites_count": 51301,
    "utc_offset": None,
    "time_zone": None,
    "geo_enabled": True,
    "verified": False,
    "statuses_count": 39703,
    "lang": "en",
    "contributors_enabled": False,
    "is_translator": False,
    "is_translation_enabled": False,
    "profile_background_color": "642D8B",
    "profile_background_image_url": "http://abs.twimg.com/images/themes/theme10/bg.gif",
    "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme10/bg.gif",
    "profile_background_tile": True,
    "profile_image_url": "http://pbs.twimg.com/profile_images/600743044535554048/DBgKQQMF_normal.jpg",
    "profile_image_url_https": "https://pbs.twimg.com/profile_images/600743044535554048/DBgKQQMF_normal.jpg",
    "profile_banner_url": "https://pbs.twimg.com/profile_banners/1074184813/1461658232",
    "profile_link_color": "FF0000",
    "profile_sidebar_border_color": "65B0DA",
    "profile_sidebar_fill_color": "7AC3EE",
    "profile_text_color": "3D1957",
    "profile_use_background_image": True,
    "has_extended_profile": True,
    "default_profile": False,
    "default_profile_image": False,
    "following": False,
    "follow_request_sent": False,
    "notifications": False,
    "translator_type": "none"
  },
  "geo": None,
  "coordinates": None,
  "place": None,
  "contributors": None,
  "retweeted_status": {
    "created_at": "Thu Oct 12 11:20:50 +0000 2017",
    "id": 918436293247406100,
    "id_str": "918436293247406080",
    "full_text": "Wildfire season in the American West is now two and a half months longer than it was 40 years ago. Our wildfire report in @YEARSofLIVING ⬇️ https://t.co/nk49r9sS1a",
    "truncated": False,
    "display_text_range": [
      0,
      139
    ],
    "entities": {
      "hashtags": [],
      "symbols": [],
      "user_mentions": [
        {
          "screen_name": "YEARSofLIVING",
          "name": "YEARS",
          "id": 308245641,
          "id_str": "308245641",
          "indices": [
            122,
            136
          ]
        }
      ],
      "urls": [
        {
          "url": "https://t.co/nk49r9sS1a",
          "expanded_url": "https://twitter.com/yearsofliving/status/878622618886094848",
          "display_url": "twitter.com/yearsofliving/…",
          "indices": [
            140,
            163
          ]
        }
      ]
    },
    "source": "<a href=\"http://twitter.com/download/iphone\" rel=\"nofollow\">Twitter for iPhone</a>",
    "in_reply_to_status_id": None,
    "in_reply_to_status_id_str": None,
    "in_reply_to_user_id": None,
    "in_reply_to_user_id_str": None,
    "in_reply_to_screen_name": None,
    "user": {
      "id": 15463610,
      "id_str": "15463610",
      "name": "Climate Central",
      "screen_name": "ClimateCentral",
      "location": "Princeton, NJ",
      "description": "Researching and reporting the science and impacts of climate change 🌎",
      "url": "https://t.co/sTxlhOkKr4",
      "entities": {
        "url": {
          "urls": [
            {
              "url": "https://t.co/sTxlhOkKr4",
              "expanded_url": "http://www.climatecentral.org",
              "display_url": "climatecentral.org",
              "indices": [
                0,
                23
              ]
            }
          ]
        },
        "description": {
          "urls": []
        }
      },
      "protected": False,
      "followers_count": 77475,
      "friends_count": 6206,
      "listed_count": 3050,
      "created_at": "Thu Jul 17 03:30:32 +0000 2008",
      "favourites_count": 30341,
      "utc_offset": -14400,
      "time_zone": "Eastern Time (US & Canada)",
      "geo_enabled": True,
      "verified": True,
      "statuses_count": 52858,
      "lang": "en",
      "contributors_enabled": False,
      "is_translator": False,
      "is_translation_enabled": False,
      "profile_background_color": "0A1241",
      "profile_background_image_url": "http://pbs.twimg.com/profile_background_images/677240012/4a1aac3ffc674aa0a080bcb176825eeb.jpeg",
      "profile_background_image_url_https": "https://pbs.twimg.com/profile_background_images/677240012/4a1aac3ffc674aa0a080bcb176825eeb.jpeg",
      "profile_background_tile": True,
      "profile_image_url": "http://pbs.twimg.com/profile_images/697146620543156225/R-VqX0vc_normal.png",
      "profile_image_url_https": "https://pbs.twimg.com/profile_images/697146620543156225/R-VqX0vc_normal.png",
      "profile_banner_url": "https://pbs.twimg.com/profile_banners/15463610/1503413844",
      "profile_link_color": "0079C2",
      "profile_sidebar_border_color": "000000",
      "profile_sidebar_fill_color": "E46F0A",
      "profile_text_color": "410936",
      "profile_use_background_image": True,
      "has_extended_profile": False,
      "default_profile": False,
      "default_profile_image": False,
      "following": False,
      "follow_request_sent": False,
      "notifications": False,
      "translator_type": "none"
    },
    "geo": None,
    "coordinates": None,
    "place": None,
    "contributors": None,
    "is_quote_status": True,
    "quoted_status_id": 878622618886094800,
    "quoted_status_id_str": "878622618886094848",
    "quoted_status": {
      "created_at": "Sat Jun 24 14:35:31 +0000 2017",
      "id": 878622618886094800,
      "id_str": "878622618886094848",
      "full_text": "Wildfire season in the American West is now two and a half months longer than it was 40 years ago.\n\n#YEARSproject #ClimateFacts https://t.co/AiA0mjoNXA",
      "truncated": False,
      "display_text_range": [
        0,
        127
      ],
      "entities": {
        "hashtags": [
          {
            "text": "YEARSproject",
            "indices": [
              100,
              113
            ]
          },
          {
            "text": "ClimateFacts",
            "indices": [
              114,
              127
            ]
          }
        ],
        "symbols": [],
        "user_mentions": [],
        "urls": [],
        "media": [
          {
            "id": 878622069532971000,
            "id_str": "878622069532971008",
            "indices": [
              128,
              151
            ],
            "media_url": "http://pbs.twimg.com/ext_tw_video_thumb/878622069532971008/pu/img/tv6rCbBH57EVbrU3.jpg",
            "media_url_https": "https://pbs.twimg.com/ext_tw_video_thumb/878622069532971008/pu/img/tv6rCbBH57EVbrU3.jpg",
            "url": "https://t.co/AiA0mjoNXA",
            "display_url": "pic.twitter.com/AiA0mjoNXA",
            "expanded_url": "https://twitter.com/YEARSofLIVING/status/878622618886094848/video/1",
            "type": "photo",
            "sizes": {
              "small": {
                "w": 340,
                "h": 340,
                "resize": "fit"
              },
              "thumb": {
                "w": 150,
                "h": 150,
                "resize": "crop"
              },
              "medium": {
                "w": 600,
                "h": 600,
                "resize": "fit"
              },
              "large": {
                "w": 720,
                "h": 720,
                "resize": "fit"
              }
            }
          }
        ]
      },
      "extended_entities": {
        "media": [
          {
            "id": 878622069532971000,
            "id_str": "878622069532971008",
            "indices": [
              128,
              151
            ],
            "media_url": "http://pbs.twimg.com/ext_tw_video_thumb/878622069532971008/pu/img/tv6rCbBH57EVbrU3.jpg",
            "media_url_https": "https://pbs.twimg.com/ext_tw_video_thumb/878622069532971008/pu/img/tv6rCbBH57EVbrU3.jpg",
            "url": "https://t.co/AiA0mjoNXA",
            "display_url": "pic.twitter.com/AiA0mjoNXA",
            "expanded_url": "https://twitter.com/YEARSofLIVING/status/878622618886094848/video/1",
            "type": "video",
            "sizes": {
              "small": {
                "w": 340,
                "h": 340,
                "resize": "fit"
              },
              "thumb": {
                "w": 150,
                "h": 150,
                "resize": "crop"
              },
              "medium": {
                "w": 600,
                "h": 600,
                "resize": "fit"
              },
              "large": {
                "w": 720,
                "h": 720,
                "resize": "fit"
              }
            },
            "video_info": {
              "aspect_ratio": [
                1,
                1
              ],
              "duration_millis": 52667,
              "variants": [
                {
                  "content_type": "application/x-mpegURL",
                  "url": "https://video.twimg.com/ext_tw_video/878622069532971008/pu/pl/SSDau35aVr1jWK77.m3u8"
                },
                {
                  "bitrate": 1280000,
                  "content_type": "video/mp4",
                  "url": "https://video.twimg.com/ext_tw_video/878622069532971008/pu/vid/720x720/Ev7hnJeFNOuwA-jt.mp4"
                },
                {
                  "bitrate": 832000,
                  "content_type": "video/mp4",
                  "url": "https://video.twimg.com/ext_tw_video/878622069532971008/pu/vid/480x480/vxwV65LvvxvuqoE0.mp4"
                },
                {
                  "bitrate": 320000,
                  "content_type": "video/mp4",
                  "url": "https://video.twimg.com/ext_tw_video/878622069532971008/pu/vid/240x240/R17LzSs4N5zqCTPG.mp4"
                }
              ]
            },
            "additional_media_info": {
              "monetizable": False
            }
          }
        ]
      },
      "source": "<a href=\"http://twitter.com/download/iphone\" rel=\"nofollow\">Twitter for iPhone</a>",
      "in_reply_to_status_id": None,
      "in_reply_to_status_id_str": None,
      "in_reply_to_user_id": None,
      "in_reply_to_user_id_str": None,
      "in_reply_to_screen_name": None,
      "user": {
        "id": 308245641,
        "id_str": "308245641",
        "name": "YEARS",
        "screen_name": "YEARSofLIVING",
        "location": "",
        "description": "YEARS of LIVING DANGEROUSLY docu-series on climate change. WATCH on demand on NatGeo, GooglePlay, iTunes, Amazon & DVD #YEARSproject",
        "url": "https://t.co/vKSslafi9r",
        "entities": {
          "url": {
            "urls": [
              {
                "url": "https://t.co/vKSslafi9r",
                "expanded_url": "http://yearsoflivingdangerously.com/",
                "display_url": "yearsoflivingdangerously.com",
                "indices": [
                  0,
                  23
                ]
              }
            ]
          },
          "description": {
            "urls": []
          }
        },
        "protected": False,
        "followers_count": 25538,
        "friends_count": 1087,
        "listed_count": 659,
        "created_at": "Tue May 31 02:29:26 +0000 2011",
        "favourites_count": 4561,
        "utc_offset": -14400,
        "time_zone": "Eastern Time (US & Canada)",
        "geo_enabled": False,
        "verified": False,
        "statuses_count": 17563,
        "lang": "en",
        "contributors_enabled": False,
        "is_translator": False,
        "is_translation_enabled": False,
        "profile_background_color": "131516",
        "profile_background_image_url": "http://pbs.twimg.com/profile_background_images/439137896788811777/tmrk6A-m.jpeg",
        "profile_background_image_url_https": "https://pbs.twimg.com/profile_background_images/439137896788811777/tmrk6A-m.jpeg",
        "profile_background_tile": True,
        "profile_image_url": "http://pbs.twimg.com/profile_images/787779443792019457/AffHFnwg_normal.jpg",
        "profile_image_url_https": "https://pbs.twimg.com/profile_images/787779443792019457/AffHFnwg_normal.jpg",
        "profile_banner_url": "https://pbs.twimg.com/profile_banners/308245641/1481820006",
        "profile_link_color": "859160",
        "profile_sidebar_border_color": "FFFFFF",
        "profile_sidebar_fill_color": "EFEFEF",
        "profile_text_color": "333333",
        "profile_use_background_image": False,
        "has_extended_profile": False,
        "default_profile": False,
        "default_profile_image": False,
        "following": False,
        "follow_request_sent": False,
        "notifications": False,
        "translator_type": "none"
      },
      "geo": None,
      "coordinates": None,
      "place": None,
      "contributors": None,
      "is_quote_status": False,
      "retweet_count": 80,
      "favorite_count": 47,
      "favorited": False,
      "retweeted": False,
      "possibly_sensitive": False,
      "lang": "en"
    },
    "retweet_count": 190,
    "favorite_count": 118,
    "favorited": False,
    "retweeted": False,
    "possibly_sensitive": False,
    "lang": "en"
  },
  "is_quote_status": True,
  "quoted_status_id": 878622618886094800,
  "quoted_status_id_str": "878622618886094848",
  "retweet_count": 190,
  "favorite_count": 0,
  "favorited": False,
  "retweeted": False,
  "lang": "en"
}

tweet1_2 = {
    'data': [
        {
            'lang': 'en',
            'created_at': '2015-06-02T13:22:55.000Z',
            'id': '605726286741434368',
            'source': 'Twitter Web Client',
            'author_id': '481186914',
            'reply_settings': 'everyone',
            'geo': {
                'place_id': '01fbe706f872cb32'
            },
            'text': 'At LC for @archemail today:  Thinking about overlap between email archiving, web archiving, and social media archiving.',
            'public_metrics': {
                'retweet_count': 0,
                'reply_count': 0,
                'like_count': 0,
                'quote_count': 0
            },
            'possibly_sensitive': False,
            'conversation_id': '605726286741434368'
        }
    ],
    'includes': {
        'users': [
            {
                'public_metrics': {
                    'followers_count': 796,
                    'following_count': 72,
                    'tweet_count': 2254,
                    'listed_count': 30
                },
                'entities': {
                    'description': {
                        'mentions': [
                            {
                                'start': 25,
                                'end': 36,
                                'username': 'DigitalLib'
                            },
                            {
                                'start': 49,
                                'end': 63,
                                'username': 'gelmanlibrary'
                            },
                            {
                                'start': 66,
                                'end': 82,
                                'username': 'librarycongress'
                            }
                        ]
                    }
                },
                'username': 'justin_littman',
                'name': 'Justin Littman',
                'id': '481186914',
                'verified': False,
                'location': 'Fairfax, VA',
                'url': '',
                'description': 'Software dev at Stanford @DigitalLib. Previously @gelmanlibrary & @librarycongress.',
                'protected': False,
                'profile_image_url': 'https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg',
                'created_at': '2012-02-02T12:19:18.000Z'
            }
        ],
        'places': [
            {
                'geo': {
                    'type': 'Feature',
                    'bbox': [-77.119401, 38.801826, -76.909396, 38.9953797],
                    'properties': {}
                },
                'name': 'Washington',
                'full_name': 'Washington, DC',
                'place_type': 'city',
                'id': '01fbe706f872cb32',
                'country_code': 'US',
                'country': 'United States'
            }
        ]
    }
}

# tweet2 has a url
tweet2_2 = {
    'data': [
        {
            'entities': {
                'urls': [
                    {
                        'start': 69,
                        'end': 92,
                        'url': 'https://t.co/OHZki6pXEe',
                        'expanded_url': 'http://bit.ly/1ipwd0B',
                        'display_url': 'bit.ly/1ipwd0B',
                        'status': 200,
                        'unwound_url': 'https://library.gwu.edu/collecting-social-media-data'
                    }
                ]
            },
            'reply_settings': 'everyone',
            'public_metrics': {
                'retweet_count': 9,
                'reply_count': 0,
                'like_count': 9,
                'quote_count': 0
            },
            'conversation_id': '660065173563158529',
            'source': 'Twitter Web Client',
            'author_id': '481186914',
            'possibly_sensitive': False,
            'created_at': '2015-10-30T12:06:15.000Z',
            'text': 'My new blog post on techniques for harvesting social media to WARCs: https://t.co/OHZki6pXEe',
            'lang': 'en',
            'id': '660065173563158529'
        }
    ],
    'includes': {
        'users': [
            {
                'location': 'Fairfax, VA',
                'url': '',
                'username': 'justin_littman',
                'entities': {
                    'description': {
                        'mentions': [
                            {
                                'start': 25,
                                'end': 36,
                                'username': 'DigitalLib'
                            },
                            {
                                'start': 49,
                                'end': 63,
                                'username': 'gelmanlibrary'
                            },
                            {
                                'start': 66,
                                'end': 82,
                                'username': 'librarycongress'
                            }
                        ]
                    }
                },
                'name': 'Justin Littman',
                'id': '481186914',
                'created_at': '2012-02-02T12:19:18.000Z',
                'verified': False,
                'description': 'Software dev at Stanford @DigitalLib. Previously @gelmanlibrary & @librarycongress.',
                'protected': False,
                'public_metrics': {
                    'followers_count': 796,
                    'following_count': 72,
                    'tweet_count': 2254,
                    'listed_count': 30
                },
                'profile_image_url': 'https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg'
            }
        ]
    }
}

# tweet3 has "attachments" (API v1: "extended_entities") 
tweet3_2 = {
    'data': [
        {
            'id': '727894186415013888',
            'lang': 'en',
            'attachments': {
                'media_keys': [
                    '16_727894166961831936']
            },
            'created_at': '2016-05-04T16:14:32.000Z',
            'source': 'Twitter Web Client',
            'author_id': '2875189485',
            'public_metrics': {
                'retweet_count': 0,
                'reply_count': 0,
                'like_count': 0,
                'quote_count': 0
            },
            'text': 'Test tweet 9. Tweet with a GIF. https://t.co/x6AYFg3REg',
            'reply_settings': 'everyone',
            'conversation_id': '727894186415013888',
            'possibly_sensitive': False,
            'entities': {
                'urls': [
                    {
                        'start': 32,
                        'end': 55,
                        'url': 'https://t.co/x6AYFg3REg',
                        'expanded_url': 'https://twitter.com/jlittman_dev/status/727894186415013888/photo/1',
                        'display_url': 'pic.twitter.com/x6AYFg3REg'
                    }
                ]
            }
        }
    ],
    'includes': {
        'media': [
            {
                'preview_image_url': 'https://pbs.twimg.com/tweet_video_thumb/Chn_42fWwAASuva.jpg',
                'media_key': '16_727894166961831936',
                'height': 230,
                'type': 'animated_gif',
                'width': 300
            }
        ],
        'users': [
            {
                'profile_image_url': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png',
                'verified': False,
                'id': '2875189485',
                'name': 'Justin Littman dev',
                'url': '',
                'description': '',
                'public_metrics': {
                    'followers_count': 0,
                    'following_count': 0,
                    'tweet_count': 29,
                    'listed_count': 2
                },
                'protected': False,
                'username': 'jlittman_dev',
                'created_at': '2014-11-13T15:49:55.000Z'
            }
        ]
    }
}

# tweet4 has "referenced_tweets" (API v1: "quoted_status")
tweet4_2 = {
    'data': [
        {
            'entities': {
                'urls': [
                    {
                        'start': 18,
                        'end': 41,
                        'url': 'https://t.co/tBu6RRJoKr',
                        'expanded_url': 'https://twitter.com/justin_littman/status/503873833213104128',
                        'display_url': 'twitter.com/justin_littman…'
                    }
                ]
            },
            'lang': 'en',
            'created_at': '2016-05-04T18:39:55.000Z',
            'referenced_tweets': [
                {
                    'type': 'quoted',
                    'id': '503873833213104128'
                }
            ],
            'id': '727930772691292161',
            'source': 'Twitter Web Client',
            'author_id': '2875189485',
            'reply_settings': 'everyone',
            'text': 'Test 10. Retweet. https://t.co/tBu6RRJoKr',
            'public_metrics': {
                'retweet_count': 0,
                'reply_count': 0,
                'like_count': 0,
                'quote_count': 0
            },
            'possibly_sensitive': False,
            'conversation_id': '727930772691292161'
        }
    ],
    'includes': {
        'users': [
            {
                'public_metrics': {
                    'followers_count': 0,
                    'following_count': 0,
                    'tweet_count': 29,
                    'listed_count': 2
                },
                'username': 'jlittman_dev',
                'name': 'Justin Littman dev',
                'id': '2875189485',
                'verified': False,
                'url': '',
                'description': '',
                'protected': False,
                'profile_image_url': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png',
                'created_at': '2014-11-13T15:49:55.000Z'
            },
            {
                'public_metrics': {
                    'followers_count': 796,
                    'following_count': 72,
                    'tweet_count': 2254,
                    'listed_count': 30
                },
                'entities': {
                    'description': {
                        'mentions': [
                            {
                                'start': 25,
                                'end': 36,
                                'username': 'DigitalLib'
                            },
                            {
                                'start': 49,
                                'end': 63,
                                'username': 'gelmanlibrary'
                            },
                            {
                                'start': 66,
                                'end': 82,
                                'username': 'librarycongress'
                            }
                        ]
                    }
                },
                'username': 'justin_littman',
                'name': 'Justin Littman',
                'id': '481186914',
                'verified': False,
                'location': 'Fairfax, VA',
                'url': '',
                'description': 'Software dev at Stanford @DigitalLib. Previously @gelmanlibrary & @librarycongress.',
                'protected': False,
                'profile_image_url': 'https://pbs.twimg.com/profile_images/496478011533713408/GjecBUNj_normal.jpeg',
                'created_at': '2012-02-02T12:19:18.000Z'
            }
        ],
        'tweets': [
            {
                'entities': {
                    'urls': [
                        {
                            'start': 42,
                            'end': 64,
                            'url': 'http://t.co/Gz5ybAD6os',
                            'expanded_url': 'https://twitter.com/justin_littman/status/503873833213104128/photo/1',
                            'display_url': 'pic.twitter.com/Gz5ybAD6os'
                        }
                    ],
                    'annotations': [
                        {
                            'start': 13,
                            'end': 26,
                            'probability': 0.7965,
                            'type': 'Place',
                            'normalized_text': 'Gelman Library'
                        }
                    ]
                },
                'lang': 'en',
                'created_at': '2014-08-25T11:57:38.000Z',
                'id': '503873833213104128',
                'source': 'Twitter for Android',
                'author_id': '481186914',
                'reply_settings': 'everyone',
                'attachments': {
                    'media_keys': [
                        '3_503873819560665088']
                },
                'text': 'First day at Gelman Library. First tweet. http://t.co/Gz5ybAD6os',
                'public_metrics': {
                    'retweet_count': 0,
                    'reply_count': 4,
                    'like_count': 6,
                    'quote_count': 0
                },
                'possibly_sensitive': False,
                'conversation_id': '503873833213104128'
            }
        ]
    }
}

# tweet 8 is a quote tweet nested in a retweet
tweet8_2 = {
    'data': [
        {
            'reply_settings': 'everyone',
            'referenced_tweets': [
                {
                    'type': 'retweeted',
                    'id': '918436293247406080'
                }
            ],
            'text': 'RT @ClimateCentral: Wildfire season in the American West is now two and a half months longer than it was 40 years ago. Our wildfire report…',
            'id': '918735887264972800',
            'entities': {
                'annotations': [
                    {
                        'start': 43,
                        'end': 55,
                        'probability': 0.4504,
                        'type': 'Place',
                        'normalized_text': 'American West'
                    }
                ],
                'mentions': [
                    {
                        'start': 3,
                        'end': 18,
                        'username': 'ClimateCentral',
                        'id': '15463610'
                    }
                ]
            },
            'possibly_sensitive': False,
            'conversation_id': '918735887264972800',
            'public_metrics': {
                'retweet_count': 168,
                'reply_count': 0,
                'like_count': 0,
                'quote_count': 0
            },
            'lang': 'en',
            'author_id': '1074184813',
            'source': 'Twitter for iPhone',
            'created_at': '2017-10-13T07:11:19.000Z'
        }
    ],
    'includes': {
        'users': [
            {
                'description': '#VWars 🧛🏻\u200d♂️#LutherSwann #Damon #TVD #Delena #IanSomerhalder #NikkiReed #SOMEREED #Bodhi👶🏻 ❤️#ISF 🐶🐱#Yoga🧘🏻\u200d♀️#BeautifulHumans #HarryPotter🦉⚡️🏆',
                'name': 'DamonSmolderhalder😈',
                'entities': {
                    'description': {
                        'hashtags': [
                            {
                                'start': 0,
                                'end': 6,
                                'tag': 'VWars'
                            },
                            {
                                'start': 12,
                                'end': 24,
                                'tag': 'LutherSwann'
                            },
                            {
                                'start': 25,
                                'end': 31,
                                'tag': 'Damon'
                            },
                            {
                                'start': 32,
                                'end': 36,
                                'tag': 'TVD'
                            },
                            {
                                'start': 37,
                                'end': 44,
                                'tag': 'Delena'
                            },
                            {
                                'start': 45,
                                'end': 60,
                                'tag': 'IanSomerhalder'
                            },
                            {
                                'start': 61,
                                'end': 71,
                                'tag': 'NikkiReed'
                            },
                            {
                                'start': 72,
                                'end': 81,
                                'tag': 'SOMEREED'
                            },
                            {
                                'start': 82,
                                'end': 88,
                                'tag': 'Bodhi'
                            },
                            {
                                'start': 93,
                                'end': 97,
                                'tag': 'ISF'
                            },
                            {
                                'start': 100,
                                'end': 105,
                                'tag': 'Yoga'
                            },
                            {
                                'start': 110,
                                'end': 126,
                                'tag': 'BeautifulHumans'
                            },
                            {
                                'start': 127,
                                'end': 139,
                                'tag': 'HarryPotter'
                            }
                        ]
                    }
                },
                'username': 'DElenaTimeless',
                'public_metrics': {
                    'followers_count': 1772,
                    'following_count': 854,
                    'tweet_count': 43347,
                    'listed_count': 53
                },
                'id': '1074184813',
                'created_at': '2013-01-09T16:04:14.000Z',
                'profile_image_url': 'https://pbs.twimg.com/profile_images/600743044535554048/DBgKQQMF_normal.jpg',
                'url': '',
                'pinned_tweet_id': '857131921427615744',
                'protected': False,
                'verified': False,
                'location': 'The Universe'
            },
            {
                'description': 'Researching & reporting the science & impacts of climate change 🌎 \nRetweets and shares ≠ endorsement | image: Alexander Gerst/NASA',
                'name': 'Climate Central',
                'entities': {
                    'url': {
                        'urls': [
                            {
                                'start': 0,
                                'end': 23,
                                'url': 'https://t.co/1I6UpNcrdn',
                                'expanded_url': 'https://www.climatecentral.org',
                                'display_url': 'climatecentral.org'
                            }
                        ]
                    }
                },
                'username': 'ClimateCentral',
                'public_metrics': {
                    'followers_count': 133300,
                    'following_count': 6920,
                    'tweet_count': 61042,
                    'listed_count': 3963
                },
                'id': '15463610',
                'created_at': '2008-07-17T03:30:32.000Z',
                'profile_image_url': 'https://pbs.twimg.com/profile_images/1148257751925186560/3AUI4s1P_normal.png',
                'url': 'https://t.co/1I6UpNcrdn',
                'protected': False,
                'verified': True,
                'location': 'Princeton, NJ'
            }
        ],
        'tweets': [
            {
                'reply_settings': 'everyone',
                'referenced_tweets': [
                    {
                        'type': 'quoted',
                        'id': '878622618886094848'
                    }
                ],
                'text': 'Wildfire season in the American West is now two and a half months longer than it was 40 years ago. Our wildfire report in @YEARSofLIVING ⬇️ https://t.co/nk49r9sS1a',
                'id': '918436293247406080',
                'entities': {
                    'annotations': [
                        {
                            'start': 23,
                            'end': 35,
                            'probability': 0.472,
                            'type': 'Place',
                            'normalized_text': 'American West'
                        }
                    ],
                    'mentions': [
                        {
                            'start': 122,
                            'end': 136,
                            'username': 'YEARSofLIVING',
                            'id': '308245641'
                        }
                    ],
                    'urls': [
                        {
                            'start': 140,
                            'end': 163,
                            'url': 'https://t.co/nk49r9sS1a',
                            'expanded_url': 'https://twitter.com/yearsofliving/status/878622618886094848',
                            'display_url': 'twitter.com/yearsofliving/…'
                        }
                    ]
                },
                'possibly_sensitive': False,
                'conversation_id': '918436293247406080',
                'public_metrics': {
                    'retweet_count': 168,
                    'reply_count': 7,
                    'like_count': 99,
                    'quote_count': 3
                },
                'lang': 'en',
                'author_id': '15463610',
                'source': 'Twitter for iPhone',
                'created_at': '2017-10-12T11:20:50.000Z'
            }
        ]
    }
}
