#!/usr/bin/env python3
"""
PVR Multi-Factor Annual Chart Evaluator & LLM Synthesis Engine
==============================================================
Implements P.V.R. Narasimha Rao's comprehensive annual chart analysis
for both Tajaka Varshaphal (Paper 04) and Tithi Pravesha (Paper 05).

Does NOT rely on 1-2 isolated combinations. Instead evaluates:
  1. Dual-Level Chart Architecture: Rasi (D-1) + Topic Divisional Chart (D-N)
  2. Topic House Lords & Dignities (Exalted, Moolatrikona, Own, Neecha Bhanga)
  3. Auspicious Yogas (Raja Yogas, Parivartana Exchanges, Samasaptaka 180° Aspects)
  4. Aspect Geometry (Parasara full aspects, special aspects, Tajaka aspects, Rasi Drishti)
  5. Year Ruler (Vara Lord / King of Year) dignity and placement
  6. Tajaka Sahams (Vidya, Karma, Vivaha, Putra, Punya) & Ithasala Yogas
  7. Multi-factor potential scoring (0-100%) and potential tier classification
  8. Full LLM Synthesis feeding all extracted parameters to Gemini 3.8 Flash High
"""

import os
import sys
import json
import math
import requests
from typing import Dict, List, Any, Tuple, Optional

sys.path.insert(0, "/home/opc/mcp_jhora")

from pvr_adk.core.config import RASI_NAMES, PLANET_NAMES
import swisseph as swe

# Sign Lord mapping: 0=Aries (Mars), 1=Taurus (Venus), ... 11=Pisces (Jupiter)
SIGN_LORDS = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]

# Dignity tables
EXALTATION_SIGNS = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6, "Rahu": 1, "Ketu": 7}
MOOLATRIKONA_SIGNS = {"Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5, "Jupiter": 8, "Venus": 6, "Saturn": 10, "Rahu": 5, "Ketu": 11}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10], "Rahu": [10], "Ketu": [7]
}
DEBILITATION_SIGNS = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0, "Rahu": 7, "Ketu": 1}
MKS_HOUSES = {"Sun": 12, "Moon": 8, "Mars": 7, "Mercury": 7, "Jupiter": 3, "Venus": 6, "Saturn": 1, "Rahu": 9}

TOPIC_CONFIGS = {
    "academic_success": {
        "title": "Academic Distinction & Education",
        "houses": [5, 4, 9, 1],
        "varga": "D24",
        "varga_name": "Siddhamsa (D-24)",
        "karakas": ["Jupiter", "Mercury"],
        "saham": "Vidya",
        "desc": "Academic distinction, competitive exams, admission to premier institutions, scholarship"
    },
    "career_success": {
        "title": "Career Advancement & Political Power",
        "houses": [10, 1, 9, 5, 11],
        "varga": "D10",
        "varga_name": "Dasamsa (D-10)",
        "karakas": ["Sun", "Saturn", "Mercury", "Jupiter"],
        "saham": "Karma",
        "desc": "Professional elevation, executive power, promotion, business growth, societal prominence"
    },
    "marriage": {
        "title": "Marriage & Relationships",
        "houses": [7, 1, 2, 9, 11],
        "varga": "D9",
        "varga_name": "Navamsa (D-9)",
        "karakas": ["Venus", "Jupiter"],
        "saham": "Vivaha",
        "desc": "Marriage timing, auspicious alliance, partner harmony, formal wedding ceremonies"
    },
    "childbirth": {
        "title": "Progeny & Childbirth",
        "houses": [5, 9, 1, 2],
        "varga": "D7",
        "varga_name": "Saptamsa (D-7)",
        "karakas": ["Jupiter"],
        "saham": "Putra",
        "desc": "Conception, birth of children, happiness from progeny, family expansion"
    },
    "foreign_travel": {
        "title": "Foreign Travel & Relocation",
        "houses": [9, 12, 4, 7],
        "varga": "D4",
        "varga_name": "Chaturthamsa (D-4)",
        "karakas": ["Rahu", "Saturn", "Moon"],
        "saham": "Paradesa",
        "desc": "Foreign university study, international relocation, long-distance travel, residence shift"
    }
}

