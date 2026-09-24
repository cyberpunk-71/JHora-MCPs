"""
PVR Annual Engine Configuration & Constants
===========================================
Defines planetary orbs, dignities, Tajaka Saham formulas, and Ayanamsa settings.
"""

import os
import swisseph as swe

# Centralized Configurable LLM Settings
LLM_API_KEY = os.environ.get("PVR_LLM_API_KEY") or os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY") or ""
LLM_BASE_URL = os.environ.get("PVR_LLM_BASE_URL") or os.environ.get("LLM_BASE_URL") or "http://127.0.0.1:8090/v1"
LLM_MODEL = os.environ.get("PVR_LLM_MODEL") or os.environ.get("LLM_MODEL") or "gemini-3.8-flash-high"

def get_llm_headers(extra_headers: dict = None) -> dict:
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    if extra_headers:
        headers.update(extra_headers)
    return headers

def get_llm_chat_endpoint() -> str:
    base = LLM_BASE_URL.rstrip("/")
    if not base.endswith("/chat/completions"):
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"
    return base

# Ayanamsa: Pushya-Paksha (Delta Cancri @ 16Cn00)
AYANAMSA_ID = swe.SIDM_TRUE_PUSHYA

RASI_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

PLANET_NAMES = [
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'
]

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Sign lords: 0=Aries (Mars), 1=Taurus (Venus), ..., 11=Pisces (Jupiter)
SIGN_LORDS = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]

# Planetary Speeds (mean degrees per day for Tajaka applying/separating aspect resolution)
PLANET_MEAN_SPEEDS = {
    "Moon": 13.176,
    "Mercury": 1.383,
    "Venus": 1.200,
    "Sun": 0.9856,
    "Mars": 0.524,
    "Jupiter": 0.083,
    "Saturn": 0.033,
    "Rahu": -0.053,
    "Ketu": -0.053
}

# Deeptamsha Orbs (Maximum orb in degrees for Tajaka aspects/Ithasala yogas)
DEEPTAMSHA_ORBS = {
    "Sun": 15.0,
    "Moon": 12.0,
    "Mars": 8.0,
    "Mercury": 7.0,
    "Jupiter": 9.0,
    "Venus": 7.0,
    "Saturn": 9.0,
    "Rahu": 6.0,
    "Ketu": 6.0
}

# Dignity tables
EXALTATION_SIGNS = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 1, "Ketu": 7}
MOOLATRIKONA_SIGNS = {"Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5, "Jupiter": 8, "Venus": 6, "Saturn": 10, "Rahu": 5, "Ketu": 11}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10], "Rahu": [10], "Ketu": [7]
}
DEBILITATION_SIGNS = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0, "Rahu": 7, "Ketu": 1}

# Topic specifications mapping life queries to relevant houses and divisional charts
TOPIC_SPECS = {
    "academic_success": {
        "title": "Academic Distinction & Higher Learning",
        "houses": [5, 4, 9, 1],
        "varga": "D24",
        "varga_name": "Siddhamsa (D-24)",
        "karakas": ["Jupiter", "Mercury"],
        "saham": "Vidya",
        "desc": "Competitive exams, state/national rank, university admission, scholarship, technical mastery"
    },
    "career_success": {
        "title": "Career Advancement & Executive Authority",
        "houses": [10, 1, 9, 5, 11],
        "varga": "D10",
        "varga_name": "Dasamsa (D-10)",
        "karakas": ["Sun", "Saturn", "Mercury", "Jupiter"],
        "saham": "Karma",
        "desc": "Professional elevation, promotion, ministerial mandate, institutional power, societal prominence"
    },
    "marriage": {
        "title": "Marriage & Relationship Alliance",
        "houses": [7, 1, 2, 9, 11],
        "varga": "D9",
        "varga_name": "Navamsa (D-9)",
        "karakas": ["Venus", "Jupiter"],
        "saham": "Vivaha",
        "desc": "Formal wedding, life partnership, relationship fruition, partner harmony"
    },
    "childbirth": {
        "title": "Progeny & Childbirth",
        "houses": [5, 9, 1, 2],
        "varga": "D7",
        "varga_name": "Saptamsa (D-7)",
        "karakas": ["Jupiter"],
        "saham": "Putra",
        "desc": "Conception, safe delivery, happiness from progeny, lineage expansion"
    },
    "foreign_travel": {
        "title": "Foreign Travel & Relocation",
        "houses": [9, 12, 4, 7],
        "varga": "D4",
        "varga_name": "Chaturthamsa (D-4)",
        "karakas": ["Rahu", "Saturn", "Moon"],
        "saham": "Paradesa",
        "desc": "International studies, foreign relocation, long-distance journey, overseas residence"
    }
}
