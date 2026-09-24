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

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

NAKSHATRA_NAMES = [
    'Ashwini', 'Bharani', 'Krittika', 'Rohini', 'Mrigashira', 'Ardra',
    'Punarvasu', 'Pushya', 'Ashlesha', 'Magha', 'Purva Phalguni', 'Uttara Phalguni',
    'Hasta', 'Chitra', 'Swati', 'Vishakha', 'Anuradha', 'Jyeshtha',
    'Mula', 'Purva Ashadha', 'Uttara Ashadha', 'Shravana', 'Dhanishta', 'Shatabhisha',
    'Purva Bhadrapada', 'Uttara Bhadrapada', 'Revati'
]

AYANAMSA_MAP = {
    "LAHIRI": "LAHIRI",
    "TRUE_CITRA": "TRUE_CITRA",
    "TRUE_LAHIRI": "TRUE_LAHIRI",
    "PUSHYA_PAKSHA": "TRUE_PUSHYA",
    "PUSHYAPAKSHA": "TRUE_PUSHYA",
    "TRUE_PUSHYA": "TRUE_PUSHYA",
    "RAMAN": "RAMAN",
    "BVRAMAN": "RAMAN",
    "KP": "KP",
    "KRISHNAMURTHY": "KP",
    "KRISHNAMURTI": "KP",
    "YUKTESHWAR": "YUKTESHWAR",
    "FAGAN": "FAGAN"
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
    
    # Set Ayanamsa if requested
    mode_key = ayanamsa_mode.upper().replace("-", "_")
    mapped_mode = AYANAMSA_MAP.get(mode_key, "LAHIRI")
    drik.set_ayanamsa_mode(mapped_mode)
    
    # Calculate Julian Day
    jd = utils.julian_day_number(dob, tob)
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

# Sign lords: 0=Aries (Mars), 1=Taurus (Venus), ..., 11=Pisces (Jupiter)
SIGN_LORDS = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]

# Planetary Speeds (mean degrees per day for Tajaka aspect resolution)
PLANET_MEAN_SPEEDS = {
    "Moon": 13.176, "Mercury": 1.383, "Venus": 1.200, "Sun": 0.9856,
    "Mars": 0.524, "Jupiter": 0.083, "Saturn": 0.033, "Rahu": -0.053, "Ketu": -0.053
}

# Deeptamsha Orbs (Maximum orb in degrees for Tajaka aspects/Ithasala yogas)
DEEPTAMSHA_ORBS = {
    "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
    "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0, "Rahu": 6.0, "Ketu": 6.0
}

# Planetary Dignities
EXALTATION_SIGNS = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 1, "Ketu": 7}
MOOLATRIKONA_SIGNS = {"Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5, "Jupiter": 8, "Venus": 6, "Saturn": 10, "Rahu": 5, "Ketu": 11}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10], "Rahu": [10], "Ketu": [7]
}
DEBILITATION_SIGNS = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0, "Rahu": 7, "Ketu": 1}

def get_planet_dignity(planet: str, sign_idx: int, is_retrograde: bool = False) -> str:
    """Calculates planetary dignity in a sign with retrograde cancellation consideration."""
    if sign_idx == EXALTATION_SIGNS.get(planet):
        return "Exalted (Paramoccha)"
    if sign_idx == MOOLATRIKONA_SIGNS.get(planet):
        return "Moolatrikona"
    if sign_idx in OWN_SIGNS.get(planet, []):
        return "Own Sign (Swakshetra)"
    if sign_idx == DEBILITATION_SIGNS.get(planet):
        if is_retrograde:
            return "Debilitated (Neecha Bhanga via Retrograde)"
        return "Debilitated (Neecha)"
    return "Neutral / Friendly"

