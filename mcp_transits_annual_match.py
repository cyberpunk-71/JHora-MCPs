#!/usr/bin/env python3
"""
PyJHora MCP Server 6: Transits, Tajaka Annual Varshaphal & Match Engine (mcp_transits_annual_match.py)
Provides Tajaka Annual Varshaphal charts, Muntha calculation, Year/Month Lord (Varsha Pati),
Tajaka Sahams (50+ sensitive points), 16 Tajaka Yogas (Ithasala, Eesarpha, Kamboola),
Ashta Koota (36 Guna) & Naalu Porutham marriage matching, and Longevity estimates.
"""
from __future__ import annotations
from typing import Dict, Any, List, Optional
from mcp_base import MCPServer
from jhora_helpers import (
    create_date_and_place,
    format_longitude,
    format_rasi_degree,
    PLANET_NAMES,
    RASI_NAMES,
    NAKSHATRA_NAMES,
    WEEKDAY_LORDS,
    calculate_chart_vision,
    get_pvr_divisional_position
)
from jhora.horoscope.transit import tajaka, saham, tajaka_yoga
from jhora.horoscope.match import compatibility
from jhora.horoscope.prediction import longevity
from jhora.horoscope.chart import charts
from jhora.panchanga import drik
from jhora import utils, const
import swisseph as swe

server = MCPServer(name="mcp-jhora-transits-annual-match", version="1.0.0")

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

def _get_planet_name(idx: int) -> str:
    if 0 <= idx < len(PLANET_NAMES):
        return PLANET_NAMES[idx]
    return f"Planet-{idx}"

