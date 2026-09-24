#!/usr/bin/env python3
"""
PyJHora MCP Server 5: Vedic Yogas, Doshas & Sensitive Sphutas (mcp_yogas_doshas.py)
Provides comprehensive Vedic Yoga detection (Pancha Mahapurusha, Raja Yogas, Dhana Yogas,
Nabhasa Yogas), Dosha diagnostics (Manglik with cancellations, Kala Sarpa 12 types, Pitru,
Guru Chandal, Shrapit), and mathematical Vedic Sphutas (Bija, Kshetra, Yogi, Tithi, Prana/Deha/Mrityu).
"""
from __future__ import annotations
import re
from typing import Dict, Any, List, Optional
from mcp_base import MCPServer
from jhora_helpers import (
    create_date_and_place,
    format_longitude,
    format_rasi_degree,
    PLANET_NAMES,
    RASI_NAMES
)
from jhora.horoscope.chart import yoga, raja_yoga, dosha, sphuta, charts
from jhora.panchanga import drik
from jhora import utils, const

server = MCPServer(name="mcp-jhora-yogas-doshas", version="1.0.0")

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

def _clean_text(html_or_text: str) -> str:
    """Strips HTML tags and normalizes whitespace."""
    if not isinstance(html_or_text, str):
        return str(html_or_text)
    clean = re.sub(r'<[^<]+?>', ' ', html_or_text)
    clean = clean.replace('\\n', '\n').replace('\t', ' ')
    clean = re.sub(r'[ ]+', ' ', clean).strip()
    return clean

@server.tool(
    name="detect_all_yogas",
    description="Scan and identify all classical Parasara and BV Raman Yogas (Pancha Mahapurusha, Dhana Yogas, Nabhasa Yogas, Sun/Moon Yogas, Raja Yogas) formed in the birth chart or a specific divisional chart.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "divisional_chart_factor": {
                "type": "integer",
                "description": "Varga factor: 1 (Rasi D-1), 9 (Navamsa D-9), 10 (Dasamsa D-10), etc. Set to 0 to scan all vargas.",
                "default": 1
            }
        },
        "required": ["year", "month", "day"]
    }
)
def detect_all_yogas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    divisional_chart_factor: int = 1,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    if divisional_chart_factor == 0:
        y_res = yoga.get_yoga_details_for_all_charts(jd, place)
    else:
        y_res = yoga.get_yoga_details(jd, place, divisional_chart_factor=divisional_chart_factor)
        
    y_dict = y_res[0] if isinstance(y_res, tuple) and len(y_res) > 0 else y_res
    
    detected_yogas = []
    for yoga_id, details in y_dict.items():
        varga = details[0] if len(details) > 0 else "D1"
        title = details[1] if len(details) > 1 else yoga_id
        condition = details[2] if len(details) > 2 else ""
        effects = details[3] if len(details) > 3 else ""
        
        detected_yogas.append({
            "yoga_id": yoga_id,
            "yoga_name": title,
            "chart_varga": varga,
            "forming_condition": _clean_text(condition),
            "astrological_effects": _clean_text(effects)
        })
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "divisional_chart_factor": divisional_chart_factor if divisional_chart_factor != 0 else "ALL_VARGAS",
        "total_yogas_detected": len(detected_yogas),
        "detected_yogas": detected_yogas
    }

@server.tool(
    name="detect_raja_yogas",
    description="Detect and analyze Raja Yogas including Dharma-Karmadhipati Raja Yoga (9th-10th lords), Kendra-Trikona lord combinations, Vipareeta Raja Yogas, and Neecha Bhanga Raja Yogas.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "divisional_chart_factor": {
                "type": "integer",
                "description": "Varga factor: 1 (Rasi D-1), 9 (Navamsa D-9), 10 (Dasamsa D-10), etc.",
                "default": 1
            }
        },
        "required": ["year", "month", "day"]
    }
)
def detect_raja_yogas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    divisional_chart_factor: int = 1,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    ry_res = raja_yoga.get_raja_yoga_details(jd, place, divisional_chart_factor=divisional_chart_factor)
    ry_dict = ry_res[0] if isinstance(ry_res, tuple) and len(ry_res) > 0 else ry_res
    
    raja_yogas_list = []
    for ry_id, details in ry_dict.items():
        forming_pairs = details[0] if len(details) > 0 else ""
        name = details[1] if len(details) > 1 else ry_id
        condition = details[2] if len(details) > 2 else ""
        effects = details[3] if len(details) > 3 else ""
        
        raja_yogas_list.append({
            "raja_yoga_id": ry_id,
            "raja_yoga_name": name,
            "participating_planet_pairs": _clean_text(forming_pairs),
            "forming_rule": _clean_text(condition),
            "effects_and_results": _clean_text(effects)
        })
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "divisional_chart_factor": divisional_chart_factor,
        "total_raja_yogas_found": len(raja_yogas_list),
        "raja_yogas": raja_yogas_list
    }

