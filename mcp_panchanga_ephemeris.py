#!/usr/bin/env python3
"""
PyJHora MCP Server 1: Panchanga & Ephemeris Engine (mcp_panchanga_ephemeris.py)
Provides detailed Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana), auspicious/inauspicious
muhurthas, calendar elements, and high-precision planetary ephemeris.
"""
from __future__ import annotations
import sys
from typing import Dict, Any, List, Optional
from jhora import utils, const
from jhora.panchanga import drik
from jhora.horoscope import info
from jhora.horoscope.chart import charts
from mcp_base import MCPServer
from jhora_helpers import create_date_and_place, format_longitude, PLANET_NAMES, RASI_NAMES, NAKSHATRA_NAMES

server = MCPServer(name="mcp-jhora-panchanga-ephemeris", version="1.0.0")

LOCATION_PARAMS = {
    "year": {"type": "integer", "description": "Year (e.g. 2026)"},
    "month": {"type": "integer", "description": "Month (1-12)"},
    "day": {"type": "integer", "description": "Day of month (1-31)"},
    "hour": {"type": "integer", "description": "Hour in 24h format (0-23)", "default": 12},
    "minute": {"type": "integer", "description": "Minute (0-59)", "default": 0},
    "second": {"type": "number", "description": "Second (0-59.99)", "default": 0.0},
    "latitude": {"type": "number", "description": "Latitude in decimal degrees (e.g. 13.0827 for Chennai)", "default": 13.0827},
    "longitude": {"type": "number", "description": "Longitude in decimal degrees (e.g. 80.2707 for Chennai)", "default": 80.2707},
    "timezone_offset": {"type": "number", "description": "Timezone offset from UTC in hours (e.g. 5.5 for IST)", "default": 5.5},
    "place_name": {"type": "string", "description": "Place name string", "default": "Location"},
    "ayanamsa_mode": {"type": "string", "description": "Ayanamsa (LAHIRI, PUSHYA_PAKSHA, RAMAN, KP)", "default": "LAHIRI"}
}

REQUIRED_LOCATION_PARAMS = ["year", "month", "day"]

@server.tool(
    name="get_panchanga_details",
    description="Calculates complete 5-fold Panchanga: Tithi, Vara, Nakshatra, Yoga, Karana, Sun/Moon rise and set times.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": REQUIRED_LOCATION_PARAMS
    }
)
def get_panchanga_details(
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
    cal_info = h.get_calendar_information()
    
    return {
        "status": "success",
        "input": {
            "date": f"{year:04d}-{month:02d}-{day:02d}",
            "time": f"{hour:02d}:{minute:02d}:{second:04.1f}",
            "place": place_name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_offset,
            "ayanamsa": ayanamsa_mode,
            "julian_day": round(jd, 6)
        },
        "panchanga": {
            "vara": cal_info.get("Day"),
            "tithi": cal_info.get("Tithi"),
            "nakshatra": cal_info.get("Nakshatram"),
            "moon_rasi": cal_info.get("Raasi"),
            "yoga": cal_info.get("Yoga"),
            "karana": cal_info.get("Karana")
        },
        "astronomical_times": {
            "sunrise": cal_info.get("Sun Rise"),
            "sunset": cal_info.get("Sun Set"),
            "moonrise": cal_info.get("Moon Rise"),
            "moonset": cal_info.get("Moon Set")
        }
    }

@server.tool(
    name="get_inauspicious_periods",
    description="Calculates inauspicious time windows: Rahu Kalam, Yamaganda, Gulika Kalam, and Durmuhurtham.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": REQUIRED_LOCATION_PARAMS
    }
)
def get_inauspicious_periods(
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
    cal_info = h.get_calendar_information()
    
    return {
        "status": "success",
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "place": place_name,
        "rahu_kalam": cal_info.get("Raagu Kaalam"),
        "yamaganda": cal_info.get("Yamagandam"),
        "gulika_kalam": cal_info.get("KuLigai"),
        "durmuhurtham": cal_info.get("Dhur Muhurtham")
    }

@server.tool(
    name="get_auspicious_periods",
    description="Calculates auspicious muhurthas: Abhijit Muhurtha, Brahma Muhurtha, and daily auspicious segments.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": REQUIRED_LOCATION_PARAMS
    }
)
def get_auspicious_periods(
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
    cal_info = h.get_calendar_information()
    
    brahma_time = drik.brahma_muhurtha(jd, place)
    
    return {
        "status": "success",
        "date": f"{year:04d}-{month:02d}-{day:02d}",
        "place": place_name,
        "abhijit_muhurtha": cal_info.get("Abhijit"),
        "brahma_muhurtha": {
            "start": utils.to_dms(brahma_time[0], is_lat_long='time') if isinstance(brahma_time, (tuple, list)) else str(brahma_time),
            "end": utils.to_dms(brahma_time[1], is_lat_long='time') if isinstance(brahma_time, (tuple, list)) and len(brahma_time) > 1 else str(brahma_time)
        }
    }

@server.tool(
    name="get_calendar_details",
    description="Calculates Vedic calendar parameters: Samvatsara, Solar/Lunar months, Ayana, Ritu, Kali/Saka/Vikram years.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": REQUIRED_LOCATION_PARAMS
    }
)
def get_calendar_details(
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
    cal_info = h.get_calendar_information()
    
    return {
        "status": "success",
        "calendar_information": cal_info
    }

@server.tool(
    name="get_planetary_ephemeris",
    description="Calculates exact positions of all 9 Grahas (Sun to Ketu) + Ascendant (Lagna) with longitudes, speeds, motion states, and Nakshatras.",
    input_schema={
        "type": "object",
        "properties": LOCATION_PARAMS,
        "required": REQUIRED_LOCATION_PARAMS
    }
)
def get_planetary_ephemeris(
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
    
    d1 = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    
    planets_data = {}
    for item in d1:
        p_id = item[0]
        rasi_idx, deg_in_rasi = item[1]
        total_deg = rasi_idx * 30.0 + deg_in_rasi
        
        if p_id == 'L':
            p_name = "Lagna"
        elif isinstance(p_id, int) and p_id < len(PLANET_NAMES):
            p_name = PLANET_NAMES[p_id]
        else:
            p_name = str(p_id)
            
        formatted = format_longitude(total_deg)
        planets_data[p_name] = formatted
            
    return {
        "status": "success",
        "ayanamsa": ayanamsa_mode,
        "julian_day": round(jd, 6),
        "planets": planets_data
    }

if __name__ == "__main__":
    server.run()
