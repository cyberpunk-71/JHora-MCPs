"""
ADK-04: Redefined Tajaka Varshaphal (Annual Tropical Solar Return Engine)
========================================================================
Implements Research Paper 04: "Re-defining Tajaka Varshaphal Charts"
By P.V.R. Narasimha Rao.

Key Principles:
  1. Exact Tropical Solar Return: Sun returns to exact natal tropical longitude.
  2. Sidereal Chart at Return Moment: Cast using Pushya-Paksha Ayanamsa.
  3. Reformed Divisional Charts: D-1, D-4, D-9, D-10 (Method 3), D-24 (Method 2).
  4. Tajaka Sahams & Ithasala Yogas within Deeptamsha Orbs.
  5. Muntha & Lagna Lord structural evaluation.
"""

from typing import Dict, Any, List, Tuple
import swisseph as swe
from pvr_annual_engine.config import (
    AYANAMSA_ID, RASI_NAMES, PLANET_NAMES, PLANET_MEAN_SPEEDS, DEEPTAMSHA_ORBS
)
from pvr_annual_engine.chart_solver import (
    calculate_julian_day_ut, get_natal_sun_tropical, solve_tropical_solar_return_jd,
    compute_sidereal_positions_and_lagna
)
from pvr_annual_engine.divisional_engine import build_varga_chart

