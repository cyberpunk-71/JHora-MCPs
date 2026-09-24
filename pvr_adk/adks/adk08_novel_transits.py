#!/usr/bin/env python3
"""
ADK-08: Two Novel Transit Principles (Stationary Transits in Vargas)
-------------------------------------------------------------------
Implements Research Paper 08: "Two Novel Transit Principles: Based on Objective Longitude Correlations"
By P.V.R. Narasimha Rao (December 31, 2013).

Core Methodological Principles:
1. Stationary Transits as Anchor Moments:
   - When a planet transitions between direct and retrograde motion, its daily speed drops to zero.
   - A stationary planet acts as a calm, observant catalyst that triggers latent karmas.
2. Divisional Longitude Matching:
   - Calculate the EXACT DIVISIONAL LONGITUDE of the stationary planet in the D-chart of interest.
   - Check if this stationary divisional longitude falls within 3.0° of:
     a) Natal divisional Lagna
     b) Natal divisional Lagna Lord
     c) Natal divisional House Lord (e.g. 7th lord in D-9 for marriage, 10th lord in D-10 for career)
     d) Natal divisional Karaka (Jupiter/Venus for marriage, Sun/Saturn for career, Mars for children)
3. Aspects Used:
   - Parasara full aspects (7th for all, 4th/8th for Mars, 5th/9th for Jupiter, 3rd/10th for Saturn).
4. Timing Window:
   - The major event materializes within 1-2 months before or after the exact stationary date.
"""

from typing import Dict, Any, List, Tuple
import swisseph as swe
from pvr_adk.core.config import (
    STATIONARY_ORB_DEGREES, PLANET_NAMES, RASI_NAMES, get_chart_method
)
from pvr_adk.core.chart_engine import set_pushya_paksha_ayanamsa

class ADK08NovelTransits:
    """Agentic Decision Kit for Stationary Transits and Exact Divisional Longitude Triggers."""

    def __init__(self):
        set_pushya_paksha_ayanamsa()

    def get_divisional_longitude(self, sidereal_deg: float, varga_factor: int,
                                 chart_method: int = 1) -> Tuple[int, float, float]:
        """
        Calculates the divisional sign index, degree within sign (0-30),
        and absolute divisional longitude (0-360) for a given sidereal longitude.
        Implements PVR's exact mathematical formula from Paper 08.
        """
        sidereal_deg = sidereal_deg % 360.0
        sign_idx = int(sidereal_deg // 30.0)
        deg_in_sign = sidereal_deg % 30.0

        from jhora.horoscope.chart import charts
        pp = [["Planet", [sign_idx, deg_in_sign]]]
        try:
            res = charts.divisional_positions_from_rasi_positions(
                pp, divisional_chart_factor=varga_factor, chart_method=chart_method
            )
            div_sign = res[0][1][0]
            div_deg = res[0][1][1]
            if varga_factor == 16 and chart_method == 2:
                div_deg = 30.0 - div_deg
        except Exception:
            span = 30.0 / varga_factor
            part_idx = int(deg_in_sign // span)
            advancement = deg_in_sign - (part_idx * span)
            div_sign = (sign_idx + part_idx) % 12
            div_deg = (advancement * varga_factor) % 30.0

        div_total = (div_sign * 30.0 + div_deg) % 360.0
        return div_sign, div_deg, div_total

    def scan_stationary_transits(self, start_jd: float, end_jd: float,
                                planet_name: str = "Saturn") -> List[Dict[str, Any]]:
        """
        Scans for stationary moments (speed transition through zero)
        for a planet between start_jd and end_jd.
        """
        set_pushya_paksha_ayanamsa()
        swe_map = {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Mars": swe.MARS}
        p_id = swe_map.get(planet_name, swe.SATURN)

        stationary_events = []
        step = 1.0  # daily step
        curr_jd = start_jd

        prev_speed = None
        while curr_jd <= end_jd:
            pos = swe.calc_ut(curr_jd, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
            speed = pos[0][3]  # daily longitudinal speed

            if prev_speed is not None:
                # Sign change in speed indicates stationary point
                if (prev_speed > 0 and speed <= 0) or (prev_speed < 0 and speed >= 0):
                    # Refine to exact stationary hour
                    exact_jd = curr_jd - 0.5
                    exact_pos = swe.calc_ut(exact_jd, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
                    sid_long = exact_pos[0][0] % 360.0
                    station_type = "Stationary Turning Retrograde" if prev_speed > 0 else "Stationary Turning Direct"
                    cal = swe.revjul(exact_jd)
                    stationary_events.append({
                        "planet": planet_name,
                        "exact_jd": exact_jd,
                        "date_str": f"{cal[0]}-{cal[1]:02d}-{cal[2]:02d}",
                        "type": station_type,
                        "sidereal_longitude": sid_long,
                        "sign": RASI_NAMES[int(sid_long // 30)],
                        "degree_in_sign": sid_long % 30.0
                    })
            prev_speed = speed
            curr_jd += step

        return stationary_events

    def check_transit_trigger_on_natal(self, stationary_event: Dict[str, Any],
                                       natal_point_div_long: float,
                                       varga_factor: int,
                                       target_point_name: str) -> Dict[str, Any]:
        """
        Tests if a stationary planet's divisional longitude triggers a natal divisional point.
        """
        p_name = stationary_event["planet"]
        sid_long = stationary_event["sidereal_longitude"]
        method = get_chart_method(varga_factor)
        _, _, stat_div_total = self.get_divisional_longitude(sid_long, varga_factor, method)

        # Check Conjunction (within 3°)
        diff = abs(stat_div_total - natal_point_div_long)
        if diff > 180.0: diff = 360.0 - diff
        is_conj = diff <= STATIONARY_ORB_DEGREES

        # Check Special Aspects:
        # Saturn aspects 3rd (60°), 7th (180°), 10th (270°)
        # Jupiter aspects 5th (120°), 7th (180°), 9th (240°)
        # Mars aspects 4th (90°), 7th (180°), 8th (210°)
        aspect_angles = [180.0]
        if p_name == "Saturn": aspect_angles.extend([60.0, 270.0])
        elif p_name == "Jupiter": aspect_angles.extend([120.0, 240.0])
        elif p_name == "Mars": aspect_angles.extend([90.0, 210.0])

        is_aspect = False
        aspect_name = "None"
        aspect_orb = 999.0

        if is_conj:
            is_aspect = True
            aspect_name = "Conjunction"
            aspect_orb = diff
        else:
            for angle in aspect_angles:
                asp_diff = abs(((stat_div_total + angle) % 360.0) - natal_point_div_long)
                if asp_diff > 180.0: asp_diff = 360.0 - asp_diff
                if asp_diff <= STATIONARY_ORB_DEGREES:
                    is_aspect = True
                    aspect_name = f"Special Aspect ({angle}°)"
                    aspect_orb = asp_diff
                    break

        return {
            "adk_id": "ADK-08",
            "name": "Stationary Transit Trigger Evaluator",
            "varga": f"D{varga_factor}",
            "target_natal_point": target_point_name,
            "target_divisional_degree": round(natal_point_div_long, 2),
            "stationary_event": stationary_event,
            "stationary_divisional_degree": round(stat_div_total, 2),
            "is_trigger_activated": is_aspect,
            "aspect_type": aspect_name,
            "orb_degrees": round(aspect_orb, 2) if is_aspect else None,
            "research_reference": "PVR Paper 08: Two Novel Transit Principles"
        }
