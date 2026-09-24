#!/usr/bin/env python3
"""
Common Helper utilities for PyJHora MCP servers.
Handles Date, Place, Julian Day, formatting, and Ayanamsa configurations.
"""
from __future__ import annotations
import math
from typing import Dict, Any, Tuple, Optional, List
from jhora import utils, const
from jhora.panchanga import drik

RASI_NAMES = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

PLANET_NAMES = [
    'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu'
]

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

AYANAMSA_MAP = {
    "LAHIRI": const._DEFAULT_AYANAMSA_MODE,
    "PUSHYA_PAKSHA": "PUSHYA_PAKSHA",
    "PUSHYAPAKSHA": "PUSHYA_PAKSHA",
    "RAMAN": "BVRAMAN",
    "BVRAMAN": "BVRAMAN",
    "KP": "KRISHNAMURTHY",
    "KRISHNAMURTI": "KRISHNAMURTHY",
    "YUKTESHWAR": "YUKTESHWAR",
    "JN_BHASIN": "JN_BHASIN",
    "SAYANA": "SAYANA"
}

def create_date_and_place(
    year: int,
    month: int,
    day: int,
    hour: int = 12,
    minute: int = 0,
    second: float = 0.0,
    latitude: float = 13.0827,
    longitude: float = 80.2707,
    timezone_offset: float = 5.5,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI"
) -> Tuple[drik.Date, Tuple[int, int, float], drik.Place, float]:
    """
    Creates drik.Date, time tuple, drik.Place, and calculates Julian Day Number.
    """
    dob = drik.Date(year, month, day)
    tob = (hour, minute, second)
    place = drik.Place(place_name, latitude, longitude, timezone_offset)
    
    # Calculate Julian Day
    jd = utils.julian_day_number(dob, tob)
    
    # Set Ayanamsa if requested
    mode_key = ayanamsa_mode.upper().replace("-", "_")
    if mode_key in AYANAMSA_MAP:
        const._DEFAULT_AYANAMSA_MODE = AYANAMSA_MAP[mode_key]
        
    return dob, tob, place, jd

parse_birth_data = create_date_and_place

def format_longitude(deg: float) -> Dict[str, Any]:
    """Formats decimal longitude into Rasi, Deg, Min, Sec and Nakshatra."""
    deg = deg % 360.0
    rasi_idx = int(deg // 30)
    rasi_deg = deg % 30.0
    d = int(rasi_deg)
    m = int((rasi_deg - d) * 60)
    s = round(((rasi_deg - d) * 60 - m) * 60, 2)
    
    nak_span = 360.0 / 27.0
    nak_idx = int(deg // nak_span)
    pada = int((deg % nak_span) // (nak_span / 4.0)) + 1
    
    return {
        "total_degrees": round(deg, 4),
        "rasi_index": rasi_idx,
        "rasi_name": RASI_NAMES[rasi_idx] if rasi_idx < len(RASI_NAMES) else str(rasi_idx),
        "degrees_in_rasi": f"{d}° {m}' {s}\"",
        "nakshatra_index": nak_idx,
        "nakshatra_name": NAKSHATRA_NAMES[nak_idx] if nak_idx < len(NAKSHATRA_NAMES) else str(nak_idx),
        "pada": pada
    }

def format_rasi_degree(rasi_idx: int, deg_in_rasi: float) -> str:
    """Formats (rasi_idx, deg_in_rasi) to human-readable string."""
    d = int(deg_in_rasi)
    m = int((deg_in_rasi - d) * 60)
    s = round(((deg_in_rasi - d) * 60 - m) * 60, 2)
    r_name = RASI_NAMES[rasi_idx] if 0 <= rasi_idx < len(RASI_NAMES) else f"Rasi-{rasi_idx}"
    return f"{r_name} {d}° {m}' {s}\""
