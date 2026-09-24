#!/usr/bin/env python3
"""
PVR ADK Core Configuration
--------------------------
Canonical settings per P.V.R. Narasimha Rao's research papers.
Strictly based on PUSHYA-PAKSHA AYANAMSA and PVR's exact research methods.

Key Tenet:
  "I am using Pushya Paksha Ayanamsa... for Dashamsa, I use this variation,
   the third one in Jagannatha Hora which is Parasara Dashamsa with even
   sign reversal, go reverse and end in nine."
   — P.V.R. Narasimha Rao (Video lecture transcript 08_Divisional_Charts.md)
"""

# ============================================================
# AYANAMSA SETTING (NON-NEGOTIABLE)
# ============================================================
# PVR Narasimha Rao strictly uses Pushya-Paksha Ayanamsa.
# In PyJHora/Swiss Ephemeris: 'TRUE_PUSHYA' (Delta Cancri anchored at 16 Cn 00' 00")
AYANAMSA_NAME = "PUSHYA_PAKSHA"
AYANAMSA_MODE = "TRUE_PUSHYA"
AYANAMSA_ID   = 29  # SE_SIDM_TRUE_PUSHYA in Swiss Ephemeris

# ============================================================
# DIVISIONAL CHART METHODS
# ============================================================
# D-10: Method 3 (Parasara with Even Sign Reversal)
# D-24: Method 2 (Parasara corrected: Odd Le->Cn, Even Cn->Le)
# D-20: Method 2 (Vaishnava Vimshamsa: Even Sign Reversal)
# D-7 : Method 2 (Even Sign Reversal as noted in lecture 13)
# Others: Method 1 (Standard)
D1_METHOD  = 1   # Rasi chart
D2_METHOD  = 1   # Hora
D3_METHOD  = 1   # Drekkana
D4_METHOD  = 1   # Chaturthamsa
D7_METHOD  = 2   # Saptamsa with even sign reversal
D9_METHOD  = 1   # Navamsa
D10_METHOD = 3   # Dashamsa with even sign reversal (end in 9)
D12_METHOD = 1   # Dwadasamsa
D16_METHOD = 1   # Shodasamsa
D20_METHOD = 2   # Vaishnava Vimshamsa (even sign reversal)
D24_METHOD = 2   # Siddhamsa corrected (Cn->Le for even)
D27_METHOD = 1   # Saptavimshamsa
D30_METHOD = 1   # Trimshamsa
D40_METHOD = 1   # Khavedamsa
D45_METHOD = 1   # Akshavedamsa
D60_METHOD = 1   # Shashtiamsa

CHART_METHOD_MAP = {
    1: D1_METHOD, 2: D2_METHOD, 3: D3_METHOD, 4: D4_METHOD,
    7: D7_METHOD, 9: D9_METHOD, 10: D10_METHOD, 12: D12_METHOD,
    16: D16_METHOD, 20: D20_METHOD, 24: D24_METHOD, 27: D27_METHOD,
    30: D30_METHOD, 40: D40_METHOD, 45: D45_METHOD, 60: D60_METHOD,
}

def get_chart_method(divisional_factor: int) -> int:
    return CHART_METHOD_MAP.get(divisional_factor, 1)

class PVRConfig:
    AYANAMSA_NAME = AYANAMSA_NAME
    AYANAMSA_MODE = AYANAMSA_MODE
    AYANAMSA_ID   = AYANAMSA_ID
    D10_METHOD    = D10_METHOD
    D24_METHOD    = D24_METHOD
    D20_METHOD    = D20_METHOD
    D7_METHOD     = D7_METHOD
    D9_METHOD     = D9_METHOD
    D60_METHOD    = 3
    CHART_METHOD_MAP = CHART_METHOD_MAP

# ============================================================
# SOLAR RETURN DEFINITION
# ============================================================
# Paper 04: Tajaka Varshaphal -> TROPICAL solar return (Sun returns to exact tropical longitude)
# Paper 05: Tithi Pravesha -> TROPICAL solar month return
SOLAR_RETURN_TYPE = "TROPICAL"

