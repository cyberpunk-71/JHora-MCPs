#!/usr/bin/env python3
"""
PyJHora MCP Server 2: Divisional Charts, Special Lagnas & Arudhas (mcp_vargas_lagnas.py)
Provides Shodashavargas (D-1 to D-60), Special Lagnas (Hora, Ghatika, Sree, etc.),
Upagrahas (Mandi, Gulika, etc.), Arudha Padas (AL, UL, A1-A12), Argala, and Planetary Aspects.
"""
from __future__ import annotations
import sys
from typing import Dict, Any, List, Optional
from jhora import utils, const
from jhora.panchanga import drik
from jhora.horoscope import info
from jhora.horoscope.chart import charts, arudhas, house
from mcp_base import MCPServer
from jhora_helpers import create_date_and_place, format_longitude, RASI_NAMES, PLANET_NAMES

server = MCPServer(name="mcp-jhora-vargas-lagnas", version="1.0.0")

def _get_planet_name(idx: int) -> str:
    if 0 <= idx < len(PLANET_NAMES):
        return PLANET_NAMES[idx]
    return f"Planet-{idx}"

LOCATION_PARAMS = {
    "year": {"type": "integer", "description": "Year (e.g. 2000)"},
    "month": {"type": "integer", "description": "Month (1-12)"},
    "day": {"type": "integer", "description": "Day of month (1-31)"},
    "hour": {"type": "integer", "description": "Hour in 24h format (0-23)", "default": 12},
    "minute": {"type": "integer", "description": "Minute (0-59)", "default": 0},
    "second": {"type": "number", "description": "Second (0-59.99)", "default": 0.0},
    "latitude": {"type": "number", "description": "Latitude in decimal degrees", "default": 13.0827},
    "longitude": {"type": "number", "description": "Longitude in decimal degrees", "default": 80.2707},
    "timezone_offset": {"type": "number", "description": "Timezone offset from UTC", "default": 5.5},
    "place_name": {"type": "string", "description": "Place name string", "default": "Location"},
    "ayanamsa_mode": {"type": "string", "description": "Ayanamsa (LAHIRI, PUSHYA_PAKSHA, RAMAN, KP)", "default": "LAHIRI"}
}

VARGA_PARAM = {
    **LOCATION_PARAMS,
    "divisional_chart_factor": {
        "type": "integer",
        "description": "Varga factor: 1 (Rasi), 2 (Hora), 3 (Drekkana), 4 (Chaturthamsa), 7 (Saptamsa), 9 (Navamsa), 10 (Dasamsa), 12 (Dwadasamsa), 16 (Shodasamsa), 20 (Vimsamsa), 24 (Siddhamsa), 27 (Nakshatramsa), 30 (Trimsamsa), 40 (Khavedamsa), 45 (Akshavedamsa), 60 (Shashtiamsa)",
        "default": 1
    }
}

