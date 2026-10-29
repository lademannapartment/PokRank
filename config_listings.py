import datetime as dt

# --- ВАШИ КОНСТАНТЫ ---
# URL Вашей Google Таблицы
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1t8jZFnJ5PxW9ry8SPN8WAGhbsgICn5F9BZCR9d4vB5U/edit"

# Названия листов
SHEET_NAME_GDANSK = "RankPokGdansk"
SHEET_NAME_SOPOT = "RankSopot"
SHEET_NAME_GDYNIA = "RankPokGdynia"  # <<< НОВАЯ КОНСТАНТА
# Общие параметры поиска
STAY_NIGHTS = 1
TIMEOUT_SEC = 60
DAYS_FORWARD = 60
MAX_RANK = 400
CREDENTIALS_FILE = "silken-glyph-443313-i4-cdf14b36288a.json"

# --- ЛИСТИНГИ ГДАНЬСКА (GDANSK) ---
MMRENT_COUNT_COLUMN_GDANSK = 3
# СВЯЗКА: Название листинга -> Индекс столбца (начиная с I=9)
LISTING_COLUMNS_GDANSK = {
    "Cactus Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 9,
    "Pineapple Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 10,
    "Jager Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 11,
    "Cosy Room - Peaceful Retreat, 2 Minutes to Gdańsk Old Town": 12,
    "Lovely Room - Peaceful Retreat, 2 Minutes to Gdańsk Old Town": 13,
    "Spacious Room - Peaceful Retreat, 2 Minutes to Gdańsk Old Town": 14,
    "Bay Room -15 Minutes to Gdańsk Old Town & Seaside": 15,
    "Mirror Room -15 Minutes to Gdańsk Old Town & Seaside": 16,
    "Beacon Room -15 Minutes to Gdańsk Old Town & Seaside": 17,
    "Superfly room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 18,
    "Sensational room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 19,
    "Vintage room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 20,
    "Leaf Room - 20 Minutes to Gdańsk Old Town & Seaside": 21,
    "Nest Room - 20 Minutes to Gdańsk Old Town & Seaside": 22,
    "Square Room - 20 Minutes to Gdańsk Old Town & Seaside": 23,
    "Twig Room - 20 Minutes to Gdańsk Old Town & Seaside": 24,
    "Alpha Room 15 min to Old Town Gdansk": 25,
    "Beta Room 10 min to Old Town Gdansk": 26,
    "Gamma Room 10 min to Old Town Gdansk": 27,
    "Downtown Room at Old Town Gdansk": 28,
    "Plaza Room at Old Town Gdansk": 29,
    "Danzig Room at Old Town Gdansk": 30,
    "Dali Room -10 Minutes to Gdańsk Old Town & Sea": 31,
    "Munch Room -10 Minutes to Gdańsk Old Town & Sea": 32,
    "Picasso Room -10 Minutes to Gdańsk Old Town & Sea": 33,
    "Beksiński Room -10 Minutes to Gdańsk Old Town & Sea": 34,
    "René Room -10 Minutes to Gdańsk Old Town & Sea": 35,
    "Van Gogh Room - 10 Minutes to Gdańsk Old Town & Sea": 36,
    "Creative Room - 10 Minutes to Gdańsk Old Town & Seaside": 37,
    "World Room - 10 Minutes to Gdańsk Old Town & Seaside": 38,
    "Lama Room - 10 Minutes to Gdańsk Old Town & Seaside": 39,
    "Colourful Room - 10 Minutes to Gdańsk Old Town & Seaside": 40,
    "Dolce Vita Room - 10 Minutes to Gdańsk Old Town & Seaside": 41,
    "Shrek Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 43,
    "Scooby Doo Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 45,
    "Pink Panther Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 46,
    "Spongebob Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 47,
    "Big Ben Room - Peaceful Retreat, 10 Minutes to Gdańsk Old Town & Seaside": 48,
    "Cracov Room - Peaceful Retreat, 10 Minutes to Gdańsk Old Town & Seaside": 49,
    "Breslau Room - Peaceful Retreat, 15 Minutes to Gdańsk Old Town & Seaside": 50,
    "Manhattan Room - Peaceful Retreat, 10 Minutes to Gdańsk Old Town & Seaside": 51,
    "Roma Room - Peaceful Retreat, 10 Minutes to Gdańsk Old Town & Seaside": 52,
    "Motlava Room - Peaceful Retreat, 10 Minutes to Gdańsk Old Town & Seaside": 53,
    "Shark Room - 3 km to Baltic Sea": 54,
    "Piggy Room - 3 km to Baltic Sea": 55,
    "Turtle Room - 3 km to Baltic Sea": 56,
    "Tiny Room - 10 Minutes to Gdańsk Old Town": 57,
    "Astro Room - 10 Minutes to Gdańsk Old Town": 58,
    "Future Room - 10 Minutes to Gdańsk Old Town": 59,
    "Hope Room - 10 Minutes to Gdańsk Old Town": 60,
    "Brand Room - 10 Minutes to Gdańsk Old Town": 61,
    "Umbrella Room - 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 62,
    "Duo Room - 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 63,
    "Teddy Bear Room - 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 64,
    "Circus Room - 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 65,
    "Bonjour Room - 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 66,
    "Ocean Room - 1 km to Baltic Sea & 15 Minutes to Gdańsk Old Town": 67,
    "Sandcastle Room - 1 km to Baltic Sea & 15 Minutes to Gdańsk Old Town": 68,
    "Coral Room - 1 km to Baltic Sea & 15 Minutes to Gdańsk Old Town": 69,
    "Jungle Room Old Town Gdansk": 70,
    "Rose Room Old Town Gdansk": 71,
    "Paris Room Old Town Gdansk": 72,
    "Giraffe Room 5 min to Old Town Gdańsk": 73,
    "Zebra Room 5 min to Old Town Gdańsk": 74,
    "Monkey Room 5 min to Old Town Gdańsk": 75,
    "Snake Room 5 min to Old Town Gdańsk": 76,
    "Stitch Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 77,
    "Lion King Room 10 Min to Old Town Gdańsk,PKP & Shopping Mall": 78,
    "Ruby Room at Old Town Gdańsk": 79,
    "Silver Room at Old Town Gdańsk": 80,
    "Bronze Room at Old Town Gdańsk": 81,
    "Mercury Room - 15 min to Old Town Gdansk": 82,
    "Hostel Room - 15 min to Old Town Gdansk": 83,
    "Earth Room - 15 min to Old Town Gdansk": 84,
    "Mars Room - 15 min to Old Town Gdansk": 85,
    "Jupiter Room - 15 min to Old Town Gdansk": 86,
    "Saturn Room - 15 min to Old Town Gdansk": 87,
    "Uranus Room - 15 min to Old Town Gdansk": 88,
    "Neptune Room - 15 min to Old Town Gdansk": 89,
    "Pluto Room - 15 min to Old Town Gdansk": 90,
    "Milkyway Room - 15 min to Old Town Gdansk": 91,
    "Sunlight Room - 15 min to Old Town Gdansk": 92,
    "Empire Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 93,
    "Droid Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 94,
    "Stormley Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 95,
    "Bounty Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 96,
    "Sir Yodington Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 97,
    "Cinque Terre Guest Room - at Old Town Gdansk": 98,
    "Verona Guest Room - at Old Town Gdansk": 99,
    "Lisbon Guest Room - at Old Town Gdansk": 100,
    "Lucca Guest Room - at Old Town Gdansk": 101,
    "Adore Room - at Old Town Gdansk": 102,
    "Ballerina's Room - at Old Town Gdansk": 103,
    "Rosie Room - at Old Town Gdansk": 104,
    "Seredino Room 4 - at Old Town Gdansk": 105,
    "Petite Room - at Old Town Gdansk": 106,
    "Atelier Room - at Old Town Gdansk": 107,
    "Jazz Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 108,
    "Baroque Rebel Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 109,
    "Angel Mood Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 110,
    "Dream Big Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 111,
    "Frog Swing Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 112,
    "Fast & Steady Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 113,
    "Tiger Country Club Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 114,
    "Mr Fox Room - 15 Minutes to Gdańsk Old Town & Seaside & Airport": 115,
    "Bengal Room - 10 Minutes to Gdańsk Old Town & Sea": 116,
    "Birman Room - 10 Minutes to Gdańsk Old Town & Sea": 117,
    "Siamese Room - 10 Minutes to Gdańsk Old Town & Sea": 118,
    "Maine Con Room - 10 Minutes to Gdańsk Old Town & Sea": 119,
    "Scotish Fold Room - 10 Minutes to Gdańsk Old Town & Sea": 120,
    "Ragdoll Room - 10 Minutes to Gdańsk Old Town & Sea": 121,
    "Industrial Room - at Old Town Gdansk": 122,
    "Loft Room - at Old Town Gdansk": 123,
    "Nordic Room - at Old Town Gdansk": 124,
    "Woody Room - at Old Town Gdansk": 125,
}

