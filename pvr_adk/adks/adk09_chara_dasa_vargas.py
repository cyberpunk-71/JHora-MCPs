#!/usr/bin/env python3
"""
ADK-09: Parasara's Chara Dasa in Divisional Charts
--------------------------------------------------
Implements Research Paper 09: "Unlocking the Power of Parasara's Chara Dasa"
By P.V.R. Narasimha Rao (April 14, 2014).

Core Methodological Breakthroughs:
1. Chara Dasa is computed DIRECTLY IN DIVISIONAL CHARTS (D-9 for marriage, D-10 for career,
   D-24 for education, D-7 for children).
2. Seed Sign Selection:
   - Compare the signs containing Lagna, Moon, and Sun in the specific divisional chart.
   - The seed sign is the one whose lord is STRONGEST.
3. Footedness & Dasa Order:
   - Odd-footed signs: Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius.
   - Even-footed signs: Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces.
   - If the 9th house from the seed sign is odd-footed -> Dasa progresses ZODIACALLY.
   - If the 9th house from the seed sign is even-footed -> Dasa progresses ANTI-ZODIACALLY.
4. Dasa Length:
   - Count from dasa sign to its lord (zodiacally if sign is odd-footed, anti-zodiacally if even-footed).
   - Subtract 1 year. (If count is 0, dasa is 12 years).
5. Predictive Rule:
   - Dasa of a sign containing or aspecting (Rasi Drishti) the house lord, exalted planet,
   - or key Karaka triggers the promised life event with exceptional clarity.
"""

from typing import Dict, Any, List, Tuple
from pvr_adk.core.config import (
    ODD_FOOTED_SIGNS, EVEN_FOOTED_SIGNS, RASI_NAMES, PLANET_NAMES
)

# Standard Sign Lords (Aries=Mars ... Pisces=Jupiter)
SIGN_LORDS = [2, 5, 3, 1, 0, 3, 5, 2, 4, 6, 6, 4]

# Jaimini Rasi Drishti mapping:
# Movable (Ar, Cn, Li, Cp) aspects all Fixed except adjacent.
# Fixed (Ta, Le, Sc, Aq) aspects all Movable except adjacent.
# Dual (Ge, Vi, Sg, Pi) aspects all other Dual signs.
RASI_DRISHTI_MAP = {
    0: [4, 7, 10],   # Aries (M) -> Leo, Scorpio, Aquarius (not Taurus)
    1: [3, 6, 9],    # Taurus (F) -> Cancer, Libra, Capricorn (not Aries)
    2: [5, 8, 11],   # Gemini (D) -> Virgo, Sagittarius, Pisces
    3: [1, 7, 10],   # Cancer (M) -> Taurus, Scorpio, Aquarius (not Leo)
    4: [0, 6, 9],    # Leo (F) -> Aries, Libra, Capricorn (not Cancer)
    5: [2, 8, 11],   # Virgo (D) -> Gemini, Sagittarius, Pisces
    6: [1, 4, 10],   # Libra (M) -> Taurus, Leo, Aquarius (not Scorpio)
    7: [0, 3, 9],    # Scorpio (F) -> Aries, Cancer, Capricorn (not Libra)
    8: [2, 5, 11],   # Sagittarius (D) -> Gemini, Virgo, Pisces
    9: [1, 4, 7],    # Capricorn (M) -> Taurus, Leo, Scorpio (not Aquarius)
    10: [0, 3, 6],   # Aquarius (F) -> Aries, Cancer, Libra (not Capricorn)
    11: [2, 5, 8],   # Pisces (D) -> Gemini, Virgo, Sagittarius
}

