dictionary = {

    "GetSetBuiltAt": 0,

    "additionalFeatures": {

        "characteristics": {

            "has_wheelchair_access": False,
            "managerie": False,
            "new_building": False,
            "pets": False,
            "share": False
        },

        "energy": {
            "eClass": "",
            "eConsumption": ""
        },

        "equipment": {
            "airConditioning": False,
            "barbecue": False,
            "cableTv": False,
            "ceramicHob": False,
            "dishwasher": False,
            "isdn": False,
            "steamOven": False,
            "tumbleDryer": False,
            "washingMachine": False
        },

        "exterior": {
            "balcony": False,
            "barbecue": False,
            "childFriendly": False,
            "lift": False,
            "parkingSpace": False,
            "playground": False,
            "pool": False,
            "privateGarage": False
        },

        "heating": {
            "electrical": False,
            "fuel": False,
            "gas": False,
            "pump": False,
            "solar": False,
            "wood": False
        },

        "interior": {
            "attic": False,
            "cellar": False,
            "fireplace": False,
            "hobbyRoom": False,
            "parquet": False,
            "pool": False,
            "sauna": False,
            "storageRoom": False,
            "view": False,
            "wineCellar": False
        }
    },

    "address": {
        "autcomplete": "",
        "city": "",
        "country": "",
        "neighbourhood": "",
        "street": "",
        "zipCode": "",
        "cityValue":{
            "translations":{

            }
        },
        "kanton":{
            "translations":{

            }
        },
    },


    "countryCode": "CH",

    "details": {
        "availableAt": 0,
        "builtAt": 0,
        "description": "",
        "keywords": "",
        "renovatedAt": ""
    },

    "distances": {
        "busStation": 0,
        "highway": 0,
        "kindergarden": 0,
        "playground": 0,
        "primarySchool": 0,
        "proximity": {
            "lake": False,
            "mountains": False,
            "sea": False
        },
        "secondarySchool": 0,
        "shopping": 0,
        "trainStation": 0,
        "university": 0
    },

    "idAgency": "",
    "idAgents": [],
    "idOwner": "",
    "isActive": False,
    "isDraft": False,
    "isPaid": False,
    "isRent": False,
    "isSale": False,
    "lat": 0,
    "lon": 0,

    "mainFeatures": {
        "baths": 0,
        "floor": 0,
        "floorSpace": 0,
        "floors": 0,
        "garages": 0,
        "livingSpace": 0,
        "lotSize": 0,
        "parkings": 0,
        "roomHeight": 0,
        "rooms": 0,
        "showers": 0,
        "toilets": 0,
        "volume": 0
    },

    "media": {
        "brochures": [],
        "gallery": [],
        "gallery_extra":{
            "gallery":{

            },
            "single":{

            }
        },
        "lead": "",
        "logo": "",
        "videos": []
    },

    "name": "",

    "price": {
        "currency": "CHF",
        "expenses": 0,
        "rentNetPrice": 0,
        "rentPrice": 0,
        "rentUnit": 0,
        "salePrice": 0
    },


    "stats": {
        "bookmarks": 0,
        "likes": 0
    },

    "subname": "",
    "subtype": "",
    "timeStampAdded": "",
    "timeStampAddedObject": "",
    "timeStampExpires": "",
    "timeStampExpiresObject": "",
    "categories": [],
    "visitInformation": {
        "name": "",
        "phone": ""
    },
    "nemanja_scout24": True,
    "isSpider": True,
    "spiderName":"scout24",
    "origSource":"",
    "isExpired":False,
    "done":False
}

actions = ['rent', 'buy']

categories = ['flat', 'house', 'furnished-residential-property',
              'office-commerce-industry', 'parking-space', 'new-building']

