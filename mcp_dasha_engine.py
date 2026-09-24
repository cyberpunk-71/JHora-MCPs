#!/usr/bin/env python3
"""
PyJHora MCP Server 4: Dasha & Timing Engine (mcp_dasha_engine.py)
Provides comprehensive Vedic Dasha calculations including Vimsottari (Maha/Antar/Pratyantar),
Graha Dashas (Ashtottari, Yogini, Shodasottari, Dwadasottari), Rasi Dashas (Narayana, Chara, Kalachakra),
and Annual Dashas (Patyayini, Mudda) with active running dasha finder.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from mcp_base import MCPServer
from jhora_helpers import (
    create_date_and_place,
    PLANET_NAMES,
    RASI_NAMES
)
from jhora.horoscope.dhasa.graha import (
    vimsottari,
    ashtottari,
    yogini,
    shodasottari,
    dwadasottari,
    dwisatpathi
)
from jhora.horoscope.dhasa.raasi import (
    narayana,
    chara,
    kalachakra
)
from jhora.horoscope.dhasa.annual import (
    mudda,
    patyayini
)
from jhora.panchanga import drik
from jhora import utils, const

server = MCPServer(name="mcp-jhora-dasha-engine", version="1.0.0")

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

def _format_dasha_date(dt) -> str:
    """Converts JD float or (y, m, d, h_float) to 'YYYY-MM-DD HH:MM:SS' string."""
    if isinstance(dt, (int, float)):
        y, m, d, h_frac = utils.jd_to_gregorian(dt)
    elif isinstance(dt, (tuple, list)):
        y, m, d = dt[0], dt[1], dt[2]
        h_frac = dt[3] if len(dt) > 3 else 0.0
    else:
        return str(dt)
    hr = int(h_frac)
    mn = int((h_frac - hr) * 60)
    sc = int(round(((h_frac - hr) * 60 - mn) * 60))
    if sc >= 60:
        sc = 0
        mn += 1
    if mn >= 60:
        mn = 0
        hr += 1
    return f"{int(y):04d}-{int(m):02d}-{int(d):02d} {hr:02d}:{mn:02d}:{sc:02d}"

def _get_planet_name(idx: int) -> str:
    if 0 <= idx < len(PLANET_NAMES):
        return PLANET_NAMES[idx]
    return f"Planet-{idx}"

def _get_rasi_name(idx: int) -> str:
    if 0 <= idx < len(RASI_NAMES):
        return RASI_NAMES[idx]
    return f"Rasi-{idx}"

@server.tool(
    name="get_vimsottari_dasha",
    description="Calculate complete 120-year Vimsottari Dasha (Mahadashas & Antardashas/Bhuktis) and identify the active running dasha for any given date.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "target_year": {"type": "integer", "description": "Optional target year to check active running dasha (defaults to birth year)"},
            "target_month": {"type": "integer", "description": "Optional target month (1-12)"},
            "target_day": {"type": "integer", "description": "Optional target day (1-31)"}
        },
        "required": ["year", "month", "day"]
    }
)
def get_vimsottari_dasha(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    target_year: Optional[int] = None,
    target_month: Optional[int] = None,
    target_day: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    # Target date Julian Day
    t_yr = target_year if target_year is not None else year
    t_mo = target_month if target_month is not None else month
    t_dy = target_day if target_day is not None else day
    target_dob = drik.Date(t_yr, t_mo, t_dy)
    target_jd = utils.julian_day_number(target_dob, (12, 0, 0))
    
    # Mahadasha start table
    md_dict = vimsottari.vimsottari_mahadasa(jd, place)
    mahadashas = []
    for p_idx, p_jd in md_dict.items():
        mahadashas.append({
            "planet": _get_planet_name(p_idx),
            "start_date": _format_dasha_date(p_jd),
            "julian_day": round(float(p_jd), 4)
        })
        
    # Full Antardasha list
    vb_res = vimsottari.get_vimsottari_dhasa_bhukthi(jd, place)
    bhuktis_raw = vb_res[1] if isinstance(vb_res, tuple) and len(vb_res) > 1 else vb_res
    
    antardashas = []
    active_dasha = None
    
    for item in bhuktis_raw:
        lords, start_dt, dur_years = item[0], item[1], item[2]
        m_lord = _get_planet_name(lords[0])
        a_lord = _get_planet_name(lords[1])
        start_str = _format_dasha_date(start_dt)
        
        # Calculate approx end date in Julian days
        if isinstance(start_dt, (int, float)):
            start_jd_val = start_dt
        else:
            s_dob = drik.Date(int(start_dt[0]), int(start_dt[1]), int(start_dt[2]))
            s_tob = (int(start_dt[3]), int((start_dt[3]%1)*60), 0)
            start_jd_val = utils.julian_day_number(s_dob, s_tob)
            
        end_jd_val = start_jd_val + dur_years * 365.25
        end_str = _format_dasha_date(end_jd_val)
        
        entry = {
            "mahadasha_lord": m_lord,
            "antardasha_lord": a_lord,
            "start_date": start_str,
            "end_date": end_str,
            "duration_years": round(float(dur_years), 3)
        }
        antardashas.append(entry)
        
        if start_jd_val <= target_jd < end_jd_val:
            active_dasha = {
                "as_of_date": f"{t_yr:04d}-{t_mo:02d}-{t_dy:02d}",
                "running_mahadasha": m_lord,
                "running_antardasha": a_lord,
                "period_start": start_str,
                "period_end": end_str,
                "remaining_duration_years": round(float((end_jd_val - target_jd) / 365.25), 3)
            }
            
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "active_running_dasha": active_dasha,
        "vimsottari_mahadashas": mahadashas,
        "total_antardashas_count": len(antardashas),
        "vimsottari_antardashas_sample": antardashas[:15]
    }

@server.tool(
    name="get_nakshatra_dashas",
    description="Calculate alternative Vedic Nakshatra/Graha Dasha systems: Ashtottari (108 yrs), Yogini (36 yrs), Shodasottari (116 yrs), Dwadasottari (112 yrs), and Dwisatpathi (100 yrs).",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "dasha_system": {
                "type": "string",
                "description": "Dasha system to calculate: ASHTOTTARI, YOGINI, SHODASOTTARI, DWADASOTTARI, DWISATPATHI, or ALL",
                "default": "ALL"
            }
        },
        "required": ["year", "month", "day"]
    }
)
def get_nakshatra_dashas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    dasha_system: str = "ALL",
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    system = dasha_system.upper()
    results = {}
    
    # 1. Ashtottari
    if system in ["ALL", "ASHTOTTARI"]:
        try:
            a_dict = ashtottari.ashtottari_mahadasa(jd, place)
            a_list = []
            for p_idx, p_jd in a_dict.items():
                a_list.append({
                    "planet": _get_planet_name(p_idx),
                    "start_date": _format_dasha_date(p_jd)
                })
            results["ashtottari_dasha_108_years"] = a_list
        except Exception as e:
            results["ashtottari_dasha_108_years"] = {"error": str(e)}
            
    # 2. Yogini
    if system in ["ALL", "YOGINI"]:
        try:
            y_raw = yogini.get_dhasa_bhukthi(dob, tob, place)
            y_names = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
            y_list = []
            for item in y_raw[:16]: # Sample
                lords, start_dt, dur = item[0], item[1], item[2]
                m_name = y_names[lords[0] % 8] if isinstance(lords[0], int) else str(lords[0])
                a_name = y_names[lords[1] % 8] if isinstance(lords[1], int) else str(lords[1])
                y_list.append({
                    "major_yogini": m_name,
                    "sub_yogini": a_name,
                    "start_date": _format_dasha_date(start_dt),
                    "duration_years": round(float(dur), 3)
                })
            results["yogini_dasha_36_years"] = {
                "total_periods": len(y_raw),
                "periods": y_list
            }
        except Exception as e:
            results["yogini_dasha_36_years"] = {"error": str(e)}
            
    # 3. Shodasottari
    if system in ["ALL", "SHODASOTTARI"]:
        try:
            s_raw = shodasottari.get_dhasa_bhukthi(dob, tob, place)
            s_list = []
            for item in s_raw[:12]:
                lords, start_dt, dur = item[0], item[1], item[2]
                s_list.append({
                    "mahadasha_lord": _get_planet_name(lords[0]),
                    "antardasha_lord": _get_planet_name(lords[1]),
                    "start_date": _format_dasha_date(start_dt),
                    "duration_years": round(float(dur), 3)
                })
            results["shodasottari_dasha_116_years"] = {
                "total_periods": len(s_raw),
                "periods": s_list
            }
        except Exception as e:
            results["shodasottari_dasha_116_years"] = {"error": str(e)}
            
    # 4. Dwadasottari
    if system in ["ALL", "DWADASOTTARI"]:
        try:
            d_raw = dwadasottari.get_dhasa_bhukthi(dob, tob, place)
            d_list = []
            for item in d_raw[:12]:
                lords, start_dt, dur = item[0], item[1], item[2]
                d_list.append({
                    "mahadasha_lord": _get_planet_name(lords[0]),
                    "antardasha_lord": _get_planet_name(lords[1]),
                    "start_date": _format_dasha_date(start_dt),
                    "duration_years": round(float(dur), 3)
                })
            results["dwadasottari_dasha_112_years"] = {
                "total_periods": len(d_raw),
                "periods": d_list
            }
        except Exception as e:
            results["dwadasottari_dasha_112_years"] = {"error": str(e)}
            
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "nakshatra_dashas": results
    }

@server.tool(
    name="get_narayana_dasa",
    description="Calculate Narayana Dasa for Rasi chart (D-1) or any divisional chart (D-9 Navamsa, D-10 Dasamsa, etc.) with sign durations and antardashas.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "divisional_chart_factor": {
                "type": "integer",
                "description": "Varga factor: 1 (Rasi), 9 (Navamsa), 10 (Dasamsa), etc.",
                "default": 1
            }
        },
        "required": ["year", "month", "day"]
    }
)
def get_narayana_dasa(
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
    
    if divisional_chart_factor == 1:
        n_raw = narayana.narayana_dhasa_for_rasi_chart(dob, tob, place)
    else:
        n_raw = narayana.narayana_dhasa_for_divisional_chart(dob, tob, place, divisional_chart_factor=divisional_chart_factor)
        
    periods = []
    for item in n_raw:
        rasis, start_dt, dur = item[0], item[1], item[2]
        m_rasi = _get_rasi_name(rasis[0])
        a_rasi = _get_rasi_name(rasis[1])
        periods.append({
            "mahadasha_sign": m_rasi,
            "antardasha_sign": a_rasi,
            "start_date": _format_dasha_date(start_dt),
            "duration_years": round(float(dur), 3)
        })
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "divisional_chart_factor": divisional_chart_factor,
        "narayana_dasa": {
            "total_subperiods_count": len(periods),
            "periods": periods
        }
    }

@server.tool(
    name="get_chara_dasa",
    description="Calculate Jaimini Chara Dasa with sign Mahadashas, Antardashas, and exact date progression.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_chara_dasa(
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
    
    c_raw = chara.get_dhasa_antardhasa(dob, tob, place)
    periods = []
    for item in c_raw:
        rasis, start_dt, dur = item[0], item[1], item[2]
        m_rasi = _get_rasi_name(rasis[0])
        a_rasi = _get_rasi_name(rasis[1])
        periods.append({
            "mahadasha_sign": m_rasi,
            "antardasha_sign": a_rasi,
            "start_date": _format_dasha_date(start_dt),
            "duration_years": round(float(dur), 3)
        })
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "chara_dasa": {
            "total_subperiods_count": len(periods),
            "periods": periods
        }
    }

@server.tool(
    name="get_kalachakra_dasa",
    description="Calculate Kalachakra Dasa based on Moon's Navamsa and Savya/Apasavya progression with Deha and Jeeva signs.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def get_kalachakra_dasa(
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
    
    k_raw = kalachakra.get_dhasa_bhukthi(dob, tob, place)
    periods = []
    for item in k_raw:
        rasis, start_dt, dur = item[0], item[1], item[2]
        m_rasi = _get_rasi_name(rasis[0])
        a_rasi = _get_rasi_name(rasis[1])
        periods.append({
            "mahadasha_sign": m_rasi,
            "antardasha_sign": a_rasi,
            "start_date": _format_dasha_date(start_dt),
            "duration_years": round(float(dur), 3)
        })
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "kalachakra_dasa": {
            "total_subperiods_count": len(periods),
            "periods": periods
        }
    }

@server.tool(
    name="get_annual_dashas",
    description="Calculate Mudda Dasa (annual Vimsottari) and Patyayini Dasa for solar return annual Varshaphal charts at a specified age/year.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "age_years": {
                "type": "integer",
                "description": "Age / year of annual chart (e.g. 24 for 24th solar return)",
                "default": 1
            }
        },
        "required": ["year", "month", "day"]
    }
)
def get_annual_dashas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    age_years: int = 1,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    # 1. Mudda Dasa
    mudda_list = []
    try:
        m_raw = mudda.mudda_dhasa_bhukthi(jd, place, years=age_years)
        for item in m_raw:
            lords, start_dt, dur_days = item[0], item[1], item[2]
            mudda_list.append({
                "mahadasha_lord": _get_planet_name(lords[0]),
                "antardasha_lord": _get_planet_name(lords[1]),
                "start_date": _format_dasha_date(start_dt),
                "duration_days": round(float(dur_days), 2)
            })
    except Exception as e:
        mudda_list = [{"error": str(e)}]
        
    # 2. Patyayini Dasa
    patyayini_list = []
    try:
        p_raw = patyayini.get_dhasa_bhukthi(jd, place)
        for item in p_raw:
            lords, start_dt, dur_frac = item[0], item[1], item[2]
            patyayini_list.append({
                "lord_1": _get_planet_name(lords[0]),
                "lord_2": _get_planet_name(lords[1]),
                "start_date": _format_dasha_date(start_dt),
                "duration_share": round(float(dur_frac), 4)
            })
    except Exception as e:
        patyayini_list = [{"error": str(e)}]
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "age_years": age_years,
        "mudda_dasa": mudda_list,
        "patyayini_dasa": patyayini_list
    }

if __name__ == "__main__":
    server.run()