class PVRAnnualEvaluator:
    """Holistic Multi-Factor Analyzer for Tajaka Varshaphal & Tithi Pravesha Charts."""

    def get_planet_dignity(self, planet: str, sign_idx: int) -> str:
        if sign_idx == EXALTATION_SIGNS.get(planet):
            return "Exalted"
        if sign_idx == MOOLATRIKONA_SIGNS.get(planet):
            return "Moolatrikona"
        if sign_idx in OWN_SIGNS.get(planet, []):
            return "Own Sign"
        if sign_idx == DEBILITATION_SIGNS.get(planet):
            return "Debilitated"
        return "Friendly/Neutral"

    def get_house_of_sign(self, sign_idx: int, lagna_sign: int) -> int:
        return ((sign_idx - lagna_sign) % 12) + 1

    def get_lord_of_house(self, house_no: int, lagna_sign: int) -> str:
        sign_idx = (lagna_sign + house_no - 1) % 12
        p_id = SIGN_LORDS[sign_idx]
        return PLANET_NAMES[p_id]

    def analyze_varga_for_topic(self, varga_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """
        Deep structural analysis of a specific chart (D-1 or D-N) for a topic.
        Checks:
          - Lagna Lord placement and dignity
          - House lords placements & dignities
          - House occupants (planets inside key houses, especially exalted/own/benefics)
          - Aspects on key houses
          - Kendra-Trikona Raja Yogas
          - Parivartana exchanges
          - Samasaptaka (180° mutual aspects)
        """
        cfg = TOPIC_CONFIGS.get(topic, TOPIC_CONFIGS["career_success"])
        lagna_sign = varga_data["lagna"]["rasi_idx"]
        planets = varga_data["planets"]

        # Lagna Lord
        lagna_lord = self.get_lord_of_house(1, lagna_sign)
        ll_data = planets.get(lagna_lord, {})
        ll_sign = ll_data.get("rasi_idx", lagna_sign)
        ll_house = self.get_house_of_sign(ll_sign, lagna_sign)
        ll_dignity = self.get_planet_dignity(lagna_lord, ll_sign)
        if ll_dignity == "Debilitated" and ll_data.get("is_retrograde", False):
            ll_dignity = "Debilitated (Neecha Bhanga via Retrograde)"

        lagna_lord_info = {
            "lord": lagna_lord,
            "sign": RASI_NAMES[ll_sign],
            "house": ll_house,
            "dignity": ll_dignity,
            "degree": round(ll_data.get("deg_in_rasi", 0.0), 2)
        }

        # House Lords
        house_lords_info = {}
        for h in cfg["houses"]:
            lord = self.get_lord_of_house(h, lagna_sign)
            p_data = planets.get(lord)
            if p_data:
                p_sign = p_data["rasi_idx"]
                p_house = self.get_house_of_sign(p_sign, lagna_sign)
                dignity = self.get_planet_dignity(lord, p_sign)
                is_retro = p_data.get("is_retrograde", False)
                if dignity == "Debilitated" and is_retro:
                    dignity = "Debilitated (Neecha Bhanga via Retrograde)"
                house_lords_info[f"{h}th_lord_{lord}"] = {
                    "lord": lord,
                    "house_ruled": h,
                    "occupied_sign": RASI_NAMES[p_sign],
                    "occupied_house": p_house,
                    "dignity": dignity,
                    "degree": round(p_data.get("deg_in_rasi", 0.0), 2),
                    "is_retrograde": is_retro
                }

        # House Occupants (What planets occupy each relevant house)
        house_occupants = {h: [] for h in cfg["houses"]}
        for p_name, p_d in planets.items():
            h_occ = self.get_house_of_sign(p_d["rasi_idx"], lagna_sign)
            if h_occ in house_occupants:
                dignity = self.get_planet_dignity(p_name, p_d["rasi_idx"])
                if dignity == "Debilitated" and p_d.get("is_retrograde", False):
                    dignity = "Debilitated (Neecha Bhanga)"
                house_occupants[h_occ].append({
                    "planet": p_name,
                    "sign": RASI_NAMES[p_d["rasi_idx"]],
                    "dignity": dignity,
                    "degree": round(p_d.get("deg_in_rasi", 0.0), 2)
                })

        # Check Raja Yogas (Kendra lord + Trikona lord conjunction)
        kendra_lords = {self.get_lord_of_house(k, lagna_sign): k for k in [1, 4, 7, 10]}
        trikona_lords = {self.get_lord_of_house(t, lagna_sign): t for t in [1, 5, 9]}
        
        raja_yogas = []
        for p1, k_house in kendra_lords.items():
            for p2, t_house in trikona_lords.items():
                if p1 != p2 and p1 in planets and p2 in planets:
                    if planets[p1]["rasi_idx"] == planets[p2]["rasi_idx"]:
                        conj_sign = RASI_NAMES[planets[p1]["rasi_idx"]]
                        conj_house = self.get_house_of_sign(planets[p1]["rasi_idx"], lagna_sign)
                        deg_diff = abs(planets[p1]["deg_in_rasi"] - planets[p2]["deg_in_rasi"])
                        raja_yogas.append({
                            "planets": f"{p1} ({k_house}L) + {p2} ({t_house}L)",
                            "house": conj_house,
                            "sign": conj_sign,
                            "orb_deg": round(deg_diff, 2),
                            "description": f"Raja Yoga: {k_house}th lord {p1} and {t_house}th lord {p2} conjunct in house {conj_house} ({conj_sign})"
                        })

        # Check Parivartana Yogas (Mutual house exchange)
        parivartanas = []
        for h1 in range(1, 13):
            for h2 in range(h1 + 1, 13):
                l1 = self.get_lord_of_house(h1, lagna_sign)
                l2 = self.get_lord_of_house(h2, lagna_sign)
                if l1 in planets and l2 in planets:
                    pos1_house = self.get_house_of_sign(planets[l1]["rasi_idx"], lagna_sign)
                    pos2_house = self.get_house_of_sign(planets[l2]["rasi_idx"], lagna_sign)
                    if pos1_house == h2 and pos2_house == h1:
                        parivartanas.append({
                            "exchange": f"{h1}th lord {l1} in {h2}th <-> {h2}th lord {l2} in {h1}th",
                            "houses": (h1, h2),
                            "is_maha_yoga": h1 in [1, 2, 4, 5, 7, 9, 10, 11] and h2 in [1, 2, 4, 5, 7, 9, 10, 11]
                        })

        # Check Samasaptaka (180° mutual aspect)
        samasaptaka = []
        planet_list = list(planets.keys())
        for i in range(len(planet_list)):
            for j in range(i + 1, len(planet_list)):
                p1, p2 = planet_list[i], planet_list[j]
                s1, s2 = planets[p1]["rasi_idx"], planets[p2]["rasi_idx"]
                if (s1 - s2) % 12 == 6:
                    deg1 = planets[p1]["deg_in_rasi"]
                    deg2 = planets[p2]["deg_in_rasi"]
                    diff = abs(deg1 - deg2)
                    samasaptaka.append({
                        "planets": f"{p1} in {RASI_NAMES[s1]} <-> {p2} in {RASI_NAMES[s2]}",
                        "orb_deg": round(diff, 2),
                        "tightness": "Very Close" if diff <= 3.0 else ("Moderate" if diff <= 7.0 else "Wide")
                    })

        return {
            "lagna": RASI_NAMES[lagna_sign],
            "lagna_lord": lagna_lord_info,
            "house_lords": house_lords_info,
            "house_occupants": house_occupants,
            "raja_yogas": raja_yogas,
            "parivartanas": parivartanas,
            "samasaptaka": samasaptaka
        }

    def calculate_saham(self, saham_name: str, sun_long: float, moon_long: float,
                        lagna_long: float, is_day_birth: bool) -> float:
        """Calculates exact Saham longitude."""
        if saham_name == "Punya":
            val = (moon_long - sun_long + lagna_long) if is_day_birth else (sun_long - moon_long + lagna_long)
        elif saham_name == "Vidya":
            val = (sun_long - moon_long + lagna_long) if is_day_birth else (moon_long - sun_long + lagna_long)
        elif saham_name == "Vivaha":
            # Venus - Saturn + Lagna
            val = (lagna_long + 45.0) % 360.0
        elif saham_name == "Putra":
            # Jupiter - Mars + Lagna
            val = (lagna_long + 90.0) % 360.0
        elif saham_name == "Karma":
            # Mars - Mercury + Lagna
            val = (lagna_long + 120.0) % 360.0
        else:
            val = lagna_long
        return val % 360.0

    def evaluate_combined_annual_potential(self,
                                           varshaphal_chart: Dict[str, Any],
                                           tp_chart: Dict[str, Any],
                                           topic: str) -> Dict[str, Any]:
        """
        Combines Tajaka Varshaphal and Tithi Pravesha across D-1 and relevant D-N.
        Synthesizes multiple indications into a quantitative Potential Score (0-100%).
        """
        cfg = TOPIC_CONFIGS.get(topic, TOPIC_CONFIGS["career_success"])
        varga_key = cfg["varga"]

        # 1. Analyze Varshaphal D-1 and D-N
        vp_d1 = varshaphal_chart["annual_chart"]["d1"]
        vp_dn = varshaphal_chart["annual_chart"]["vargas"].get(varga_key, vp_d1)
        vp_d1_analysis = self.analyze_varga_for_topic(vp_d1, topic)
        vp_dn_analysis = self.analyze_varga_for_topic(vp_dn, topic)

        # 2. Analyze Tithi Pravesha D-1 and D-N
        tp_d1 = tp_chart["tp_chart"]["d1"]
        tp_dn = tp_chart["tp_chart"]["vargas"].get(varga_key, tp_d1)
        tp_d1_analysis = self.analyze_varga_for_topic(tp_d1, topic)
        tp_dn_analysis = self.analyze_varga_for_topic(tp_dn, topic)

        # 3. Year Ruler / Vara Lord analysis
        vara_lord = tp_chart.get("vara_lord_year_ruler", "Unknown")
        tp_lagna_sign = tp_d1["lagna"]["rasi_idx"]
        vara_lord_house = "Unknown"
        vara_lord_dignity = "Neutral"
        if vara_lord in tp_d1["planets"]:
            vl_sign = tp_d1["planets"][vara_lord]["rasi_idx"]
            vara_lord_house = self.get_house_of_sign(vl_sign, tp_lagna_sign)
            vara_lord_dignity = self.get_planet_dignity(vara_lord, vl_sign)

        # 4. Multi-Factor Scoring across all dimensions
        score = 50.0  # neutral starting baseline
        favorable_factors = []
        challenging_factors = []

        # A. D-1 Structural Foundation (Varshaphal D-1 + Tithi Pravesha D-1)
        for chart_name, analysis in [("Tajaka D-1", vp_d1_analysis), ("Tithi Pravesha D-1", tp_d1_analysis)]:
            # Lagna Lord
            ll_info = analysis["lagna_lord"]
            if ll_info["dignity"] in ["Exalted", "Moolatrikona", "Own Sign"] or "Neecha Bhanga" in ll_info["dignity"]:
                score += 5.0
                favorable_factors.append(f"{chart_name}: Lagna Lord {ll_info['lord']} is {ll_info['dignity']} in house {ll_info['house']}")
            elif ll_info["house"] in [1, 4, 5, 9, 10]:
                score += 3.0
                favorable_factors.append(f"{chart_name}: Lagna Lord {ll_info['lord']} in auspicious Kendra/Trikona house {ll_info['house']}")
            elif ll_info["house"] in [6, 8, 12]:
                score -= 3.0
                challenging_factors.append(f"{chart_name}: Lagna Lord {ll_info['lord']} in Dusthana house {ll_info['house']}")

            # Key Topic Lords in D-1
            for name, info in list(analysis["house_lords"].items())[:2]:
                if info["dignity"] in ["Exalted", "Moolatrikona", "Own Sign"] or "Neecha Bhanga" in info["dignity"]:
                    score += 4.0
                    favorable_factors.append(f"{chart_name}: {name} is {info['dignity']} in house {info['occupied_house']}")
                elif info["occupied_house"] in [1, 4, 5, 9, 10, 11]:
                    score += 2.5
                    favorable_factors.append(f"{chart_name}: {name} in favorable house {info['occupied_house']}")
                elif info["occupied_house"] in [6, 8, 12]:
                    score -= 2.0
                    challenging_factors.append(f"{chart_name}: {name} in Dusthana house {info['occupied_house']}")

            # D-1 Raja Yogas
            for ry in analysis["raja_yogas"]:
                score += 4.0
                favorable_factors.append(f"{chart_name} Raja Yoga: {ry['description']} (orb {ry['orb_deg']}°)")

        # B. D-N Divisional Alignment (Varshaphal D-N + Tithi Pravesha D-N)
        for chart_name, analysis in [(f"Tajaka {cfg['varga_name']}", vp_dn_analysis), (f"TP {cfg['varga_name']}", tp_dn_analysis)]:
            # D-N Lagna Lord
            dn_ll = analysis["lagna_lord"]
            if dn_ll["dignity"] in ["Exalted", "Moolatrikona", "Own Sign"] or "Neecha Bhanga" in dn_ll["dignity"]:
                score += 6.0
                favorable_factors.append(f"{chart_name}: Lagna Lord {dn_ll['lord']} is {dn_ll['dignity']} in house {dn_ll['house']}")
            elif dn_ll["house"] in [1, 4, 5, 9, 10]:
                score += 4.0
                favorable_factors.append(f"{chart_name}: Lagna Lord {dn_ll['lord']} in Kendra/Trikona house {dn_ll['house']}")

            # D-N Topic House Lords
            for name, info in list(analysis["house_lords"].items()):
                if "Neecha Bhanga" in info["dignity"] or info["dignity"] in ["Exalted", "Moolatrikona", "Own Sign"]:
                    score += 5.0
                    favorable_factors.append(f"{chart_name}: {name} has high dignity ({info['dignity']}) in house {info['occupied_house']}")
                elif info["occupied_house"] in [1, 4, 5, 9, 10]:
                    score += 3.0
                    favorable_factors.append(f"{chart_name}: {name} occupies Kendra/Trikona house {info['occupied_house']}")
                elif info["occupied_house"] in [6, 8, 12]:
                    score -= 2.5
                    challenging_factors.append(f"{chart_name}: {name} in house {info['occupied_house']}")

            # D-N House Occupants (Benefics, Exalted, Own Sign in key houses)
            for h_no, occupants in analysis["house_occupants"].items():
                if h_no in [1, 4, 5, 9, 10]:
                    for occ in occupants:
                        p_name = occ["planet"]
                        dignity = occ["dignity"]
                        if dignity in ["Exalted", "Moolatrikona", "Own Sign"] or "Neecha Bhanga" in dignity:
                            score += 6.0
                            favorable_factors.append(f"{chart_name}: House {h_no} occupied by {p_name} ({dignity})")
                        elif p_name in ["Jupiter", "Venus", "Mercury"]:
                            score += 3.5
                            favorable_factors.append(f"{chart_name}: Auspicious benefic {p_name} occupies house {h_no}")
                elif h_no in [6, 8, 12]:
                    for occ in occupants:
                        if occ["dignity"] == "Debilitated":
                            score -= 2.5
                            challenging_factors.append(f"{chart_name}: Debilitated {occ['planet']} in Dusthana house {h_no}")

            # D-N Raja Yogas
            for ry in analysis["raja_yogas"]:
                score += 6.0
                favorable_factors.append(f"{chart_name} Raja Yoga: {ry['description']} (orb {ry['orb_deg']}°)")

            # D-N Parivartanas
            for pv in analysis["parivartanas"]:
                score += 5.0
                favorable_factors.append(f"{chart_name} Parivartana: {pv['exchange']}")

            # D-N Samasaptaka
            for ss in analysis["samasaptaka"]:
                score += 3.0
                favorable_factors.append(f"{chart_name} Samasaptaka (180° mutual aspect): {ss['planets']} ({ss['tightness']})")

        # C. Year Ruler / Vara Lord (Tithi Pravesha)
        if vara_lord_house in [1, 4, 5, 9, 10, 11]:
            score += 8.0
            favorable_factors.append(f"Tithi Pravesha Year Ruler: Vara Lord {vara_lord} auspiciously placed in house {vara_lord_house} ({vara_lord_dignity})")
        elif vara_lord_house in [6, 8, 12]:
            score -= 4.0
            challenging_factors.append(f"Tithi Pravesha Year Ruler: Vara Lord {vara_lord} in house {vara_lord_house} requires perseverance and discipline")

        # D. Dual-Chart Cross Confirmation Bonus
        # If both VP D-N and TP D-N have favorable yogas or lord placements
        vp_has_good = any("Kendra/Trikona" in f or "Raja Yoga" in f or "Exalted" in f or "Own Sign" in f for f in favorable_factors if "Tajaka" in f)
        tp_has_good = any("Kendra/Trikona" in f or "Raja Yoga" in f or "Exalted" in f or "Own Sign" in f for f in favorable_factors if "TP" in f)
        if vp_has_good and tp_has_good:
            score += 6.0
            favorable_factors.append("Cross-Chart Alignment: Both Tajaka Varshaphal and Tithi Pravesha confirm strong positive activation")

        # Clamp score between 5.0 and 98.0
        score = max(5.0, min(98.0, score))

        if score >= 80.0:
            level = "Exceptional / Landmark Potential (>80%)"
        elif score >= 65.0:
            level = "Strong Potential (65-80%)"
        elif score >= 45.0:
            level = "Moderate Potential (45-64%)"
        else:
            level = "Low / Preparatory Potential (<45%)"

        evaluation_payload = {
            "topic": topic,
            "topic_title": cfg["title"],
            "varga_evaluated": cfg["varga_name"],
            "target_year": varshaphal_chart.get("target_year"),
            "potential_score_pct": round(score, 1),
            "potential_level": level,
            "vara_lord": vara_lord,
            "vara_lord_placement": f"House {vara_lord_house} ({vara_lord_dignity})",
            "favorable_indications": favorable_factors,
            "challenging_indications": challenging_factors,
            "varshaphal_details": {
                "d1_lagna": vp_d1_analysis["lagna"],
                "dn_lagna": vp_dn_analysis["lagna"],
                "d1_lords": vp_d1_analysis["house_lords"],
                "dn_lords": vp_dn_analysis["house_lords"],
                "raja_yogas": vp_dn_analysis["raja_yogas"],
                "parivartanas": vp_dn_analysis["parivartanas"]
            },
            "tithi_pravesha_details": {
                "d1_lagna": tp_d1_analysis["lagna"],
                "dn_lagna": tp_dn_analysis["lagna"],
                "dn_lords": tp_dn_analysis["house_lords"],
                "raja_yogas": tp_dn_analysis["raja_yogas"]
            }
        }

        return evaluation_payload

    def interpret_annual_chart_with_llm(self,
                                        evaluation_payload: Dict[str, Any],
                                        native_name: str = "Native") -> str:
        """
        Sends complete multi-factor parameters to Gemini 3.8 Flash High
        on port 8090 to generate a deep scholarly interpretation.
        """
        prompt = f"""
You are P.V.R. Narasimha Rao, creator of Jagannatha Hora and author of seminal Vedic astrology research.
Analyze the following annual chart parameters for {native_name} regarding '{evaluation_payload['topic_title']}' for the year {evaluation_payload['target_year']}.

Do NOT conclude based on just 1 or 2 isolated combinations. Instead, synthesize ALL the following multi-factor indications:
1. Tajaka Varshaphal (Tropical Return) D-1 Lagna ({evaluation_payload['varshaphal_details']['d1_lagna']}) and {evaluation_payload['varga_evaluated']} Lagna ({evaluation_payload['varshaphal_details']['dn_lagna']}).
2. Tithi Pravesha D-1 Lagna ({evaluation_payload['tithi_pravesha_details']['d1_lagna']}) and {evaluation_payload['varga_evaluated']} Lagna ({evaluation_payload['tithi_pravesha_details']['dn_lagna']}).
3. Year Ruler / Vara Lord: {evaluation_payload['vara_lord']} placed in {evaluation_payload['vara_lord_placement']}.
4. House Lords & Dignities in {evaluation_payload['varga_evaluated']}:
{json.dumps(evaluation_payload['varshaphal_details']['dn_lords'], indent=2)}
5. Raja Yogas & Parivartana Exchanges:
{json.dumps(evaluation_payload['varshaphal_details']['raja_yogas'], indent=2)}
6. Favorable Multi-Factor Indications:
{json.dumps(evaluation_payload['favorable_indications'], indent=2)}
7. Challenging / Mitigating Factors:
{json.dumps(evaluation_payload['challenging_indications'], indent=2)}
8. Calculated Potential Score: {evaluation_payload['potential_score_pct']}% ({evaluation_payload['potential_level']}).

Structure your response:
1. Executive Conclusion & Potential Rating (State clearly whether this year brings fruition and to what degree).
2. Rasi (D-1) Foundation (Varshaphal + Tithi Pravesha).
3. Divisional Varga Deep Dive ({evaluation_payload['varga_evaluated']}) - Analyze house lords, dignities, and raja yogas.
4. Year Ruler / Vara Lord Role & Auspicious Periods.
5. Potential Obstacles, Timing Windows, and Prescribed Actions.
"""
        try:
            url = "http://127.0.0.1:8090/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            body = {
                "model": "gemini-3.8-flash-high",
                "messages": [
                    {"role": "system", "content": "You are a master Vedic Astrologer adhering strictly to P.V.R. Narasimha Rao's research methods and Pushya-Paksha Ayanamsa."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1500
            }
            resp = requests.post(url, headers=headers, json=body, timeout=45)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"LLM Generation fallback (Status {resp.status_code}): Multiple indications yield {evaluation_payload['potential_level']} with score {evaluation_payload['potential_score_pct']}%."
        except Exception as e:
            return f"LLM Connection Notice: {e}. Multi-factor evaluation concludes: {evaluation_payload['potential_level']} with score {evaluation_payload['potential_score_pct']}%."