@server.tool(
    name="get_divisional_chart",
    description="Calculates planetary placements and house positions for any Divisional Chart (D-1 to D-60: Rasi, Navamsa, Dasamsa, Shashtiamsa, etc.).",
    input_schema={
        "type": "object",
        "properties": VARGA_PARAM,
        "required": ["year", "month", "day"]
    }
)
def get_divisional_chart(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    divisional_chart_factor: int = 1,
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    chart_data = charts.divisional_chart(jd, place, divisional_chart_factor=divisional_chart_factor)
    
    lagna_rasi = 0
    placements = {}
    for item in chart_data:
        p_id = item[0]
        rasi_idx, deg_in_rasi = item[1]
        total_deg = rasi_idx * 30.0 + deg_in_rasi
        
        if p_id == 'L':
            p_name = "Lagna"
            lagna_rasi = rasi_idx
        elif isinstance(p_id, int) and p_id < len(PLANET_NAMES):
            p_name = PLANET_NAMES[p_id]
        else:
            p_name = str(p_id)
            
        formatted = format_longitude(total_deg)
        formatted["house_from_lagna"] = ((rasi_idx - lagna_rasi + 12) % 12) + 1
        placements[p_name] = formatted

    for p_name, data in placements.items():
        data["house_from_lagna"] = ((data["rasi_index"] - lagna_rasi + 12) % 12) + 1

    return {
        "status": "success",
        "varga": f"D-{divisional_chart_factor}",
        "divisional_factor": divisional_chart_factor,
        "ayanamsa": ayanamsa_mode,
        "lagna_rasi": RASI_NAMES[lagna_rasi],
        "placements": placements
    }

@server.tool(
    name="get_all_divisional_charts_summary",
    description="Calculate standard Shodashavarga (16 divisional charts: D-1, D-2, D-3, D-4, D-7, D-9 Navamsa, D-10 Dasamsa, D-12, D-16, D-20, D-24, D-27, D-30, D-40, D-45, D-60) summary with planetary signs for each varga.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": ["year", "month", "day"]
    }
)
def get_all_divisional_charts_summary(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    vargas = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60]
    varga_labels = {
        1: "D-1 (Rasi)", 2: "D-2 (Hora)", 3: "D-3 (Drekkana)", 4: "D-4 (Chaturthamsa)",
        7: "D-7 (Saptamsa)", 9: "D-9 (Navamsa)", 10: "D-10 (Dasamsa)", 12: "D-12 (Dwadasamsa)",
        16: "D-16 (Shodasamsa)", 20: "D-20 (Vimsamsa)", 24: "D-24 (Siddhamsa)", 27: "D-27 (Nakshatramsa)",
        30: "D-30 (Trimsamsa)", 40: "D-40 (Khavedamsa)", 45: "D-45 (Akshavedamsa)", 60: "D-60 (Shashtiamsa)"
    }
    
    summary = {}
    for v in vargas:
        c_data = charts.divisional_chart(jd, place, divisional_chart_factor=v)
        v_dict = {}
        for item in c_data:
            p_id = item[0]
            r_idx, d_in_r = item[1]
            p_name = "Lagna" if p_id == 'L' else (_get_planet_name(p_id) if isinstance(p_id, int) and p_id < len(PLANET_NAMES) else str(p_id))
            v_dict[p_name] = RASI_NAMES[r_idx]
        summary[varga_labels.get(v, f"D-{v}")] = v_dict
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "shodashavarga_summary": summary
    }

@server.tool(
    name="get_special_lagnas",
    description="Calculates all Special Lagnas: Bhava Lagna, Hora Lagna, Ghatika Lagna, Vighatika Lagna, Varnada Lagna, Sree Lagna, Indu Lagna, Pranapada Lagna.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": ["year", "month", "day"]
    }
)
def get_special_lagnas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    h = info.Horoscope(
        place_with_country_code=place_name,
        latitude=latitude, longitude=longitude, timezone_offset=timezone_offset,
        date_in=dob, birth_time=f"{hour:02d}:{minute:02d}:{int(second):02d}"
    )
    sp_lagnas = h.get_special_lagnas_for_chart(jd, place, divisional_chart_factor=1)
    
    return {
        "status": "success",
        "special_lagnas": sp_lagnas
    }

@server.tool(
    name="get_upagrahas",
    description="Calculates Upagrahas and Apaprashas: Mandi, Gulika, Dhuma, Vyatipata, Parivesha, Indrachapa, Upaketu, Kala, Mrityu, Ardhaprahara, Yamaghantaka.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": ["year", "month", "day"]
    }
)
def get_upagrahas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    h = info.Horoscope(
        place_with_country_code=place_name,
        latitude=latitude, longitude=longitude, timezone_offset=timezone_offset,
        date_in=dob, birth_time=f"{hour:02d}:{minute:02d}:{int(second):02d}"
    )
    upagrahas = h.get_special_planets_for_chart(jd, place, divisional_chart_factor=1)
    
    return {
        "status": "success",
        "upagrahas": upagrahas
    }