# ============================================================
# PANCHA KOSHA MAPPING (Paper 02)
# ============================================================
PANCHA_KOSHA_MAP = {
    "Annamaya": {
        "charts": [1, 2, 3, 4, 7, 9, 10, 12],
        "sheath": "Physical Matter & Material Entities",
        "description": "Physical body, wealth, siblings, real estate, children, spouse, career, parents"
    },
    "Praanamaya": {
        "charts": [16, 20, 24],
        "sheath": "Life Force Energy & Spending Praana",
        "description": "Spending praana for comfort (D16), spiritual sadhana (D20), knowledge/education (D24)"
    },
    "Manomaya": {
        "charts": [27, 30],
        "sheath": "Mind, Sankalpa/Vikalpa & Subconscious Enemies",
        "description": "Mental intentions/strengths (D27), fighting internal shadripus/weaknesses (D30)"
    },
    "Vijnanamaya": {
        "charts": [40, 45],
        "sheath": "Higher Intellect, Ritam & Satyam",
        "description": "Subtle awareness of Cosmic Rhythm Ritam (D40), adherence to Truth & Dharma Satyam (D45)"
    },
    "Aanandamaya": {
        "charts": [60],
        "sheath": "Bliss, Core Soul Motivation & Root Desires",
        "description": "Causal motivations, past life impressions, what delights the soul at the deepest level (D60)"
    }
}

# ============================================================
# UNIFIED NAKSHATRA DASA (Paper 03)
# ============================================================
CONDITIONAL_DASA_SPECS = {
    "Shodasottari": {
        "span_years": 116,
        "seed_nakshatra": "Pushya",
        "controlling_planet": "Jupiter",
        "description": "Lagna in Sun hora in Sukla paksha OR Moon hora in Krishna paksha"
    },
    "Dwadasottari": {
        "span_years": 112,
        "seed_nakshatra": "Revati",
        "controlling_planet": "Ketu",
        "description": "Lagna in Taurus or Libra navamsa"
    },
    "Ashtottari": {
        "span_years": 108,
        "seed_nakshatra": "Ardra",
        "controlling_planet": "Mars",
        "description": "Rahu in kendra/trikona from lagna lord, but not occupying lagna"
    },
    "Panchottari": {
        "span_years": 105,
        "seed_nakshatra": "Anuradha",
        "controlling_planet": "Venus",
        "description": "Lagna in Cancer dwadasamsa"
    },
    "Satabdika": {
        "span_years": 100,
        "seed_nakshatra": "Revati",
        "controlling_planet": "Sun",
        "description": "Lagna in same sign in rasi and navamsa (Vargottama)"
    },
    "Chaturaaseeti": {
        "span_years": 84,
        "seed_nakshatra": "Swati",
        "controlling_planet": "Saturn",
        "description": "10th lord in 10th house"
    },
    "Dwisaptati": {
        "span_years": 72,
        "seed_nakshatra": "Moola",
        "controlling_planet": "Rahu",
        "description": "Lagna lord in 7th or 7th lord in lagna"
    },
    "Shashtisama": {
        "span_years": 60,
        "seed_nakshatra": "Ashwini",
        "controlling_planet": "Moon",
        "description": "Sun in lagna"
    },
    "Shattrimsa": {
        "span_years": 36,
        "seed_nakshatra": "Shravana",
        "controlling_planet": "Mercury",
        "description": "Lagna in Sun hora daytime OR Moon hora nighttime"
    },
    "Vimsottari": {
        "span_years": 120,
        "seed_nakshatra": "Krittika",
        "controlling_planet": "None (Universal Default)",
        "description": "Default and supreme dasa taught by Parasara"
    }
}

# ============================================================
# TRANSIT TRIGGER CONSTANTS (Paper 08)
# ============================================================
STATIONARY_ORB_DEGREES = 3.0
STATIONARY_TIME_WINDOW_DAYS = 60

# ============================================================
# CHARA DASA CONSTANTS (Paper 09)
# ============================================================
ODD_FOOTED_SIGNS = [0, 1, 2, 6, 7, 8]     # Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius
EVEN_FOOTED_SIGNS = [3, 4, 5, 9, 10, 11]  # Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces

# Names & Symbols
PLANET_NAMES = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
RASI_NAMES   = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
RASI_SHORT   = ['Ar', 'Ta', 'Ge', 'Cn', 'Le', 'Vi', 'Li', 'Sc', 'Sg', 'Cp', 'Aq', 'Pi']
NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]