# --- ЛИСТИНГИ СОПОТА (SOPOT) ---
LISTING_COLUMNS_SOPOT = {
    "Deer Room - 5 Minutes to Sopot Molo & Seaside": 6,   # F
    "Elk Room - 5 Minutes to Sopot Molo & Seaside": 7,    # G
    "Balance Room - 5 Minutes to Sopot Molo & Seaside": 8,# H
    "Funky Room - 5 Minutes to Sopot Molo & Seaside": 9,  # I
    "Array Room - 5 Minutes to Sopot Molo & Seaside": 10, # J
    "Surf Room - 5 Minutes to Sopot Molo & Seaside": 11,  # K
}

LISTING_COLUMNS_GDYNIA = {
    "Blue Room 2 minutes to City Center Gdynia & Seaside": 6,
    "Green Room 2 minutes to City Center Gdynia & Seaside": 7,
    "Orange Room 2 minutes to City Center Gdynia & Seaside": 8,
    "Catch the Wave Room in the Center of Gdynia": 9,
    "Retro Room in the Center of Gdynia": 10,
    "Wild & Free Room in the Center of Gdynia": 11,
    "Summer Vibes Room in the Center of Gdynia": 12,
    "Quill Room": 13,
    "Robot Room": 14,
    "Fox Room": 15,
    "Seaside Room": 16,
    "plato": 17,
    "Panda Room": 18,
}