def get_pvr_divisional_position(rasi_idx: int, deg_in_rasi: float, varga_factor: int, method: str = "pvr") -> Tuple[int, float]:
    """
    Computes (varga_sign_index, deg_in_varga) for any divisional chart (D-1 to D-60)
    incorporating P.V.R. Narasimha Rao's reformed research formulas.
    """
    span = 30.0 / float(varga_factor)
    k = int(deg_in_rasi // span)
    if k >= varga_factor:
        k = varga_factor - 1
    deg_in_varga = (deg_in_rasi - (k * span)) * float(varga_factor)

    if varga_factor == 1:
        v_sign = rasi_idx
    elif varga_factor == 2:  # Hora
        if rasi_idx % 2 == 0:  # Odd sign: 0-15 Sun (Leo=4), 15-30 Moon (Cancer=3)
            v_sign = 4 if k == 0 else 3
        else:  # Even sign: 0-15 Moon (Cancer=3), 15-30 Sun (Leo=4)
            v_sign = 3 if k == 0 else 4
    elif varga_factor == 3:  # Drekkana
        v_sign = (rasi_idx + 4 * k) % 12
    elif varga_factor == 4:  # Chaturthamsa
        v_sign = (rasi_idx + 3 * k) % 12
    elif varga_factor == 7:  # Saptamsa
        if rasi_idx % 2 == 0:
            v_sign = (rasi_idx + k) % 12
        else:
            v_sign = (rasi_idx + 6 + k) % 12
    elif varga_factor == 9:  # Navamsa
        elem = rasi_idx % 4
        start = 0 if elem == 0 else (9 if elem == 1 else (6 if elem == 2 else 3))
        v_sign = (start + k) % 12
    elif varga_factor == 10:  # Dasamsa
        if method == "pvr":
            if rasi_idx % 2 == 0:
                v_sign = (rasi_idx + k) % 12
            else:  # Even sign: reverse from 9th (PVR Method 3)
                v_sign = ((rasi_idx + 8) - k) % 12
        else:
            v_sign = (rasi_idx + k) if rasi_idx % 2 == 0 else (rasi_idx + 8 + k) % 12
    elif varga_factor == 12:  # Dwadasamsa
        v_sign = (rasi_idx + k) % 12
    elif varga_factor == 16:  # Shodasamsa
        m = rasi_idx % 3
        start = 0 if m == 0 else (4 if m == 1 else 8)
        if method == "pvr":
            v_sign = (start + k) % 12 if rasi_idx % 2 == 0 else (start + 15 - k) % 12
        else:
            v_sign = (start + k) % 12
    elif varga_factor == 20:  # Vimsamsa
        m = rasi_idx % 3
        start = 0 if m == 0 else (8 if m == 1 else 4)
        v_sign = (start + k) % 12
    elif varga_factor == 24:  # Siddhamsa
        if method == "pvr":
            v_sign = (4 + k) % 12 if rasi_idx % 2 == 0 else (3 - k) % 12
        else:
            v_sign = (4 + k) % 12 if rasi_idx % 2 == 0 else (3 + k) % 12
    elif varga_factor == 27:  # Nakshatramsa / Bhamsa
        elem = rasi_idx % 4
        start = 0 if elem == 0 else (3 if elem == 1 else (6 if elem == 2 else 9))
        v_sign = (start + k) % 12
    elif varga_factor == 30:  # Trimsamsa
        if rasi_idx % 2 == 0:  # Odd: Mars(5), Sat(5), Jup(8), Merc(7), Ven(5)
            if deg_in_rasi < 5.0: v_sign = 0
            elif deg_in_rasi < 10.0: v_sign = 10
            elif deg_in_rasi < 18.0: v_sign = 8
            elif deg_in_rasi < 25.0: v_sign = 2
            else: v_sign = 6
        else:  # Even: Ven(5), Merc(7), Jup(8), Sat(5), Mars(5)
            if deg_in_rasi < 5.0: v_sign = 1
            elif deg_in_rasi < 12.0: v_sign = 5
            elif deg_in_rasi < 20.0: v_sign = 11
            elif deg_in_rasi < 25.0: v_sign = 9
            else: v_sign = 7
    elif varga_factor == 40:  # Khavedamsa
        start = 0 if rasi_idx % 2 == 0 else 6
        v_sign = (start + k) % 12
    elif varga_factor == 45:  # Akshavedamsa
        m = rasi_idx % 3
        start = 0 if m == 0 else (4 if m == 1 else 8)
        v_sign = (start + k) % 12
    elif varga_factor == 60:  # Shashtiamsa
        if method == "pvr":
            v_sign = (rasi_idx + k) % 12 if rasi_idx % 2 == 0 else ((rasi_idx + 6) - k) % 12
        else:
            v_sign = (rasi_idx + k) % 12
    else:
        v_sign = (rasi_idx + k) % 12

    return v_sign % 12, deg_in_varga

def calculate_chart_vision(
    lagna_rasi: int,
    lagna_deg: float,
    planets_data: Dict[str, Dict[str, Any]],
    chart_name: str = "Chart"
) -> Dict[str, Any]:
    """
    Generates an exhaustive, high-resolution structural vision for any chart
    (D-1 to D-60, Tajaka Varshaphal, or Tithi Pravesha) specifically structured
    for LLM comprehension:
      - 12 Houses: sign, lord, lord's dignity, lord's house, and all occupant planets
      - All 12 House Lords' exact status & dignity
      - Graha Drishti (Full Planetary Aspects)
      - Rasi Drishti (Jaimini Sign Aspects)
      - Kendra-Trikona Raja Yogas, Dhana Yogas, Parivartanas, and Samasaptakas
    """
    lagna_sign_name = RASI_NAMES[lagna_rasi]
    
    # 1. House Occupants & Placements
    house_occupants = {h: [] for h in range(1, 13)}
    planet_house_map = {}
    planet_sign_map = {}
    planet_dignity_map = {}

    for p_name, p_info in planets_data.items():
        if p_name in ["Lagna", "L"]:
            continue
        p_rasi = p_info.get("rasi_index", p_info.get("rasi_idx", 0))
        p_deg = p_info.get("deg_in_rasi", 0.0)
        is_retro = p_info.get("is_retrograde", False)
        h_no = ((p_rasi - lagna_rasi + 12) % 12) + 1
        dignity = get_planet_dignity(p_name, p_rasi, is_retro)

        planet_house_map[p_name] = h_no
        planet_sign_map[p_name] = p_rasi
        planet_dignity_map[p_name] = dignity

        house_occupants[h_no].append({
            "planet": p_name,
            "sign": RASI_NAMES[p_rasi],
            "degree": round(p_deg, 2) if isinstance(p_deg, (int, float)) else str(p_deg),
            "dignity": dignity,
            "is_retrograde": is_retro
        })

    # 2. 12 House Lords Summary
    house_lords = {}
    for h in range(1, 13):
        h_sign_idx = (lagna_rasi + h - 1) % 12
        h_sign_name = RASI_NAMES[h_sign_idx]
        lord_id = SIGN_LORDS[h_sign_idx]
        lord_name = PLANET_NAMES[lord_id]
        
        lord_house = planet_house_map.get(lord_name, "Unknown")
        lord_sign_idx = planet_sign_map.get(lord_name, 0)
        lord_dignity = planet_dignity_map.get(lord_name, "Unknown")
        
        house_lords[f"House_{h}"] = {
            "house_number": h,
            "sign": h_sign_name,
            "lord": lord_name,
            "lord_occupied_house": lord_house,
            "lord_occupied_sign": RASI_NAMES[lord_sign_idx] if lord_name in planet_sign_map else "Unknown",
            "lord_dignity": lord_dignity,
            "occupants": house_occupants[h]
        }

    # 3. Graha Drishti (Planetary Aspects)
    graha_aspects = {}
    for p_name, p_house in planet_house_map.items():
        aspected_houses = []
        # Base 7th house aspect for all planets
        aspected_houses.append(((p_house + 6 - 1) % 12) + 1)
        # Special aspects
        if p_name == "Mars":
            aspected_houses.extend([((p_house + 3 - 1) % 12) + 1, ((p_house + 7 - 1) % 12) + 1])
        elif p_name == "Jupiter" or p_name in ["Rahu", "Ketu"]:
            aspected_houses.extend([((p_house + 4 - 1) % 12) + 1, ((p_house + 8 - 1) % 12) + 1])
        elif p_name == "Saturn":
            aspected_houses.extend([((p_house + 2 - 1) % 12) + 1, ((p_house + 9 - 1) % 12) + 1])

        aspected_houses = sorted(list(set(aspected_houses)))
        aspected_planets = []
        for ah in aspected_houses:
            for occ in house_occupants[ah]:
                aspected_planets.append(f"{occ['planet']} (in House {ah})")

        graha_aspects[p_name] = {
            "planet_in_house": p_house,
            "aspected_houses": aspected_houses,
            "aspected_planets": aspected_planets
        }

    # 4. Rasi Drishti (Jaimini Sign Aspects)
    # Movable (0,3,6,9) aspects Fixed (1,4,7,10) except adjacent.
    # Fixed (1,4,7,10) aspects Movable (0,3,6,9) except adjacent.
    # Dual (2,5,8,11) aspects all other Dual.
    rasi_aspects = {}
    for s_idx in range(12):
        s_name = RASI_NAMES[s_idx]
        elem_mode = s_idx % 3  # 0=Movable, 1=Fixed, 2=Dual
        aspected_signs = []
        if elem_mode == 0:  # Movable -> Fixed except next
            adj_fixed = (s_idx + 1) % 12
            for f_sign in [1, 4, 7, 10]:
                if f_sign != adj_fixed:
                    aspected_signs.append(RASI_NAMES[f_sign])
        elif elem_mode == 1:  # Fixed -> Movable except previous
            adj_movable = (s_idx - 1) % 12
            for m_sign in [0, 3, 6, 9]:
                if m_sign != adj_movable:
                    aspected_signs.append(RASI_NAMES[m_sign])
        else:  # Dual -> All other Dual
            for d_sign in [2, 5, 8, 11]:
                if d_sign != s_idx:
                    aspected_signs.append(RASI_NAMES[d_sign])

        rasi_aspects[s_name] = aspected_signs

    # 5. Raja Yogas & Dhana Yogas
    kendra_lords = {SIGN_LORDS[(lagna_rasi + k - 1) % 12]: k for k in [1, 4, 7, 10]}
    trikona_lords = {SIGN_LORDS[(lagna_rasi + t - 1) % 12]: t for t in [1, 5, 9]}
    raja_yogas = []
    
    for k_p_id, k_h in kendra_lords.items():
        for t_p_id, t_h in trikona_lords.items():
            if k_p_id != t_p_id:
                p1 = PLANET_NAMES[k_p_id]
                p2 = PLANET_NAMES[t_p_id]
                if p1 in planet_house_map and p2 in planet_house_map:
                    if planet_house_map[p1] == planet_house_map[p2]:
                        h_conj = planet_house_map[p1]
                        raja_yogas.append({
                            "type": "Kendra-Trikona Raja Yoga",
                            "planets": f"{p1} (Lord of {k_h}) + {p2} (Lord of {t_h})",
                            "conjunction_house": h_conj,
                            "conjunction_sign": RASI_NAMES[(lagna_rasi + h_conj - 1) % 12]
                        })

    # 6. Parivartana Yogas (Mutual Exchanges)
    parivartanas = []
    for h1 in range(1, 13):
        for h2 in range(h1 + 1, 13):
            l1_id = SIGN_LORDS[(lagna_rasi + h1 - 1) % 12]
            l2_id = SIGN_LORDS[(lagna_rasi + h2 - 1) % 12]
            p1 = PLANET_NAMES[l1_id]
            p2 = PLANET_NAMES[l2_id]
            if p1 in planet_house_map and p2 in planet_house_map:
                if planet_house_map[p1] == h2 and planet_house_map[p2] == h1:
                    is_maha = (h1 in [1, 2, 4, 5, 7, 9, 10, 11] and h2 in [1, 2, 4, 5, 7, 9, 10, 11])
                    parivartanas.append({
                        "exchange": f"{h1}th Lord {p1} in House {h2} <-> {h2}th Lord {p2} in House {h1}",
                        "houses": (h1, h2),
                        "yoga_category": "Maha Parivartana Yoga (Highly Auspicious)" if is_maha else "Dainya / Khala Parivartana"
                    })

    # 7. Samasaptaka (180° Direct Mutual Aspects)
    samasaptakas = []
    p_names = list(planet_house_map.keys())
    for i in range(len(p_names)):
        for j in range(i + 1, len(p_names)):
            p1, p2 = p_names[i], p_names[j]
            h1, h2 = planet_house_map[p1], planet_house_map[p2]
            if (h1 - h2) % 12 == 6:
                samasaptakas.append({
                    "planets": f"{p1} (House {h1}) <-> {p2} (House {h2})",
                    "signs": f"{RASI_NAMES[planet_sign_map[p1]]} <-> {RASI_NAMES[planet_sign_map[p2]]}"
                })

    return {
        "chart_name": chart_name,
        "lagna_sign": lagna_sign_name,
        "lagna_degree": round(lagna_deg, 2) if isinstance(lagna_deg, (int, float)) else str(lagna_deg),
        "houses_and_lords": house_lords,
        "graha_aspects": graha_aspects,
        "rasi_aspects": rasi_aspects,
        "raja_yogas": raja_yogas,
        "parivartanas": parivartanas,
        "samasaptakas": samasaptakas
    }