@server.tool(
    name="get_arudha_padas",
    description="Calculates all 12 House Arudha Padas (A1 to A12, including Arudha Lagna AL and Upapada Lagna UL).",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": ["year", "month", "day"]
    }
)
def get_arudha_padas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    arudha_longs = arudhas.bhava_arudha_longitudes(jd, place)
    
    padas = {}
    pada_names = [
        "A1 (Arudha Lagna - AL)", "A2 (Dhana Pada)", "A3 (Bhratri Pada)", "A4 (Matri Pada)",
        "A5 (Mantra/Putra Pada)", "A6 (Roga/Shatru Pada)", "A7 (Dara Pada - DP)", "A8 (Mrityu/Randhra Pada)",
        "A9 (Bhagya/Dharma Pada)", "A10 (Karma/Rajya Pada)", "A11 (Labha Pada)", "A12 (Upapada Lagna - UL)"
    ]
    
    for i, long_val in enumerate(arudha_longs):
        name = pada_names[i] if i < len(pada_names) else f"A{i+1}"
        formatted = format_longitude(long_val)
        padas[name] = formatted
        
    return {
        "status": "success",
        "ayanamsa": ayanamsa_mode,
        "arudha_padas": padas
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
    name="get_argala_virodhargala",
    description="Calculates primary, secondary, and tertiary Argala (intervention) and Virodhargala (obstruction) on all 12 houses.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": ["year", "month", "day"]
    }
)
def get_argala_virodhargala(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    chart_d1 = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    h_list = _get_h_list(chart_d1)
    argala, virodha = house.get_argala(h_list, separator='/')
    
    argala_summary = {}
    for h in range(12):
        argala_summary[f"house_{h+1}"] = {
            "rasi": RASI_NAMES[h],
            "argala_planets": [p for p in argala[h] if p],
            "virodhargala_planets": [p for p in virodha[h] if p]
        }
    
    return {
        "status": "success",
        "ayanamsa": ayanamsa_mode,
        "argala_analysis": argala_summary
    }

@server.tool(
    name="get_planetary_aspects",
    description="Calculates Graha Drishti (planetary aspects with exact visual fractions) and Rasi Drishti (sign-based aspects by movable, fixed, dual signs).",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": ["year", "month", "day"]
    }
)
def get_planetary_aspects(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707, timezone_offset: float = 5.5,
    place_name: str = "Location", ayanamsa_mode: str = "LAHIRI",
    **kwargs
) -> Dict[str, Any]:
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, timezone_offset, place_name, ayanamsa_mode
    )
    
    chart_d1 = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    h_list = _get_h_list(chart_d1)
    
    graha_rasis, graha_houses, graha_planets = house.graha_drishti_from_chart(h_list, separator='/')
    rasi_aspected_rasis, rasi_aspected_houses, rasi_aspected_planets = house.raasi_drishti_from_chart(h_list, separator='/')
    
    graha_aspects = {}
    for p_idx in range(len(PLANET_NAMES)):
        p_name = _get_planet_name(p_idx)
        aspected_r = [RASI_NAMES[r] for r in graha_rasis.get(p_idx, [])]
        aspected_h = [h+1 for h in graha_houses.get(p_idx, [])]
        aspected_p = [_get_planet_name(p) for p in graha_planets.get(p_idx, [])]
        graha_aspects[p_name] = {
            "aspected_rasis": aspected_r,
            "aspected_houses": aspected_h,
            "aspected_planets": aspected_p
        }
        
    rasi_aspects = {}
    for r_idx in range(12):
        r_name = RASI_NAMES[r_idx]
        aspected_r = [RASI_NAMES[r] for r in rasi_aspected_rasis.get(r_idx, [])]
        aspected_h = [h+1 for h in rasi_aspected_houses.get(r_idx, [])]
        aspected_p = [_get_planet_name(p) for p in rasi_aspected_planets.get(r_idx, [])]
        rasi_aspects[r_name] = {
            "aspected_rasis": aspected_r,
            "aspected_houses": aspected_h,
            "aspected_planets": aspected_p
        }
    
    return {
        "status": "success",
        "ayanamsa": ayanamsa_mode,
        "graha_drishti_planetary_aspects": graha_aspects,
        "rasi_drishti_sign_aspects": rasi_aspects
    }

if __name__ == "__main__":
    server.run()