cantons = ['canton-appenzell-inner-rhoden',
           'canton-appenzell-ausser-rhoden',
           'canton-basel-landschaft',
           'canton-bern',
           'canton-fribourg',
           'canton-aargau',
           'canton-geneva',
           'canton-glarus',
           'canton-grisons',
           'canton-jura',
           'canton-lucerne',
           'canton-nidwalden',
           'canton-obwalden',
           'canton-schaffhausen',
           'canton-schwyz',
           'canton-solothurn',
           'canton-st-gallen',
           'canton-thurgau',
           'canton-uri',
           'canton-zurich',
           'canton-zug',
           'canton-basel-stadt',
           'canton-neuchatel',
           'canton-valais',
           'canton-ticino',
           'canton-vaud'
           ]

headers = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"en-US,en;q=0.8,fr;q=0.6,de-CH;q=0.4,de;q=0.2,it;q=0.2",
    "Cache-Control":"no-cache",
    "Connection":"keep-alive",
    "Cookie":"ASP.NET_SessionId=ppd2gq4dcjdp1ta3dosyrrj1; xm_immoweb=682887690.20480.0000; __RequestVerificationToken=ybcoGsTfGUNQLx5YwF76ldVxD7c7L7pnIYGPbsK5DA9uL37SDWOLvk01f6xtmqgJ2QAXQzIDr7iR_2NYLAOMzNcndVE1; cv-type-search=commercial; TS01e0caa0=017721f21fd50eeb2c2d76c7abc9edb8eea71274e5953e5ba349d6f14ea9c067d7bb5e0bab8ac5f4e236fec1d7fc530c2ff1d7f05b; optimizelySegments=%7B%223015460430%22%3A%22referral%22%2C%223016060529%22%3A%22gc%22%2C%223030850461%22%3A%22false%22%2C%224392040044%22%3A%22none%22%7D; optimizelyBuckets=%7B%225888203954%22%3A%225883700990%22%7D; ki_t=1463747524807%3B1475502332400%3B1475502332400%3B25%3B225; ki_r=; TS01b76dde=017721f21f2a2c6701280b1102e1c5c4638ed319968512702914b1adde27ba2e9a4ab65237e9de66e6db47ce431216dd8486dcaa9583df3f8999ce707c64680950c14fa2c5db4c37c8876ca108af6836ea62c904840797bc57befa4704d685ff95204533cb; IS24_DATA=eyJ2ZXJzaW9uIjoyLCJsbmciOjMsImZvcmNlQWRzIjpudWxsLCJoaWRlSXBhZEFwcERvd25sb2FkIjpmYWxzZSwicGFnZVNpemUiOjEyMCwiZm9yY2VEZXZpY2VSZWRpcmVjdGlvbiI6ZmFsc2UsInNlYXJjaCI6eyJsYXN0U2VhcmNoIjoicz0yJnQ9MSZsPTQxNTcmcj00MCIsIm9wZW5GbG9vIjpudWxsLCJvcGVuUHJvcCI6bnVsbCwib3BlbkF0dHIiOm51bGwsIm9wZW5BZ2VzIjpudWxsLCJvcGVuUXVhciI6bnVsbCwib3BlbkF2YWkiOm51bGwsInJlY2VudFBsYWNlcyI6bnVsbCwiY2l0eUFyZWFIaW50Q2xvc2VkIjpudWxsfSwiY29udGFjdCI6eyJnZW5kZXIiOm51bGwsImVtYWlsIjpudWxsLCJuYW1lIjpudWxsLCJmaXJzdG5hbWUiOm51bGwsInBob25lIjpudWxsLCJzdHJlZXQiOm51bGwsInN0cmVldG51bWJlciI6bnVsbCwiemlwIjpudWxsLCJjaXR5IjpudWxsLCJjb250YWN0cmVhc29uIjpudWxsLCJtc2ciOm51bGwsInJlY2lwaWVudGVtYWlsIjpudWxsfSwiZmVlZGJhY2siOnsiZW1haWwiOm51bGx9LCJwcm9wZXJ0eUFkbWluIjp7ImNsb3NlZFBhZ2VNZXNzYWdlcyI6W119LCJoaWRlTmF0aXZlQXBwTGluayI6ZmFsc2UsImRldGFpbHMiOnsibGFzdE9mZmVyVHlwZSI6bnVsbCwibGFzdE1zUmVnaW9uSWQiOm51bGx9LCJsb2dpbmJyb3dzZXJ0YWciOnsiYnJvd3NlcnRhZyI6bnVsbH0sInN1cnZleSI6eyJoaWRlR2VuZXJpY1dlYk1lc3NhZ2VJRCI6bnVsbH0sImZhdm91cml0ZSI6eyJpZGVudGlmaWVyIjpudWxsLCJ0ZW1wSWRlbnRpZmllciI6bnVsbCwic29ydE9wdGlvbiI6bnVsbH0sImZpbmFuY2VDYWxjdWxhdG9yIjp7InNlbGxpbmdQcmljZSI6bnVsbCwiZXF1aXR5Q2FwaXRhbCI6bnVsbCwieWVhcmx5RWFybmluZyI6bnVsbCwiaW50ZXJlc3RSYXRlIjpudWxsLCJzaG93U3VjY2Vzc01lc3NhZ2UiOmZhbHNlfSwiaW5zZXJ0aW9uIjp7InNlbGVjdGVkUnVudGltZUR1cmF0aW9uIjpudWxsLCJzZWxlY3RlZFJ1bnRpbWVQYWNrYWdlIjpudWxsfSwidHJhY2tpbmciOnsiZW1haWxIYXNoIjpudWxsfX0%3d; TS014244ca=017721f21fffda2af1f637bd1d7751f5cf2c9d3de80fa2f41d58ba0aa95d1edd75631d68eaedaa7fdef04c0a37b8fe53a899ea74175637531e8747e07481c13881fdb228f69c8dd933e414d040f8ce9edcc473e7fe; s24gtm_currentInsertionStep=home; optimizelyEndUserId=oeu1463747522780r0.628291409981264; _ga=GA1.2.331309166.1463747523; _gid=GA1.2.1285955615.1507816450; _dc_gtm_UA-960143-1=1; axd=1001114881317500133; _uetsid=_uetfc8d0bce; trckr-e1948aa9-2b4c-4220-8fa8-e956dd2d9a90=%7B%22hasAdBlocker%22%3A%22No%22%7D; TS0115e3b4=017721f21f31dc6a4151484642b960ce50e4933f2eb5bc830cf70bcee60ad2b775ab430fc17f3647741258a5e9ce318db087caa6b3",
    "Host":"www.immoscout24.ch",
    "Pragma":"no-cache",
    "Referer":"https://www.immocosmos.ch/",
    "Upgrade-Insecure-Requests":"1",
    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36"
}

apartment_categories = ['flat', 'attic-flat', 'duplex-maisonette', 'furnished-residential-property', 'stepped-apartment',
                        'loft', 'penthouse', 'single-room', 'studio', 'secondary-suite', 'attic-room']

house_categories = ['detached-house', 'villa', 'castle', 'chalet', 'rustico', 'terrace-house',
                    'stepped-house', 'farmhouse', 'detached-secondary-suite', 'stepped-house', 'semi-detached-house']

parking_categories = ['parking-space-outdoor-covered-or-uncovered', 'parking-space-in-garage', 'single-garage',
                      'shelter', 'motorcycle-parking-space', 'motorcycle-parking-space-outdoor-covered-or-uncovered',
                      'box-stall', 'double-garage']

office_commerce_categories = ['advertising-space', 'arcade', 'bar', 'bakery', 'butcher’s', 'cafe',
                              'car-park', 'commercial-premises', 'commercial-premises', 'factory', 'hair-salon',
                              'industrial-property', 'kiosk', 'multi-storey-car-park', 'office', 'office-building',
                              'practice', 'residential-and-office-building', 'restaurant', 'retail-space', 'sauna',
                              'warehouse', 'workshop', 'shopping-centre', 'discotheque-club', 'hotel', 'pub']