#!/usr/bin/env python3
"""
PyJHora MCP Server 3: Planetary Strengths, Bhava Bala & Ashtakavarga (mcp_strengths_ashtakavarga.py)
Provides comprehensive Shadbala (6-fold strength), Vimsopaka Bala, Harsha Bala, Bhava Bala,
Bhinna & Sarva Ashtakavarga matrices, Trikona/Ekadhipatya Shodhana, and Shodhaya Pindas.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
import numpy as np
from mcp_base import MCPServer
from jhora_helpers import (
    create_date_and_place,
    format_rasi_degree,
    PLANET_NAMES,
    RASI_NAMES
)
from jhora.horoscope.chart import strength, ashtakavarga, charts, house
from jhora.panchanga import drik
from jhora import utils, const

server = MCPServer(name="mcp-jhora-strengths-ashtakavarga", version="1.0.0")

LOCATION_PARAMS = {
    "year": {"type": "integer", "description": "Year of birth (e.g. 2000)"},
    "month": {"type": "integer", "description": "Month of birth (1-12)"},
    "day": {"type": "integer", "description": "Day of birth (1-31)"},
    "hour": {"type": "integer", "description": "Hour of birth (0-23)", "default": 12},
    "minute": {"type": "integer", "description": "Minute of birth (0-59)", "default": 0},
    "second": {"type": "number", "description": "Second of birth (0-59.99)", "default": 0.0},
    "latitude": {"type": "number", "description": "Birth latitude in decimal degrees", "default": 13.0827},
    "longitude": {"type": "number", "description": "Birth longitude in decimal degrees", "default": 80.2707},
    "timezone_offset": {"type": "number", "description": "Timezone offset from UTC in hours (e.g. 5.5 for IST)", "default": 5.5},
    "place_name": {"type": "string", "description": "City/Location name", "default": "Location"},
    "ayanamsa_mode": {"type": "string", "description": "Ayanamsa mode (LAHIRI, PUSHYA_PAKSHA, RAMAN, KP)", "default": "LAHIRI"}
}

def _get_h_list(chart_d1):
    h_list = ['' for _ in range(12)]
    for p, (r, deg) in chart_d1:
        if p in ['L', 0, 1, 2, 3, 4, 5, 6, 7, 8]:
            p_str = str(p)
            if h_list[r] == '':
                h_list[r] = p_str
            else:
                h_list[r] += '/' + p_str
    return h_list

@server.tool(
    name="get_shadbala_breakdown",
    description="Calculate complete 6-fold Shadbala breakdown for 7 classical planets (Sun to Saturn), including Sthana, Dig, Kala, Chesta, Naisargika, Drik Balas, total Virupas, Rupas, required thresholds, percentage strengths, and relative ranks.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_shadbala_breakdown(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI"
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    # strength.shad_bala(jd, place) returns a list of 9 arrays
    sb = strength.shad_bala(jd, place)
    
    thresholds = [6.5, 6.0, 5.0, 7.0, 6.5, 5.5, 5.0] # Sun to Saturn minimum Rupas
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    planet_details = {}
    ranks = []
    
    for i, p_name in enumerate(planets):
        sthana = float(sb[0][i])
        dig = float(sb[1][i])
        kala = float(sb[2][i])
        chesta = float(sb[3][i])
        naisargika = float(sb[4][i])
        drik_val = float(sb[5][i])
        total_shashtiamsas = float(sb[6][i])
        total_rupas = float(sb[7][i])
        ratio = float(sb[8][i])
        req_rupas = thresholds[i]
        is_strong = total_rupas >= req_rupas
        
        ranks.append((p_name, total_rupas))
        
        planet_details[p_name] = {
            "sthana_bala_shashtiamsas": round(sthana, 2),
            "dig_bala_shashtiamsas": round(dig, 2),
            "kala_bala_shashtiamsas": round(kala, 2),
            "chesta_bala_shashtiamsas": round(chesta, 2),
            "naisargika_bala_shashtiamsas": round(naisargika, 2),
            "drik_bala_shashtiamsas": round(drik_val, 2),
            "total_virupas_shashtiamsas": round(total_shashtiamsas, 2),
            "total_rupas": round(total_rupas, 2),
            "required_minimum_rupas": req_rupas,
            "strength_ratio_percent": round(ratio * 100.0, 1),
            "is_strength_sufficient": is_strong
        }
        
    ranks.sort(key=lambda x: x[1], reverse=True)
    ranked_order = [f"{rank+1}. {name} ({round(val, 2)} Rupas)" for rank, (name, val) in enumerate(ranks)]
    
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "shadbala_summary": {
            "planet_details": planet_details,
            "relative_strength_ranking": ranked_order
        }
    }

@server.tool(
    name="get_vimsopaka_and_vargeeya_bala",
    description="Calculate Panchavargeeya Bala (5-varga), Dwadasavargeeya Bala (12-varga), Harsha Bala, and Ishta/Kashta Phala for the planets.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_vimsopaka_and_vargeeya_bala(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI"
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    try:
        pv = strength.pancha_vargeeya_bala(jd, place)
    except Exception:
        pv = [0.0] * 7
        
    try:
        dv = strength.dwadhasa_vargeeya_bala(jd, place)
    except Exception:
        dv = [0.0] * 7
        
    try:
        hb = strength.harsha_bala(dob, tob, place)
    except Exception:
        hb = [0.0] * 7
        
    try:
        ip = strength._ishta_phala(jd, place)
    except Exception:
        ip = [0.0] * 7
        
    res = {}
    for i, p in enumerate(planets):
        pv_val = round(float(pv[i]), 2) if i < len(pv) else 0.0
        dv_val = round(float(dv[i]), 2) if i < len(dv) else 0.0
        hb_val = round(float(hb[i]), 2) if i < len(hb) else 0.0
        ishta_val = round(float(ip[i]), 2) if i < len(ip) else 0.0
        kashta_val = round(60.0 - ishta_val, 2) if ishta_val > 0 else 0.0
        
        res[p] = {
            "pancha_vargeeya_bala_points_max_20": pv_val,
            "dwadasa_vargeeya_bala_points_max_20": dv_val,
            "harsha_bala_points_max_20": hb_val,
            "ishta_phala_virupas_max_60": ishta_val,
            "kashta_phala_virupas_max_60": kashta_val
        }
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "planetary_vimsopaka_and_vargeeya_balas": res
    }

@server.tool(
    name="get_bhava_bala",
    description="Calculate Bhava Bala (strength of all 12 houses) including Bhava Adhipati Bala, Bhava Dig Bala, Bhava Drishti Bala, and Total Bhava Bala in Rupas with rankings.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_bhava_bala(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI"
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    # strength.bhava_bala(jd, place) returns [virupas_list, rupas_list, ratio_list]
    bb = strength.bhava_bala(jd, place)
    bb_virupas = bb[0] if len(bb) > 0 else [0.0]*12
    bb_rupas = bb[1] if len(bb) > 1 else [0.0]*12
    bb_ratio = bb[2] if len(bb) > 2 else [1.0]*12
    
    try:
        adhipati = strength._bhava_adhipathi_bala(jd, place)
    except Exception:
        adhipati = [0.0] * 12
        
    try:
        dig = strength._bhava_dig_bala(jd, place)
    except Exception:
        dig = [0.0] * 12
        
    try:
        drik_b = strength._bhava_drik_bala(jd, place)
    except Exception:
        drik_b = [0.0] * 12
        
    houses_data = {}
    ranked = []
    
    for h in range(12):
        house_num = h + 1
        tot_virupa = float(bb_virupas[h]) if h < len(bb_virupas) else 0.0
        tot_rupa = float(bb_rupas[h]) if h < len(bb_rupas) else 0.0
        adh = float(adhipati[h]) if h < len(adhipati) else 0.0
        dg = float(dig[h]) if h < len(dig) else 0.0
        dr = float(drik_b[h]) if h < len(drik_b) else 0.0
        
        ranked.append((house_num, tot_rupa))
        
        houses_data[f"house_{house_num}"] = {
            "house_number": house_num,
            "adhipati_bala_shashtiamsas": round(adh, 2),
            "dig_bala_shashtiamsas": round(dg, 2),
            "drishti_bala_shashtiamsas": round(dr, 2),
            "total_bhava_virupas": round(tot_virupa, 2),
            "total_bhava_bala_rupas": round(tot_rupa, 2)
        }
        
    ranked.sort(key=lambda x: x[1], reverse=True)
    ranked_summary = [f"Rank {r+1}: House {h_num} ({round(v, 2)} Rupas)" for r, (h_num, v) in enumerate(ranked)]
    
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "bhava_bala_results": {
            "houses": houses_data,
            "house_strength_ranking": ranked_summary
        }
    }

@server.tool(
    name="get_ashtakavarga_matrices",
    description="Calculate complete Ashtakavarga matrices including 8 Bhinna Ashtakavarga (BAV) tables (Sun to Saturn + Lagna across 12 signs) and Sarvashtakavarga (SAV) total bindus (summing to 337).",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_ashtakavarga_matrices(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI"
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    chart_d1 = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    h_list = _get_h_list(chart_d1)
    
    bav, sav, pav = ashtakavarga.get_ashtaka_varga(h_list)
    
    planets_8 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]
    
    bav_dict = {}
    for p_idx, p_name in enumerate(planets_8):
        points = bav[p_idx]
        bav_dict[p_name] = {
            "total_bindus": sum(points),
            "by_rasi": {RASI_NAMES[r]: points[r] for r in range(12)}
        }
        
    sav_by_rasi = {RASI_NAMES[r]: sav[r] for r in range(12)}
    
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "sarvashtakavarga": {
            "total_bindus": sum(sav),
            "ideal_standard_sum": 337,
            "sav_by_rasi": sav_by_rasi
        },
        "bhinna_ashtakavarga": bav_dict
    }

@server.tool(
    name="get_shodhaya_pindas_and_reductions",
    description="Perform Trikona Shodhana (triplicity reduction) and Ekadhipatya Shodhana (single lordship reduction) on Ashtakavarga, and calculate Rasi Pinda, Graha Pinda, and Shodhaya Pinda for 7 planets.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_shodhaya_pindas_and_reductions(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI"
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    chart_d1 = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    h_list = _get_h_list(chart_d1)
    
    bav, sav, pav = ashtakavarga.get_ashtaka_varga(h_list)
    
    trikona = ashtakavarga._trikona_sodhana(bav)
    ekadhipatya = ashtakavarga._ekadhipatya_sodhana(trikona, h_list)
    raasi_pindas, graha_pindas, sodhya_pindas = ashtakavarga.sodhaya_pindas(bav, h_list)
    
    planets_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    pindas_result = {}
    for i, p_name in enumerate(planets_7):
        pindas_result[p_name] = {
            "rasi_pinda": int(raasi_pindas[i]),
            "graha_pinda": int(graha_pindas[i]),
            "shodhaya_pinda_total": int(sodhya_pindas[i])
        }
        
    sodhita_ashtakavarga = {}
    for i, p_name in enumerate(planets_7):
        sodhita_ashtakavarga[p_name] = {
            "trikona_shodhana_reduction": {RASI_NAMES[r]: trikona[i][r] for r in range(12)},
            "ekadhipatya_shodhana_sodhita": {RASI_NAMES[r]: ekadhipatya[i][r] for r in range(12)}
        }
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "shodhaya_pindas": pindas_result,
        "sodhita_ashtakavarga_matrices": sodhita_ashtakavarga
    }

if __name__ == "__main__":
    server.run()