@server.tool(
    name="detect_doshas",
    description="Comprehensive evaluation of 8 major Vedic Astrological Doshas: Manglik (Kuja Dosha with cancellations), Kala Sarpa (12 types), Pitru Dosha, Guru Chandala, Ganda Moola, Kalathra, Ghata, and Shrapit Doshas.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def detect_doshas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    raw_doshas = dosha.get_dosha_details(jd, place)
    
    analyzed_doshas = {}
    active_doshas_summary = []
    
    for d_name, desc_html in raw_doshas.items():
        clean_desc = _clean_text(desc_html)
        
        # Determine if dosha is actively present or cancelled/absent
        is_absent = (
            "there is no" in clean_desc.lower() or
            "is not present" in clean_desc.lower() or
            "is ineffective" in clean_desc.lower() or
            "reduces effects" in clean_desc.lower() or
            "no dosha" in clean_desc.lower()
        )
        is_present = not is_absent
        
        if is_present:
            active_doshas_summary.append(d_name)
            
        analyzed_doshas[d_name] = {
            "is_present": is_present,
            "status": "Active / Present" if is_present else "Absent / Cancelled",
            "detailed_analysis": clean_desc
        }
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "active_doshas_count": len(active_doshas_summary),
        "active_doshas_list": active_doshas_summary,
        "dosha_diagnostics": analyzed_doshas
    }

@server.tool(
    name="get_sphutas_and_sensitive_points",
    description="Calculate mathematical Vedic Sphutas and sensitive chart points: Bija Sphuta (male vitality), Kshetra Sphuta (female fertility), Santhana Sphuta, Yogi & Avayogi Sphutas, Tithi Sphuta, Prana, Deha, Mrityu, and Tri-Sphutas.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "divisional_chart_factor": {
                "type": "integer",
                "description": "Varga factor for sphuta calculation (default: 1 for Rasi)",
                "default": 1
            }
        },
        "required": ["year", "month", "day"]
    }
)
def get_sphutas_and_sensitive_points(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    divisional_chart_factor: int = 1,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    def _calc_sphuta_item(calc_fn):
        try:
            r_idx, deg = calc_fn(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
            total_deg = r_idx * 30.0 + deg
            fmt = format_longitude(total_deg)
            return {
                "longitude_degrees": round(total_deg, 4),
                "rasi": fmt["rasi_name"],
                "degrees_in_rasi": fmt["degrees_in_rasi"],
                "nakshatra": fmt["nakshatra_name"],
                "pada": fmt["pada"]
            }
        except Exception as e:
            return {"error": str(e)}
            
    sphutas_dict = {
        "beeja_sphuta_male_vitality": _calc_sphuta_item(sphuta.beeja_sphuta),
        "kshetra_sphuta_female_fertility": _calc_sphuta_item(sphuta.kshetra_sphuta),
        "yogi_sphuta_prosperity_point": _calc_sphuta_item(sphuta.yogi_sphuta),
        "avayogi_sphuta_obstacle_point": _calc_sphuta_item(sphuta.avayogi_sphuta),
        "tithi_sphuta": _calc_sphuta_item(sphuta.tithi_sphuta),
        "prana_sphuta_life_breath": _calc_sphuta_item(sphuta.prana_sphuta),
        "deha_sphuta_physical_body": _calc_sphuta_item(sphuta.deha_sphuta),
        "mrityu_sphuta_critical_longevity": _calc_sphuta_item(sphuta.mrityu_sphuta),
        "tri_sphuta_combined_sensitive_point": _calc_sphuta_item(sphuta.tri_sphuta),
        "sookshma_tri_sphuta": _calc_sphuta_item(sphuta.sookshma_tri_sphuta)
    }
    
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "divisional_chart_factor": divisional_chart_factor,
        "vedic_sphutas": sphutas_dict
    }

if __name__ == "__main__":
    server.run()