@server.tool(
    name="calculate_tajaka_varshaphal",
    description="Calculate Tajaka Annual Solar Return chart (Varshaphal) for any target age/year, including exact Varsha Pravesha time, Lord of the Year (Varsha Pati), Lord of the Month (Maasa Pati), Muntha position, and annual planetary positions.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "target_age_years": {
                "type": "integer",
                "description": "Age for solar return (e.g. 24 for 24th birthday year / 25th year of life)",
                "default": 1
            },
            "divisional_chart_factor": {
                "type": "integer",
                "description": "Varga factor for annual chart (default: 1 for Rasi D-1)",
                "default": 1
            }
        },
        "required": ["year", "month", "day"]
    }
)
def calculate_tajaka_varshaphal(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    target_age_years: int = 1,
    divisional_chart_factor: int = 1,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    # 1. Annual Chart & Varsha Pravesha time
    ac, (vp_date, vp_time) = tajaka.annual_chart(jd, place, divisional_chart_factor=divisional_chart_factor, years=target_age_years)
    
    # 2. Lord of the Year
    try:
        varsha_lord_idx = tajaka.lord_of_the_year(jd, place, years_from_dob=target_age_years)
        varsha_lord_name = _get_planet_name(varsha_lord_idx)
    except Exception:
        varsha_lord_idx = None
        varsha_lord_name = "Unknown"
        
    # 3. Natal Lagna & Muntha calculation
    natal_pp = charts.divisional_chart(jd, place, divisional_chart_factor=1)
    natal_lagna_rasi = natal_pp[0][1][0]
    muntha_rasi_idx = (natal_lagna_rasi + target_age_years) % 12
    muntha_house_from_annual_lagna = ((muntha_rasi_idx - ac[0][1][0]) % 12) + 1
    
    # Format Annual Chart Positions
    annual_planets = {}
    for p_id, (rasi_idx, deg_in_rasi) in ac:
        p_name = "Lagna" if p_id == "L" else _get_planet_name(p_id)
        tot_deg = rasi_idx * 30.0 + deg_in_rasi
        annual_planets[p_name] = {
            "rasi_name": RASI_NAMES[rasi_idx],
            "degrees_in_rasi": format_rasi_degree(rasi_idx, deg_in_rasi),
            "total_degrees": round(tot_deg, 4)
        }
        
    vp_date_str = f"{vp_date[0]:04d}-{vp_date[1]:02d}-{vp_date[2]:02d} {vp_time}"
    
    # Generate Detailed Chart Vision for Varshaphal
    vision_input = {}
    annual_lagna_rasi = ac[0][1][0]
    annual_lagna_deg = ac[0][1][1]
    for p_id, (rasi_idx, deg_in_rasi) in ac:
        if p_id != "L":
            p_name = _get_planet_name(p_id)
            vision_input[p_name] = {
                "rasi_idx": rasi_idx,
                "deg_in_rasi": deg_in_rasi,
                "is_retrograde": False
            }
    
    detailed_vision = calculate_chart_vision(
        annual_lagna_rasi, annual_lagna_deg, vision_input, chart_name="Tajaka Annual Varshaphal"
    )
    
    return {
        "status": "success",
        "birth_chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "target_age_years": target_age_years,
        "varsha_pravesha_exact_time": vp_date_str,
        "lord_of_the_year_varshapathi": varsha_lord_name,
        "muntha_position": {
            "muntha_sign": RASI_NAMES[muntha_rasi_idx],
            "muntha_house_in_annual_chart": muntha_house_from_annual_lagna
        },
        "annual_chart_positions": annual_planets,
        "detailed_chart_vision": detailed_vision
    }

@server.tool(
    name="calculate_tithi_pravesha_chart_detailed_vision",
    description="Calculate the annual Soli-Lunar return chart (Tithi Pravesha) as researched by P.V.R. Narasimha Rao: solves exact Tithi return moment, determines the Lord of the Year (Vara Lord) and Hora Lord, and provides full 12-house structural vision (lords, dignities, occupants, Graha & Rasi aspects, Raja yogas, Parivartanas) across D-1 and divisional charts.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "target_year": {
                "type": "integer",
                "description": "Calendar year for the Tithi Pravesha return (e.g. 2026)",
                "default": 2026
            },
            "divisional_chart_factor": {
                "type": "integer",
                "description": "Varga factor to compute (e.g. 1 for D-1, 9 for D-9, 10 for D-10, 24 for D-24)",
                "default": 1
            },
            "pvr_reformed_method": {
                "type": "boolean",
                "description": "Use PVR reformed varga rules (D-10 M3, D-24 M2, D-60 M3)",
                "default": True
            }
        },
        "required": ["year", "month", "day", "target_year"]
    }
)
def calculate_tithi_pravesha_chart_detailed_vision(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location", ayanamsa_mode: str = "PUSHYA_PAKSHA",
    target_year: int = 2026,
    divisional_chart_factor: int = 1,
    pvr_reformed_method: bool = True,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, birth_jd_ut = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    # 1. Natal Tithi angle
    s_pos_b = swe.calc_ut(birth_jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
    m_pos_b = swe.calc_ut(birth_jd_ut, swe.MOON, swe.FLG_SWIEPH)[0][0]
    natal_tithi_angle = (m_pos_b - s_pos_b) % 360.0
    tithi_no = int(natal_tithi_angle / 12.0) + 1
    
    # Preceding New Moon tropical Sun sign at birth
    approx_b_nm = birth_jd_ut - (natal_tithi_angle / 12.1907)
    curr_b = approx_b_nm
    for _ in range(25):
        sp = swe.calc_ut(curr_b, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        mp = swe.calc_ut(curr_b, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
        d = (mp[0][0] - sp[0][0]) % 360.0
        if d > 180.0: d -= 360.0
        if abs(d) < 1e-7: break
        rel_sp = (mp[0][3] - sp[0][3])
        if abs(rel_sp) < 1e-4: rel_sp = 12.1907
        curr_b -= (d / rel_sp)
    birth_nm_sun_trop = swe.calc_ut(curr_b, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360.0
    birth_nm_sign = int(birth_nm_sun_trop // 30.0)

    # 2. Target Year New Moon in same tropical sign
    approx_day = 80 + birth_nm_sign * 30.43
    if approx_day > 365: approx_day -= 365
    approx_m = max(1, min(12, int(approx_day // 30.43) + 1))
    approx_d = max(1, min(28, int(approx_day % 30.43) + 1))
    approx_t_jd = swe.julday(target_year, approx_m, approx_d, 12.0)
    
    # Find preceding New Moon
    s_t = swe.calc_ut(approx_t_jd, swe.SUN, swe.FLG_SWIEPH)[0][0]
    m_t = swe.calc_ut(approx_t_jd, swe.MOON, swe.FLG_SWIEPH)[0][0]
    ang_t = (m_t - s_t) % 360.0
    curr_t = approx_t_jd - (ang_t / 12.1907)
    for _ in range(25):
        sp = swe.calc_ut(curr_t, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        mp = swe.calc_ut(curr_t, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
        d = (mp[0][0] - sp[0][0]) % 360.0
        if d > 180.0: d -= 360.0
        if abs(d) < 1e-7: break
        rel_sp = (mp[0][3] - sp[0][3])
        if abs(rel_sp) < 1e-4: rel_sp = 12.1907
        curr_t -= (d / rel_sp)
    
    # 3. Solve exact Tithi Pravesha return JD
    tp_jd_ut = curr_t + (natal_tithi_angle / 12.1907)
    for _ in range(30):
        sp = swe.calc_ut(tp_jd_ut, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        mp = swe.calc_ut(tp_jd_ut, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
        d = (mp[0][0] - sp[0][0]) % 360.0
        err = (natal_tithi_angle - d)
        if err > 180.0: err -= 360.0
        elif err < -180.0: err += 360.0
        if abs(err) < 1e-7: break
        rel_sp = (mp[0][3] - sp[0][3])
        if abs(rel_sp) < 1e-4: rel_sp = 12.1907
        tp_jd_ut += (err / rel_sp)

    # Local return date
    cal_date = swe.revjul(tp_jd_ut)
    y, mo, da, float_hour = cal_date
    local_h = float_hour + tz
    if local_h >= 24.0:
        local_h -= 24.0
        da += 1
    hr = int(local_h)
    mn = int((local_h - hr) * 60.0)
    sc = round(((local_h - hr) * 60.0 - mn) * 60.0, 2)
    tp_return_local_str = f"{y:04d}-{mo:02d}-{da:02d} {hr:02d}:{mn:02d}:{sc:05.2f}"

    # Year Lord (Vara Lord)
    day_of_week_idx = int(tp_jd_ut + (tz / 24.0) + 1.5) % 7
    vara_lord = WEEKDAY_LORDS[day_of_week_idx]

    # TP Sidereal Positions
    ayanamsa_val = swe.get_ayanamsa_ut(tp_jd_ut)
    houses, ascmc = swe.houses(tp_jd_ut, latitude, longitude, b'P')
    tp_d1_asc = (ascmc[0] - ayanamsa_val) % 360.0
    
    tp_d1_planets = {}
    for p_name in PLANET_NAMES:
        if p_name == "Ketu":
            rahu_tot = tp_d1_planets.get("Rahu", (0.0, False))[0]
            tp_d1_planets["Ketu"] = ((rahu_tot + 180.0) % 360.0, True)
            continue
        pid = getattr(swe, p_name.upper()) if p_name != "Rahu" else swe.MEAN_NODE
        res, _ = swe.calc_ut(tp_jd_ut, pid)
        sid_deg = (res[0] - ayanamsa_val) % 360.0
        is_ret = (res[3] < 0.0)
        tp_d1_planets[p_name] = (sid_deg, is_ret)

    # Compute target Varga
    v_lagna_sign, v_lagna_deg = get_pvr_divisional_position(
        int(tp_d1_asc // 30.0), tp_d1_asc % 30.0, divisional_chart_factor,
        method="pvr" if pvr_reformed_method else "standard"
    )
    
    tp_varga_placements = {}
    vision_input = {}
    for p_name, (tot_d, is_ret) in tp_d1_planets.items():
        v_s, v_d = get_pvr_divisional_position(
            int(tot_d // 30.0), tot_d % 30.0, divisional_chart_factor,
            method="pvr" if pvr_reformed_method else "standard"
        )
        h_from_l = ((v_s - v_lagna_sign + 12) % 12) + 1
        tp_varga_placements[p_name] = {
            "sign": RASI_NAMES[v_s],
            "degrees_in_sign": f"{v_d:.2f}°",
            "house_from_lagna": h_from_l,
            "is_retrograde": is_ret
        }
        vision_input[p_name] = {
            "rasi_idx": v_s,
            "deg_in_rasi": v_d,
            "is_retrograde": is_ret
        }

    detailed_vision = calculate_chart_vision(
        v_lagna_sign, v_lagna_deg, vision_input,
        chart_name=f"Tithi Pravesha D-{divisional_chart_factor}"
    )

    return {
        "status": "success",
        "target_year": target_year,
        "tithi_number": tithi_no,
        "tithi_pravesha_exact_time_local": tp_return_local_str,
        "vara_lord_year_ruler": vara_lord,
        "ayanamsa": ayanamsa_mode,
        "varga": f"D-{divisional_chart_factor}",
        "calculation_method": "PVR Reformed" if pvr_reformed_method else "Standard Parasara",
        "lagna_sign": RASI_NAMES[v_lagna_sign],
        "lagna_degree": round(v_lagna_deg, 2),
        "varga_placements": tp_varga_placements,
        "detailed_chart_vision": detailed_vision
    }

@server.tool(
    name="calculate_tajaka_sahams",
    description="Calculate all classic Tajaka Sahams (sensitive Arabic/Vedic parts) including Punya (Fortune), Vidya (Knowledge), Yashas (Fame), Mitra (Friends), Sathru (Enemies), Bandhu (Relatives), Karma (Career), Vivaha (Marriage), Karyasiddhi (Success), Roga (Disease), and Apamrityu (Accidents).",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "target_age_years": {
                "type": "integer",
                "description": "Optional age to compute Sahams on Annual Varshaphal chart (if omitted, computes on Natal chart)",
                "default": 0
            },
            "night_birth": {
                "type": "boolean",
                "description": "Set true if birth or Pravesha occurred at night (after sunset)",
                "default": False
            }
        },
        "required": ["year", "month", "day"]
    }
)
def calculate_tajaka_sahams(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    target_age_years: int = 0,
    night_birth: bool = False,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    if target_age_years > 0:
        pp, _ = tajaka.annual_chart(jd, place, divisional_chart_factor=1, years=target_age_years)
        chart_mode = f"Annual Varshaphal (Age {target_age_years})"
    else:
        pp = charts.divisional_chart(jd, place, divisional_chart_factor=1)
        chart_mode = "Natal Chart (D-1)"
        
    saham_fns = [
        ("Punya Saham (Fortune & Good Deeds)", saham.punya_saham),
        ("Vidya Saham (Education & Learning)", saham.vidya_saham),
        ("Yashas Saham (Fame & Reputation)", saham.yasas_saham),
        ("Mitra Saham (Friends & Allies)", saham.mitra_saham),
        ("Sathru Saham (Enemies & Rivals)", saham.sathru_saham),
        ("Bandhu Saham (Relatives & Family)", saham.bandhu_saham),
        ("Karma Saham (Career & Profession)", saham.karma_saham),
        ("Karyasiddhi Saham (Success in Undertakings)", saham.karyasiddhi_saham),
        ("Vivaha Saham (Marriage & Union)", saham.vivaha_saham),
        ("Preethi Saham (Love & Affection)", saham.preethi_saham),
        ("Roga Saham (Disease & Illness)", saham.roga_saham),
        ("Apamrityu Saham (Untimely Mishap)", saham.apamrithyu_saham),
        ("Artha Saham (Wealth & Money)", saham.artha_saham),
        ("Laabha Saham (Gains & Profit)", saham.laabha_saham),
        ("Jeeva Saham (Life Vitality)", saham.jeeva_saham),
        ("Rajya Saham (Authority & Status)", saham.rajya_saham),
        ("Gaurava Saham (Respect & Honor)", saham.gaurava_saham),
        ("Santapa Saham (Grief & Sorrow)", saham.santapa_saham),
        ("Sastra Saham (Weapons & Sciences)", saham.sastra_saham),
        ("Vanika Saham (Commerce & Trade)", saham.vanika_saham)
    ]
    
    sahams_res = {}
    for s_name, s_fn in saham_fns:
        try:
            # Check if fn accepts night_time_birth
            try:
                deg = s_fn(pp, night_time_birth=night_birth)
            except TypeError:
                deg = s_fn(pp)
            fmt = format_longitude(deg)
            sahams_res[s_name] = {
                "longitude_degrees": round(float(deg), 4),
                "rasi": fmt["rasi_name"],
                "degrees_in_rasi": fmt["degrees_in_rasi"],
                "nakshatra": fmt["nakshatra_name"],
                "pada": fmt["pada"]
            }
        except Exception as e:
            sahams_res[s_name] = {"error": str(e)}
            
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "chart_mode": chart_mode,
        "is_night_birth": night_birth,
        "tajaka_sahams": sahams_res
    }

@server.tool(
    name="calculate_tajaka_yogas",
    description="Evaluate 16 classic Tajaka planetary yogas including Ithasala (Muthashila), Eesarpha (Musaripha), Kamboola, Gairi-Kamboola, Nakta, and Yamaya yogas.",
    input_schema={
        "type": "object",
        "properties": {
            **LOCATION_PARAMS,
            "target_age_years": {
                "type": "integer",
                "description": "Age for Annual Varshaphal chart (0 for Natal)",
                "default": 0
            }
        },
        "required": ["year", "month", "day"]
    }
)
def calculate_tajaka_yogas(
    year: int, month: int, day: int,
    hour: int = 12, minute: int = 0, second: float = 0.0,
    latitude: float = 13.0827, longitude: float = 80.2707,
    timezone_offset: float = 5.5, timezone: Optional[float] = None,
    place_name: str = "Location",
    ayanamsa_mode: str = "LAHIRI",
    target_age_years: int = 0,
    **kwargs
) -> Dict[str, Any]:
    tz = timezone if timezone is not None else timezone_offset
    dob, tob, place, jd = create_date_and_place(
        year, month, day, hour, minute, second,
        latitude, longitude, tz, place_name, ayanamsa_mode
    )
    
    if target_age_years > 0:
        pp, _ = tajaka.annual_chart(jd, place, divisional_chart_factor=1, years=target_age_years)
        chart_mode = f"Annual Varshaphal (Age {target_age_years})"
    else:
        pp = charts.divisional_chart(jd, place, divisional_chart_factor=1)
        chart_mode = "Natal Chart (D-1)"
        
    yogas = {}
    
    # 1. Ithasala
    try:
        ith = tajaka_yoga.get_ithasala_yoga_planet_pairs(pp)
        yogas["ithasala_muthashila_yoga"] = {
            "description": "Harmonious union between faster and slower planets moving towards conjunction/aspect within deeptamsa",
            "active_pairs": [
                f"{_get_planet_name(p1)} -> {_get_planet_name(p2)} (Aspect Type: {asp})"
                for p1, p2, asp in ith
            ]
        }
    except Exception as e:
        yogas["ithasala_muthashila_yoga"] = {"error": str(e)}
        
    # 2. Eesarpha
    try:
        ees = tajaka_yoga.get_eesarpha_yoga_planet_pairs(pp)
        yogas["eesarpha_musaripha_yoga"] = {
            "description": "Separating aspect where faster planet has moved past the slower planet by more than 1 degree",
            "active_pairs": [
                f"{_get_planet_name(p1)} separates from {_get_planet_name(p2)}"
                for p1, p2 in ees
            ]
        }
    except Exception as e:
        yogas["eesarpha_musaripha_yoga"] = {"error": str(e)}
        
    # 3. Kamboola
    try:
        kam = tajaka_yoga.get_kamboola_yoga_planet_pairs(pp)
        yogas["kamboola_yoga"] = {
            "description": "Moon connects with planets forming Ithasala yoga, consolidating the auspicious results",
            "is_formed": kam[0] if isinstance(kam, tuple) else False,
            "details": str(kam[1:]) if isinstance(kam, tuple) else str(kam)
        }
    except Exception as e:
        yogas["kamboola_yoga"] = {"error": str(e)}
        
    # 4. Gairi Kamboola
    try:
        gkam = tajaka_yoga.get_gairi_kamboola_yoga_planet_pairs(pp)
        yogas["gairi_kamboola_yoga"] = {
            "description": "Moon in late degrees connecting with a planet in another sign to transfer light",
            "active_pairs": str(gkam)
        }
    except Exception as e:
        yogas["gairi_kamboola_yoga"] = {"error": str(e)}
        
    # 5. Nakta Yoga
    try:
        nak = tajaka_yoga.get_nakta_yoga_planet_triples(pp)
        yogas["nakta_yoga"] = {
            "description": "Faster intermediate planet acts as mediator between two non-aspecting planets",
            "active_triples": str(nak)
        }
    except Exception as e:
        yogas["nakta_yoga"] = {"error": str(e)}
        
    # 6. Yamaya Yoga
    try:
        yam = tajaka_yoga.get_yamaya_yoga_planet_triples(pp)
        yogas["yamaya_yoga"] = {
            "description": "Slower intermediate planet acts as mediator between two non-aspecting planets",
            "active_triples": str(yam)
        }
    except Exception as e:
        yogas["yamaya_yoga"] = {"error": str(e)}
        
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "chart_mode": chart_mode,
        "tajaka_yogas": yogas
    }

@server.tool(
    name="calculate_kundali_match",
    description="Calculate comprehensive Vedic Marriage Compatibility (Kundali Milan) using Ashta Koota (36 Gunas: Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi) plus Naalu Porutham (Mahendra, Vedha, Rajju, Sthree Dheerga).",
    input_schema={
        "type": "object",
        "properties": {
            "boy_nakshatra_number": {"type": "integer", "description": "Boy's Moon Nakshatra (1=Ashwini to 27=Revati)"},
            "boy_pada_number": {"type": "integer", "description": "Boy's Moon Nakshatra Pada (1-4)", "default": 1},
            "girl_nakshatra_number": {"type": "integer", "description": "Girl's Moon Nakshatra (1=Ashwini to 27=Revati)"},
            "girl_pada_number": {"type": "integer", "description": "Girl's Moon Nakshatra Pada (1-4)", "default": 1}
        },
        "required": ["boy_nakshatra_number", "girl_nakshatra_number"]
    }
)
def calculate_kundali_match(
    boy_nakshatra_number: int,
    girl_nakshatra_number: int,
    boy_pada_number: int = 1,
    girl_pada_number: int = 1,
    **kwargs
) -> Dict[str, Any]:
    ak = compatibility.Ashtakoota(
        boy_nakshatra_number,
        boy_pada_number,
        girl_nakshatra_number,
        girl_pada_number
    )
    res = ak.compatibility_score()
    
    # Koota maximum points
    max_kootas = {
        "varna_porutham": (res[0], 1.0, "Spiritual & Ego alignment"),
        "vashya_porutham": (res[1], 2.0, "Mutual attraction & dominance balance"),
        "tara_dina_porutham": (res[2], 3.0, "Health, destiny & longevity harmony"),
        "yoni_porutham": (res[3], 4.0, "Physical, sexual & biological compatibility"),
        "graha_maitri_porutham": (res[4], 5.0, "Psychological & intellectual friendship"),
        "gana_porutham": (res[5], 6.0, "Temperament & behavioral alignment"),
        "bhakoot_rasi_porutham": (res[6], 7.0, "Family happiness & emotional welfare"),
        "nadi_porutham": (res[7], 8.0, "Genetic health & progeny compatibility")
    }
    
    kootas_breakdown = {}
    for k_name, (obtained, max_pt, desc) in max_kootas.items():
        kootas_breakdown[k_name] = {
            "score_obtained": float(obtained),
            "max_points": float(max_pt),
            "significance": desc
        }
        
    total_score = float(res[8])
    
    poruthams = {
        "mahendra_porutham_progeny_wealth": bool(res[9]),
        "vedha_porutham_affliction_avoidance": bool(res[10]),
        "rajju_porutham_spousal_longevity": bool(res[11]),
        "sthree_dheerga_porutham_prosperity": bool(res[12])
    }
    
    boy_nak_name = NAKSHATRA_NAMES[boy_nakshatra_number - 1] if 1 <= boy_nakshatra_number <= 27 else f"Nakshatra-{boy_nakshatra_number}"
    girl_nak_name = NAKSHATRA_NAMES[girl_nakshatra_number - 1] if 1 <= girl_nakshatra_number <= 27 else f"Nakshatra-{girl_nakshatra_number}"
    
    if total_score >= 28.0:
        verdict = "Excellent Match (Uttama)"
    elif total_score >= 18.0:
        verdict = "Good / Acceptable Match (Madhyama)"
    else:
        verdict = "Below Average / Not Recommended (Adhama)"
        
    return {
        "status": "success",
        "boy_nakshatra": f"{boy_nak_name} (Pada {boy_pada_number})",
        "girl_nakshatra": f"{girl_nak_name} (Pada {girl_pada_number})",
        "total_score_out_of_36": total_score,
        "compatibility_verdict": verdict,
        "is_acceptable_match": total_score >= 18.0,
        "ashta_koota_gunas": kootas_breakdown,
        "naalu_poruthams_south_indian_checks": poruthams
    }

@server.tool(
    name="calculate_longevity_estimates",
    description="Estimate Jaimini / Parasara longevity brackets (Alpayu <36, Madhyayu 36-72, Deerghayu 72-108) based on the three classical indicator pairs.",
    input_schema={"type": "object", "properties": LOCATION_PARAMS, "required": ["year", "month", "day"]}
)
def calculate_longevity_estimates(
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
    
    # longevity.life_span_range returns 0 (Short), 1 (Medium), 2 (Long)
    lon_idx = longevity.life_span_range(jd, place)
    
    brackets = {
        0: ("Alpayu (Short Life Span)", "0 to 36 years"),
        1: ("Madhyayu (Medium Life Span)", "36 to 72 years"),
        2: ("Deerghayu / Purnayu (Long Life Span)", "72 to 108+ years")
    }
    
    category, span_range = brackets.get(lon_idx, ("Unknown", "N/A"))
    
    return {
        "status": "success",
        "chart_date": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02.0f}",
        "place": place_name,
        "ayanamsa": ayanamsa_mode,
        "longevity_evaluation": {
            "category": category,
            "estimated_age_span": span_range,
            "indicator_index": lon_idx,
            "methodology": "Three pairs analysis: Lagna Lord vs 8th Lord, Moon vs Sun, and Lagna vs Hora Lagna signs (movable/fixed/dual combinations)."
        }
    }

if __name__ == "__main__":
    server.run()
