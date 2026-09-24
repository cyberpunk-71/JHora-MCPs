#!/usr/bin/env python3
"""
PVR Research Papers - Complete Example Verification Engine
==========================================================
Verifies all published examples across PVR Narasimha Rao's 9 research papers.
Strictly uses Pushya-Paksha Ayanamsa (AYANAMSA_ID=29, SE_SIDM_TRUE_PUSHYA).
Checks every substep of inference:
  - Seed sign & controlling planet selection
  - Divisional calculation methods (D-10 method 3, D-24 method 2, D-7 method 2, D-20 method 2)
  - Return moments (Tropical Varshaphal, Tropical New Moon Tithi Pravesha, Chaitra Pratipada)
  - Stationary transit divisional longitudes and natal aspect triggers
  - Dasa progression ray and transit triggers
  - Chara Dasa reference strength, footedness, and event sign matches
"""

import os
import sys
import re
import math
from typing import Dict, List, Any, Optional

sys.path.insert(0, "/home/opc/mcp_jhora")

import swisseph as swe
from pvr_adk.core.config import PVRConfig
from pvr_adk.core.chart_engine import (
    get_birth_chart, get_julian_day, PLANET_NAMES, RASI_NAMES
)
from pvr_adk.adks.adk01_ayanamsa_foundation import ADK01AyanamsaFoundation
from pvr_adk.adks.adk02_pancha_kosha import ADK02PanchaKosha
from pvr_adk.adks.adk03_unified_nakshatra_dasa import ADK03UnifiedNakshatraDasa
from pvr_adk.adks.adk04_tajaka_varshaphal import ADK04TajakaVarshaphal
from pvr_adk.adks.adk05_tithi_pravesha import ADK05TithiPravesha
from pvr_adk.adks.adk06_lunar_new_year import ADK06LunarNewYear
from pvr_adk.adks.adk07_dasa_progression import ADK07DasaProgression
from pvr_adk.adks.adk08_novel_transits import ADK08NovelTransits
from pvr_adk.adks.adk09_chara_dasa_vargas import ADK09CharaDasaVargas
from jhora.horoscope.chart import charts
from jhora_helpers import create_date_and_place

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def clean_text(s: str) -> str:
    s = s.replace("–", "-").replace("—", "-").replace("”", '"').replace("“", '"').replace("’", "'").replace("‘", "'")
    s = re.sub(r"GM\s*T", "GMT", s)
    return s

def parse_coords(s: str):
    s = clean_text(s)
    lon, lat = None, None
    m_lon = re.search(r"(\d+)\s*([ew])\s*(\d+)?", s, re.I)
    if m_lon:
        deg = float(m_lon.group(1))
        mins = float(m_lon.group(3)) if m_lon.group(3) else 0.0
        lon = deg + mins / 60.0
        if m_lon.group(2).lower() == "w":
            lon = -lon
    m_lat = re.search(r"(\d+)\s*([ns])\s*(\d+)?", s, re.I)
    if m_lat:
        deg = float(m_lat.group(1))
        mins = float(m_lat.group(3)) if m_lat.group(3) else 0.0
        lat = deg + mins / 60.0
        if m_lat.group(2).lower() == "s":
            lat = -lat
    return lat, lon

def parse_tz(s: str) -> float:
    s = clean_text(s)
    if "ist" in s.lower():
        return 5.5
    m = re.search(r"(\d+):(\d+)\s*(east|west)", s, re.I)
    if m:
        val = float(m.group(1)) + float(m.group(2))/60.0
        return val if m.group(3).lower() == "east" else -val
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:hrs?|hours?)\s*(east|west)", s, re.I)
    if m:
        val = float(m.group(1))
        return val if m.group(2).lower() == "east" else -val
    if "edt" in s.lower():
        return -4.0
    if "est" in s.lower():
        return -5.0
    if "cst" in s.lower():
        return -6.0
    if "pst" in s.lower():
        return -8.0
    return 5.5

def parse_birthdata(s: str) -> Optional[Dict[str, Any]]:
    if not s:
        return None
    s = clean_text(s)
    m = re.search(r"(\d{4})\s+([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{1,2})(?::(\d{2}))?(?::(\d{2}))?\s*(am|pm)?", s, re.I)
    if not m:
        return None
    year = int(m.group(1))
    month = MONTHS.get(m.group(2).lower(), 1)
    day = int(m.group(3))
    hour = int(m.group(4))
    minute = int(m.group(5)) if m.group(5) else 0
    second = float(m.group(6)) if m.group(6) else 0.0
    ampm = m.group(7)
    if ampm:
        if ampm.lower() == "pm" and hour < 12:
            hour += 12
        elif ampm.lower() == "am" and hour == 12:
            hour = 0
            
    tz = parse_tz(s)
    lat, lon = parse_coords(s)
    if lat is None or lon is None:
        low = s.lower()
        if "calcutta" in low or "kolkata" in low:
            lat, lon = 22.5667, 88.3667
        elif "porbandar" in low:
            lat, lon = 21.6167, 69.8167
        elif "bombay" in low or "mumbai" in low:
            lat, lon = 18.9667, 72.8167
        elif "new delhi" in low or "delhi" in low:
            lat, lon = 28.6000, 77.2000
        elif "washington" in low:
            lat, lon = 38.8951, -77.0364
        elif "new haven" in low:
            lat, lon = 41.3083, -72.9279
        elif "manhattan" in low or "new york" in low:
            lat, lon = 40.7831, -73.9712
        elif "machilipatnam" in low:
            lat, lon = 16.1667, 81.1333
        elif "guntur" in low:
            lat, lon = 16.3000, 80.4500
        elif "amaravati" in low:
            lat, lon = 16.5833, 80.3667
        elif "eluru" in low:
            lat, lon = 16.7000, 81.1000
        elif "chennai" in low or "madras" in low:
            lat, lon = 13.0827, 80.2707
        elif "pondicherry" in low:
            lat, lon = 11.9416, 79.8083
        elif "sambalpur" in low:
            lat, lon = 21.4667, 83.9667
        elif "brookline" in low:
            lat, lon = 42.3318, -71.1212
        elif "honolulu" in low:
            lat, lon = 21.3069, -157.8583
        else:
            lat, lon = 16.1667, 81.1333
            
    return {
        "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute, "second": second,
        "tz": tz, "lat": lat, "lon": lon, "raw": s
    }

print("PVR Example Parser loaded successfully.")