class ADK09CharaDasaVargas:
    """Agentic Decision Kit for Parasara's Chara Dasa in Divisional Charts."""

    def is_odd_footed(self, sign_idx: int) -> bool:
        return sign_idx in ODD_FOOTED_SIGNS

    def get_stronger_lord(self, sign_idx: int, planets_in_varga: Dict[str, Any]) -> Tuple[str, float]:
        """Returns the primary lord name and estimated strength score."""
        p_id = SIGN_LORDS[sign_idx]
        p_name = PLANET_NAMES[p_id]
        p_data = planets_in_varga.get(p_name)
        if not p_data:
            return p_name, 1.0

        score = 2.0
        # Angular houses / exalted boost
        p_deg = p_data.get("deg_in_rasi", 15.0)
        score += (p_deg / 30.0)  # tie breaker: advancement in sign
        return p_name, score

    def calculate_seed_sign(self, varga_data: Dict[str, Any]) -> Tuple[int, str]:
        """
        PVR Breakthrough: Compare signs containing Lagna, Moon, and Sun.
        The seed sign is the one whose lord is strongest.
        """
        lagna_sign = varga_data["lagna"]["rasi_idx"]
        planets = varga_data["planets"]
        moon_sign = planets["Moon"]["rasi_idx"]
        sun_sign = planets["Sun"]["rasi_idx"]

        candidates = [
            ("Lagna", lagna_sign, self.get_stronger_lord(lagna_sign, planets)),
            ("Moon", moon_sign, self.get_stronger_lord(moon_sign, planets)),
            ("Sun", sun_sign, self.get_stronger_lord(sun_sign, planets))
        ]

        # Sort by strength score descending
        candidates.sort(key=lambda x: x[2][1], reverse=True)
        chosen = candidates[0]
        return chosen[1], f"Derived from {chosen[0]} (Lord {chosen[2][0]} is strongest with score {chosen[2][1]:.2f})"

    def calculate_dasa_length(self, dasa_sign: int, planets_in_varga: Dict[str, Any]) -> int:
        """
        Count from dasa sign to its lord sign, then subtract 1.
        Zodiacal if sign is odd-footed, anti-zodiacal if even-footed.
        """
        lord_name, _ = self.get_stronger_lord(dasa_sign, planets_in_varga)
        lord_sign = planets_in_varga[lord_name]["rasi_idx"]

        if self.is_odd_footed(dasa_sign):
            count = ((lord_sign - dasa_sign) % 12) + 1
        else:
            count = ((dasa_sign - lord_sign) % 12) + 1

        dasa_years = count - 1
        if dasa_years <= 0:
            dasa_years = 12
        return dasa_years

    def generate_chara_dasa_sequence(self, varga_data: Dict[str, Any],
                                      birth_year: int) -> List[Dict[str, Any]]:
        """
        Generates the 12 Chara Dasa sign periods with exact years and date ranges.
        """
        seed_sign, rationale = self.calculate_seed_sign(varga_data)
        planets = varga_data["planets"]

        # 9th house from seed sign
        ninth_from_seed = (seed_sign + 8) % 12
        go_zodiacal = self.is_odd_footed(ninth_from_seed)
        step = 1 if go_zodiacal else -1

        sequence = []
        curr_year = float(birth_year)

        for i in range(12):
            sign_idx = (seed_sign + i * step) % 12
            dasa_len = self.calculate_dasa_length(sign_idx, planets)
            end_year = curr_year + dasa_len

            # Check which planets are in this sign
            planets_in_sign = [
                p_name for p_name, p_d in planets.items()
                if p_d["rasi_idx"] == sign_idx
            ]

            # Check Jaimini aspects
            aspected_signs = RASI_DRISHTI_MAP.get(sign_idx, [])
            planets_aspecting = [
                p_name for p_name, p_d in planets.items()
                if p_d["rasi_idx"] in aspected_signs
            ]

            sequence.append({
                "order": i + 1,
                "sign_index": sign_idx,
                "sign_name": RASI_NAMES[sign_idx],
                "dasa_years": dasa_len,
                "start_year": round(curr_year, 1),
                "end_year": round(end_year, 1),
                "planets_in_sign": planets_in_sign,
                "planets_aspecting": planets_aspecting,
                "aspected_signs": [RASI_NAMES[s] for s in aspected_signs]
            })
            curr_year = end_year

        return sequence

    def evaluate_timing_for_topic(self, chart_data: Dict[str, Any], varga_name: str,
                                  key_planet: str, target_house: int,
                                  birth_year: int) -> Dict[str, Any]:
        """
        Finds the exact Chara Dasa periods that trigger a given topic in the specified varga.
        """
        varga_data = chart_data.get("vargas", {}).get(varga_name)
        if not varga_data:
            return {"error": f"Varga {varga_name} not available"}

        seq = self.generate_chara_dasa_sequence(varga_data, birth_year)
        lagna_sign = varga_data["lagna"]["rasi_idx"]
        target_sign = (lagna_sign + target_house - 1) % 12

        favorable_periods = []
        for period in seq:
            sign_idx = period["sign_index"]
            is_target_sign = (sign_idx == target_sign)
            has_key_planet = (key_planet in period["planets_in_sign"])
            aspects_key_planet = (key_planet in period["planets_aspecting"])
            aspects_target_sign = (target_sign in [RASI_NAMES.index(s) for s in period["aspected_signs"]])

            score = 0
            reasons = []
            if is_target_sign:
                score += 4; reasons.append(f"Dasa is of the {target_house}th house sign ({RASI_NAMES[target_sign]})")
            if has_key_planet:
                score += 3; reasons.append(f"Sign contains key planet {key_planet}")
            if aspects_key_planet:
                score += 2; reasons.append(f"Sign aspects key planet {key_planet} via Jaimini Rasi Drishti")
            if aspects_target_sign:
                score += 2; reasons.append(f"Sign aspects the {target_house}th house sign")

            if score >= 3:
                favorable_periods.append({
                    "period": period,
                    "activation_score": score,
                    "reasons": reasons
                })

        # Sort periods by activation score descending
        favorable_periods.sort(key=lambda x: x["activation_score"], reverse=True)

        return {
            "adk_id": "ADK-09",
            "name": f"Parasara Chara Dasa Engine in {varga_name}",
            "varga": varga_name,
            "target_house": target_house,
            "key_planet": key_planet,
            "most_favorable_periods": favorable_periods,
            "full_sequence": seq,
            "research_reference": "PVR Paper 09: Unlocking the Power of Parasara's Chara Dasa"
        }
