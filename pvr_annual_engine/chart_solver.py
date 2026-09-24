"""
PVR Astronomical Chart Solvers
==============================
High-precision ephemeris solvers for:
  - Tropical Solar Return (Tajaka Varshaphal)
  - Preceding New Moon Tropical Soli-Lunar Return (Tithi Pravesha)
  - Sidereal Positions under Pushya-Paksha Ayanamsa
"""

import math
from typing import Dict, Any, Tuple
import swisseph as swe
from pvr_annual_engine.config import AYANAMSA_ID, PLANET_NAMES, RASI_NAMES

swe.set_sid_mode(AYANAMSA_ID, 0.0, 0.0)

def calculate_julian_day_ut(year: int, month: int, day: int,
                            hour: int, minute: int, second: float,
                            timezone: float = 5.5) -> float:
    """Calculates UT Julian Day Number."""
    local_time_dec = hour + (minute / 60.0) + (second / 3600.0)
    jd_local = swe.julday(year, month, day, local_time_dec)
    return jd_local - (timezone / 24.0)

def get_natal_sun_tropical(jd_ut: float) -> float:
    """Returns exact natal tropical longitude of the Sun."""
    res = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH)
    return res[0][0] % 360.0

def solve_tropical_solar_return_jd(natal_sun_trop: float, target_year: int,
                                   birth_month: int, birth_day: int) -> float:
    """
    Solves for the exact Julian Day (UT) when the Sun reaches natal_sun_trop
    in target_year using sub-arcsecond Newton-Raphson iteration.
    """
    approx_jd = swe.julday(target_year, birth_month, birth_day, 12.0)
    curr_jd = approx_jd

    for _ in range(30):
        sun_pos = swe.calc_ut(curr_jd, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        curr_long = sun_pos[0][0] % 360.0
        sun_speed = sun_pos[0][3] if sun_pos[0][3] != 0.0 else 0.9856

        diff = (natal_sun_trop - curr_long)
        if diff > 180.0: diff -= 360.0
        elif diff < -180.0: diff += 360.0

        if abs(diff) < 1e-7:  # sub-arcsecond precision
            break

        curr_jd += (diff / sun_speed)

    return curr_jd

def get_preceding_new_moon_ut(jd_ut: float) -> Tuple[float, float, int]:
    """
    Finds the exact Julian Day (UT) of the New Moon immediately preceding jd_ut,
    and returns (nm_jd_ut, sun_tropical_longitude, sun_tropical_sign).
    """
    s = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
    m = swe.calc_ut(jd_ut, swe.MOON, swe.FLG_SWIEPH)[0][0]
    angle = (m - s) % 360.0
    approx_nm = jd_ut - (angle / 12.1907)
    curr = approx_nm

    for _ in range(30):
        s_pos = swe.calc_ut(curr, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        m_pos = swe.calc_ut(curr, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
        diff = (m_pos[0][0] - s_pos[0][0]) % 360.0
        if diff > 180.0: diff -= 360.0
        if abs(diff) < 1e-7: break
        rel_speed = (m_pos[0][3] - s_pos[0][3])
        if abs(rel_speed) < 1e-4: rel_speed = 12.1907
        curr -= (diff / rel_speed)

    sun_trop = swe.calc_ut(curr, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360.0
    return curr, sun_trop, int(sun_trop // 30.0)

def find_target_year_new_moon_ut(target_year: int, target_tropical_sign: int) -> float:
    """
    Finds the New Moon in the target year where the Sun is in target_tropical_sign.
    """
    approx_day_of_year = 80 + target_tropical_sign * 30.43
    if approx_day_of_year > 365:
        approx_day_of_year -= 365
    approx_month = int(approx_day_of_year // 30.43) + 1
    approx_day = int(approx_day_of_year % 30.43) + 1
    approx_jd = swe.julday(target_year, max(1, min(12, approx_month)), max(1, min(28, approx_day)), 12.0)

    nm_jd, _, nm_sign = get_preceding_new_moon_ut(approx_jd)

    if nm_sign != target_tropical_sign:
        diff_signs = (target_tropical_sign - nm_sign) % 12
        if diff_signs <= 6:
            nm_jd += (diff_signs * 29.530588)
        else:
            nm_jd -= ((12 - diff_signs) * 29.530588)
        nm_jd, _, nm_sign = get_preceding_new_moon_ut(nm_jd + 5.0)

    return nm_jd

def get_natal_tithi_angle(birth_jd_ut: float) -> Tuple[float, float, int]:
    """Returns (tithi_angle_degrees, tithi_fractional_progress, tithi_number_1_to_30)."""
    sun = swe.calc_ut(birth_jd_ut, swe.SUN, swe.FLG_SWIEPH)[0][0]
    moon = swe.calc_ut(birth_jd_ut, swe.MOON, swe.FLG_SWIEPH)[0][0]
    diff = (moon - sun) % 360.0
    tithi_no = int(diff / 12.0) + 1
    tithi_progress = (diff % 12.0) / 12.0
    return diff, tithi_progress, tithi_no

def solve_tithi_pravesha_jd_ut(birth_jd_ut: float, target_year: int) -> float:
    """
    Finds exact Julian Day (UT) of Tithi Pravesha return in target_year.
    """
    natal_angle, _, _ = get_natal_tithi_angle(birth_jd_ut)
    _, _, birth_nm_sign = get_preceding_new_moon_ut(birth_jd_ut)

    target_nm_ut = find_target_year_new_moon_ut(target_year, birth_nm_sign)
    curr_ret = target_nm_ut + (natal_angle / 12.1907)

    for _ in range(30):
        s_pos = swe.calc_ut(curr_ret, swe.SUN, swe.FLG_SWIEPH | swe.FLG_SPEED)
        m_pos = swe.calc_ut(curr_ret, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
        diff = (m_pos[0][0] - s_pos[0][0]) % 360.0
        err = (natal_angle - diff)
        if err > 180.0: err -= 360.0
        elif err < -180.0: err += 360.0
        if abs(err) < 1e-7: break
        rel_speed = (m_pos[0][3] - s_pos[0][3])
        if abs(rel_speed) < 1e-4: rel_speed = 12.1907
        curr_ret += (err / rel_speed)

    return curr_ret

def compute_sidereal_positions_and_lagna(jd_ut: float, latitude: float, longitude: float) -> Tuple[float, Dict[str, Tuple[float, bool]]]:
    """
    Computes Pushya-Paksha Ascendant (Lagna) and Planetary Longitudes (tot_deg, is_retrograde).
    """
    swe.set_sid_mode(AYANAMSA_ID, 0.0, 0.0)

    # Lagna
    houses, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P', swe.FLG_SIDEREAL)
    lagna_deg = ascmc[0] % 360.0

    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    planets_d1 = {}
    for p_name, p_code in planets_map.items():
        res = swe.calc_ut(jd_ut, p_code, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        tot_deg = res[0][0] % 360.0
        is_retro = res[0][3] < 0.0
        planets_d1[p_name] = (tot_deg, is_retro)

    # Ketu = Rahu + 180°
    rahu_deg = planets_d1["Rahu"][0]
    ketu_deg = (rahu_deg + 180.0) % 360.0
    planets_d1["Ketu"] = (ketu_deg, True)

    return lagna_deg, planets_d1
