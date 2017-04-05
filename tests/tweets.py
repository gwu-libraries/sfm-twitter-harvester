#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
