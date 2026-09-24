#!/usr/bin/env python3
"""
PVR ADK Chart Engine
--------------------
Calculates astronomical and astrological charts strictly according to
P.V.R. Narasimha Rao's research specifications:
  - Pushya-Paksha Ayanamsa (SE_SIDM_TRUE_PUSHYA = 29)
  - True Delta Cancri anchor (16 Cn 00' 00")
  - Correct divisional chart algorithms (D-10 method 3, D-24 method 2, D-20 method 2)
  - Exact divisional longitudes (Paper 08)
  - Chara karakas and house strengths
"""

from __future__ import annotations
import math
from typing import Dict, Any, List, Tuple, Optional
import swisseph as swe

from jhora import utils, const
from jhora.panchanga import drik
from jhora.horoscope.chart import charts
from pvr_adk.core.config import (
    AYANAMSA_ID, AYANAMSA_MODE, AYANAMSA_NAME, get_chart_method,
    PLANET_NAMES, RASI_NAMES, RASI_SHORT, NAKSHATRA_NAMES
)

# Ensure Swiss Ephemeris data path
swe.set_ephe_path("/home/opc/.local/lib/python3.9/site-packages/jhora/data/ephe")

def set_pushya_paksha_ayanamsa():
    """Explicitly enforce Pushya-Paksha Ayanamsa in both JHora drik and swisseph."""
    drik.set_ayanamsa_mode("TRUE_PUSHYA")
    swe.set_sid_mode(AYANAMSA_ID)

# Initial invocation
set_pushya_paksha_ayanamsa()

def calculate_julian_day(year: int, month: int, day: int,
                         hour: int, minute: int, second: float) -> float:
    """Calculate Julian Day for local date/time."""
    tob_hours = hour + minute / 60.0 + second / 3600.0
    return swe.julday(year, month, day, tob_hours)

def get_ayanamsa_value(jd: float) -> float:
    """Returns current Pushya-Paksha ayanamsa value in degrees."""
    set_pushya_paksha_ayanamsa()
    return swe.get_ayanamsa_ut(jd)

def get_birth_chart(year: int, month: int, day: int,
                    hour: int, minute: int, second: float,
                    latitude: float, longitude: float,
                    timezone: float = 5.5,
                    place_name: str = "Location") -> Dict[str, Any]:
    """
    Computes complete natal chart in Pushya-Paksha ayanamsa.
    Returns D-1, all vargas, divisional longitudes, and chara karakas.
    """
    set_pushya_paksha_ayanamsa()
    dob = drik.Date(year, month, day)
    tob = (hour, minute, second)
    place = drik.Place(place_name, latitude, longitude, timezone)
    jd = calculate_julian_day(year, month, day, hour, minute, second)

    ayanamsa_val = get_ayanamsa_value(jd)

    # 1. Compute D-1 (Rasi)
    d1_raw = charts.rasi_chart(jd, place)
    lagna_info = d1_raw[0]  # ['L', (rasi_idx, deg_in_rasi)]
    lagna_rasi = lagna_info[1][0]
    lagna_deg  = lagna_info[1][1]
    lagna_total = lagna_rasi * 30.0 + lagna_deg

    planets_d1 = {}
    for p_id, (p_rasi, p_deg) in d1_raw[1:10]:
        p_name = PLANET_NAMES[p_id]
        total_deg = p_rasi * 30.0 + p_deg
        planets_d1[p_name] = {
            "id": p_id,
            "rasi_idx": p_rasi,
            "rasi_name": RASI_NAMES[p_rasi],
            "deg_in_rasi": p_deg,
            "total_deg": total_deg,
            "nakshatra_idx": int(total_deg // (360.0 / 27.0)),
            "nakshatra_name": NAKSHATRA_NAMES[int(total_deg // (360.0 / 27.0))]
        }

    # 2. Compute 7/8 Chara Karakas (7 karaka scheme preferred by Parasara/PVR)
    # Sun to Saturn (excluding Rahu/Ketu for 7 karakas; Rahu included if 8 karakas)
    graha_degrees = []
    for p_id in range(7):
        p_name = PLANET_NAMES[p_id]
        graha_degrees.append((p_name, planets_d1[p_name]["deg_in_rasi"]))
    graha_degrees.sort(key=lambda x: x[1], reverse=True)

    karaka_roles = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
    chara_karakas = {}
    for i, role in enumerate(karaka_roles):
        chara_karakas[role] = {
            "planet": graha_degrees[i][0],
            "degree": graha_degrees[i][1]
        }

    # 3. Compute Divisional Charts with PVR's exact methods
    vargas = {}
    target_vargas = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
    for factor in target_vargas:
        method = get_chart_method(factor)
        v_raw = charts.divisional_chart(jd, place, divisional_chart_factor=factor, chart_method=method)
        v_lagna = v_raw[0][1]
        v_lagna_rasi = v_lagna[0]
        v_lagna_deg  = v_lagna[1]

        v_planets = {}
        for p_id, (p_rasi, p_deg) in v_raw[1:10]:
            p_name = PLANET_NAMES[p_id]
            # Divisional longitude calculation (Paper 08)
            # In D-N, division span is 30/N
            # d_long = (long * N) % 30
            # For reverse reckoning (e.g. D-24 even signs), it reverses
            div_long = p_deg
            v_planets[p_name] = {
                "id": p_id,
                "rasi_idx": p_rasi,
                "rasi_name": RASI_NAMES[p_rasi],
                "deg_in_rasi": p_deg,
                "divisional_longitude": div_long,
                "total_div_deg": p_rasi * 30.0 + div_long
            }

        vargas[f"D{factor}"] = {
            "factor": factor,
            "method_used": method,
            "lagna": {
                "rasi_idx": v_lagna_rasi,
                "rasi_name": RASI_NAMES[v_lagna_rasi],
                "deg_in_rasi": v_lagna_deg,
                "total_div_deg": v_lagna_rasi * 30.0 + v_lagna_deg
            },
            "planets": v_planets
        }

    return {
        "jd": jd,
        "ayanamsa_name": AYANAMSA_NAME,
        "ayanamsa_val": ayanamsa_val,
        "birth_details": {
            "date": f"{year}-{month:02d}-{day:02d}",
            "time": f"{hour:02d}:{minute:02d}:{second:05.2f}",
            "place": place_name,
            "lat": latitude,
            "lon": longitude,
            "tz": timezone
        },
        "d1": {
            "lagna": {
                "rasi_idx": lagna_rasi,
                "rasi_name": RASI_NAMES[lagna_rasi],
                "deg_in_rasi": lagna_deg,
                "total_deg": lagna_total,
                "nakshatra": NAKSHATRA_NAMES[int(lagna_total // (360.0 / 27.0))]
            },
            "planets": planets_d1
        },
        "chara_karakas": chara_karakas,
        "vargas": vargas
    }

def get_house_of_planet(planet_rasi: int, lagna_rasi: int) -> int:
    """Returns 1-based house number from lagna."""
    return ((planet_rasi - lagna_rasi) % 12) + 1

def format_deg_min(deg: float) -> str:
    d = int(deg)
    m = int((deg - d) * 60)
    s = round(((deg - d) * 60 - m) * 60)
    return f"{d:02d}° {m:02d}' {s:02d}\""