class ADK04TajakaVarshaphal:
    """Agentic Decision Kit for Redefined Tropical Solar Return Varshaphal."""

    def calculate_saham(self, saham_name: str, sun_deg: float, moon_deg: float,
                        mars_deg: float, mercury_deg: float, jupiter_deg: float,
                        venus_deg: float, saturn_deg: float, lagna_deg: float,
                        is_day_birth: bool) -> float:
        """Calculates exact sidereal Saham longitude."""
        if saham_name == "Punya":
            val = (moon_deg - sun_deg + lagna_deg) if is_day_birth else (sun_deg - moon_deg + lagna_deg)
        elif saham_name == "Vidya":
            val = (sun_deg - moon_deg + lagna_deg) if is_day_birth else (moon_deg - sun_deg + lagna_deg)
        elif saham_name == "Karma":
            val = (mars_deg - mercury_deg + lagna_deg)
        elif saham_name == "Vivaha":
            val = (venus_deg - saturn_deg + lagna_deg)
        elif saham_name == "Putra":
            val = (jupiter_deg - mars_deg + lagna_deg)
        elif saham_name == "Paradesa":
            # 9th cusp approx (lagna + 240) - 9th lord + lagna
            val = (lagna_deg + 240.0 - saturn_deg + lagna_deg)
        else:
            val = lagna_deg
        return val % 360.0

    def detect_tajaka_yogas(self, planets_d1: Dict[str, Tuple[float, bool]]) -> List[Dict[str, Any]]:
        """
        Detects Ithasala (applying), Easarapha (separating), and Kamboola yogas.
        """
        yogas = []
        p_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        for i in range(len(p_names)):
            for j in range(i + 1, len(p_names)):
                p1, p2 = p_names[i], p_names[j]
                deg1, is_retro1 = planets_d1[p1]
                deg2, is_retro2 = planets_d1[p2]

                speed1 = PLANET_MEAN_SPEEDS[p1]
                speed2 = PLANET_MEAN_SPEEDS[p2]

                # Identify faster and slower planet
                if speed1 >= speed2:
                    faster, slower = p1, p2
                    f_deg, s_deg = deg1, deg2
                    f_retro, s_retro = is_retro1, is_retro2
                else:
                    faster, slower = p2, p1
                    f_deg, s_deg = deg2, deg1
                    f_retro, s_retro = is_retro2, is_retro1

                # Angular distance
                ang_diff = (f_deg - s_deg) % 360.0
                if ang_diff > 180.0:
                    ang_diff = 360.0 - ang_diff

                # Check Tajaka Aspect angles: 0° (Conj), 60° (Sextile), 90° (Square), 120° (Trine), 180° (Opp)
                aspect_types = {0: "Conjunction", 60: "Friendly Sextile", 90: "Inimical Square", 120: "Friendly Trine", 180: "Inimical Opposition"}
                closest_aspect = None
                min_orb = 999.0

                for asp_ang, asp_type in aspect_types.items():
                    curr_orb = abs(ang_diff - asp_ang)
                    if curr_orb < min_orb:
                        min_orb = curr_orb
                        closest_aspect = (asp_ang, asp_type)

                # Deeptamsha threshold
                max_orb = (DEEPTAMSHA_ORBS[faster] + DEEPTAMSHA_ORBS[slower]) / 2.0

                if min_orb <= max_orb and closest_aspect:
                    asp_ang, asp_type = closest_aspect
                    # Check applying (Ithasala) vs separating (Easarapha)
                    f_pos_in_sign = f_deg % 30.0
                    s_pos_in_sign = s_deg % 30.0

                    if f_pos_in_sign < s_pos_in_sign:
                        yoga_type = "Ithasala (Muthasila - Applying Auspicious Yoga)"
                    else:
                        yoga_type = "Easarapha (Musaripha - Separating Yoga)"

                    yogas.append({
                        "faster_planet": faster,
                        "slower_planet": slower,
                        "yoga_type": yoga_type,
                        "aspect": asp_type,
                        "orb_deg": round(min_orb, 2),
                        "deeptamsha_limit": round(max_orb, 2)
                    })

        return yogas

    def generate_varshaphal_chart(self, birth_year: int, birth_month: int, birth_day: int,
                                  birth_hour: int, birth_minute: int, birth_second: float,
                                  target_year: int,
                                  latitude: float, longitude: float,
                                  timezone: float = 5.5) -> Dict[str, Any]:
        """
        Generates full Tajaka Varshaphal analysis with Vargas, Sahams, and Yogas.
        """
        birth_jd_ut = calculate_julian_day_ut(birth_year, birth_month, birth_day,
                                              birth_hour, birth_minute, birth_second, timezone)
        sun_trop = get_natal_sun_tropical(birth_jd_ut)
        return_jd_ut = solve_tropical_solar_return_jd(sun_trop, target_year, birth_month, birth_day)

        cal_date = swe.revjul(return_jd_ut)
        y, m, d, float_hour = cal_date
        local_h = float_hour + timezone
        if local_h >= 24.0:
            local_h -= 24.0
            d += 1
        h = int(local_h)
        mn = int((local_h - h) * 60.0)
        sec = round(((local_h - h) * 60.0 - mn) * 60.0, 2)

        # Natal Lagna & Sidereal Return positions
        natal_lagna_deg, _ = compute_sidereal_positions_and_lagna(birth_jd_ut, latitude, longitude)
        ret_lagna_deg, ret_planets_d1 = compute_sidereal_positions_and_lagna(return_jd_ut, latitude, longitude)

        # Build Vargas
        d1_chart = build_varga_chart(ret_lagna_deg, ret_planets_d1, 1)
        d4_chart = build_varga_chart(ret_lagna_deg, ret_planets_d1, 4)
        d7_chart = build_varga_chart(ret_lagna_deg, ret_planets_d1, 7)
        d9_chart = build_varga_chart(ret_lagna_deg, ret_planets_d1, 9)
        d10_chart = build_varga_chart(ret_lagna_deg, ret_planets_d1, 10)
        d24_chart = build_varga_chart(ret_lagna_deg, ret_planets_d1, 24)

        # Muntha: (Natal Lagna Sign + completed years) % 12
        completed_years = target_year - birth_year
        natal_lagna_sign = int(natal_lagna_deg // 30.0)
        muntha_sign = (natal_lagna_sign + completed_years) % 12
        ret_lagna_sign = int(ret_lagna_deg // 30.0)
        muntha_house = ((muntha_sign - ret_lagna_sign) % 12) + 1

        # Sahams
        is_day = (6 <= h < 18)
        sahams = {}
        for s_name in ["Punya", "Vidya", "Karma", "Vivaha", "Putra", "Paradesa"]:
            s_deg = self.calculate_saham(
                s_name,
                ret_planets_d1["Sun"][0], ret_planets_d1["Moon"][0],
                ret_planets_d1["Mars"][0], ret_planets_d1["Mercury"][0],
                ret_planets_d1["Jupiter"][0], ret_planets_d1["Venus"][0],
                ret_planets_d1["Saturn"][0], ret_lagna_deg, is_day
            )
            s_sign = int(s_deg // 30.0)
            sahams[s_name] = {
                "longitude_deg": round(s_deg, 2),
                "sign": RASI_NAMES[s_sign],
                "house_from_lagna": ((s_sign - ret_lagna_sign) % 12) + 1
            }

        tajaka_yogas = self.detect_tajaka_yogas(ret_planets_d1)

        return {
            "adk_id": "ADK-04",
            "name": "Redefined Tajaka Varshaphal Engine",
            "target_year": target_year,
            "return_moment_utc_jd": return_jd_ut,
            "return_moment_local": f"{y}-{m:02d}-{d:02d} {h:02d}:{mn:02d}:{sec:05.2f}",
            "muntha": {
                "sign": RASI_NAMES[muntha_sign],
                "house_from_varshaphal_lagna": muntha_house,
                "is_auspicious": muntha_house in [1, 2, 3, 5, 9, 10, 11]
            },
            "sahams": sahams,
            "tajaka_yogas": tajaka_yogas,
            "charts": {
                "D1": d1_chart,
                "D4": d4_chart,
                "D7": d7_chart,
                "D9": d9_chart,
                "D10": d10_chart,
                "D24": d24_chart
            }
        }
