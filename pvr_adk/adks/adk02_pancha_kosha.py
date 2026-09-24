#!/usr/bin/env python3
"""
ADK-02: Upanishadic Pancha Koshas & Multi-Layered Divisional Interpretation
---------------------------------------------------------------------------
Implements Research Paper 02: "Upanishadic Pancha Koshas & Vedic Astrology Charts"
By P.V.R. Narasimha Rao (June 21, 2015).

Core Architectural Mapping:
1. Annamaya Kosha (Sheath of Matter):
   - Charts: D-1 to D-12 (D-1, D-2, D-3, D-4, D-7, D-9, D-10, D-12)
   - Scope: Tangible physical existence, body, spouse, job, physical children, parents.
2. Praanamaya Kosha (Sheath of Life Force / Praana):
   - Charts: D-13 to D-24 (D-16, D-20, D-24)
   - Seed Houses: 4th, 8th, 12th (trikonas of spending)
   - Scope: How praana is spent for comfort (D-16), spiritual evolution (D-20), knowledge (D-24).
3. Manomaya Kosha (Sheath of Mind):
   - Charts: D-25 to D-36 (D-27, D-30)
   - Seed Houses: 3rd & 6th (initiative & fighting)
   - Scope: Sankalpa/Vikalpa (D-27), fighting internal enemies/shadripus (D-30).
4. Vijnanamaya Kosha (Sheath of Higher Intellect):
   - Charts: D-37 to D-48 (D-40, D-45)
   - Seed Houses: 4th (Sukha) & 9th (Dharma)
   - Scope: Subtle awareness of Cosmic Rhythm / Ritam (D-40), adherence to Truth / Satyam (D-45).
5. Aanandamaya Kosha (Sheath of Bliss / Causal Body):
   - Charts: D-49 to D-60 (D-60)
   - Seed House: 12th (Moksha/Bondage)
   - Scope: Root causal motivations, what the soul desires and enjoys at the deepest level.
"""

from typing import Dict, Any, List, Optional
from pvr_adk.core.config import PANCHA_KOSHA_MAP, PLANET_NAMES, RASI_NAMES
from pvr_adk.core.chart_engine import get_house_of_planet

class ADK02PanchaKosha:
    """Agentic Decision Kit for Pancha Kosha Layered Astrological Analysis."""

    def __init__(self):
        self.kosha_map = PANCHA_KOSHA_MAP

    def classify_chart_to_kosha(self, divisional_factor: int) -> Dict[str, Any]:
        """Maps any divisional chart factor to its Upanishadic Kosha."""
        for kosha_name, data in self.kosha_map.items():
            if divisional_factor in data["charts"]:
                return {
                    "divisional_factor": divisional_factor,
                    "kosha": kosha_name,
                    "sheath_nature": data["sheath"],
                    "description": data["description"]
                }
        return {
            "divisional_factor": divisional_factor,
            "kosha": "Unknown",
            "sheath_nature": "General",
            "description": "Standard divisional chart"
        }

    def evaluate_kosha_layers(self, chart_data: Dict[str, Any], query_topic: str) -> Dict[str, Any]:
        """
        Interprets a query topic across the 5 Upanishadic Koshas.
        Topics: 'career', 'marriage', 'spirituality', 'education', 'fame_and_ritam'
        """
        vargas = chart_data.get("vargas", {})
        analysis = {}

        if query_topic in ["career", "workplace"]:
            # Annamaya layer: D-10
            d10 = vargas.get("D10")
            # Praanamaya layer: D-24 (intellect applied)
            d24 = vargas.get("D24")
            # Vijnanamaya layer: D-40 (smoothness/alignment with cosmic rhythm)
            d40 = vargas.get("D40")
            # Aanandamaya layer: D-60 (soul desire)
            d60 = vargas.get("D60")

            analysis["Annamaya_D10_Workplace"] = self._analyze_varga(d10, "10th", "Sun", "Saturn")
            analysis["Praanamaya_D24_Knowledge"] = self._analyze_varga(d24, "5th", "Mercury", "Jupiter")
            analysis["Vijnanamaya_D40_Ritam"] = self._analyze_varga(d40, "1st", "Jupiter", "Venus")
            analysis["Aanandamaya_D60_SoulMotivation"] = self._analyze_varga(d60, "10th", "Sun", "Mercury")

        elif query_topic in ["education", "academics"]:
            # Praanamaya layer: D-24 (core learning)
            d24 = vargas.get("D24")
            # Annamaya layer: D-4 (basic comforts/school)
            d4 = vargas.get("D4")
            # Vijnanamaya layer: D-40 (flow with exams)
            d40 = vargas.get("D40")

            analysis["Praanamaya_D24_Siddhamsa"] = self._analyze_varga(d24, "5th", "Jupiter", "Mercury")
            analysis["Annamaya_D4_Foundation"] = self._analyze_varga(d4, "4th", "Moon", "Mercury")
            analysis["Vijnanamaya_D40_ExamRhythm"] = self._analyze_varga(d40, "5th", "Jupiter", "Sun")

        elif query_topic in ["marriage", "relationships"]:
            # Annamaya layer: D-9 (physical marriage)
            d9 = vargas.get("D9")
            # Praanamaya layer: D-16 (happiness/pleasure)
            d16 = vargas.get("D16")
            # Manomaya layer: D-27 (mental affinity)
            d27 = vargas.get("D27")

            analysis["Annamaya_D9_Navamsa"] = self._analyze_varga(d9, "7th", "Venus", "Jupiter")
            analysis["Praanamaya_D16_Comfort"] = self._analyze_varga(d16, "4th", "Venus", "Moon")
            analysis["Manomaya_D27_MentalBond"] = self._analyze_varga(d27, "7th", "Moon", "Venus")

        elif query_topic in ["spirituality", "sadhana"]:
            # Praanamaya layer: D-20 (sadhana/upasana)
            d20 = vargas.get("D20")
            # Manomaya layer: D-30 (overcoming shadripus)
            d30 = vargas.get("D30")
            # Vijnanamaya layer: D-45 (satyam/truth)
            d45 = vargas.get("D45")
            # Aanandamaya layer: D-60 (mukti motivation)
            d60 = vargas.get("D60")

            analysis["Praanamaya_D20_Upasana"] = self._analyze_varga(d20, "8th", "Ketu", "Jupiter")
            analysis["Manomaya_D30_Shadripus"] = self._analyze_varga(d30, "6th", "Saturn", "Mars")
            analysis["Vijnanamaya_D45_Satyam"] = self._analyze_varga(d45, "9th", "Sun", "Jupiter")
            analysis["Aanandamaya_D60_LiberationDesire"] = self._analyze_varga(d60, "12th", "Ketu", "Moon")

        return {
            "adk_id": "ADK-02",
            "name": "Upanishadic Pancha Koshas Interpreter",
            "query_topic": query_topic,
            "analysis_by_kosha": analysis,
            "research_reference": "PVR Paper 02: Upanishadic Pancha Koshas & Vedic Astrology Charts"
        }

    def _analyze_varga(self, varga_data: Optional[Dict[str, Any]], key_house_str: str,
                       karaka1: str, karaka2: str) -> Dict[str, Any]:
        if not varga_data:
            return {"status": "Varga data unavailable"}
        lagna = varga_data["lagna"]
        planets = varga_data["planets"]
        
        # Check karaka placements from Lagna
        k1_house = get_house_of_planet(planets[karaka1]["rasi_idx"], lagna["rasi_idx"]) if karaka1 in planets else None
        k2_house = get_house_of_planet(planets[karaka2]["rasi_idx"], lagna["rasi_idx"]) if karaka2 in planets else None

        # Check kendra/trikona strength
        k1_auspicious = k1_house in [1, 4, 5, 7, 9, 10, 11] if k1_house else False
        k2_auspicious = k2_house in [1, 4, 5, 7, 9, 10, 11] if k2_house else False

        return {
            "lagna": lagna["rasi_name"],
            "lagna_degree": round(lagna["deg_in_rasi"], 2),
            "key_focus_house": key_house_str,
            "karaka_1": {"name": karaka1, "house_from_lagna": k1_house, "is_auspicious": k1_auspicious},
            "karaka_2": {"name": karaka2, "house_from_lagna": k2_house, "is_auspicious": k2_auspicious},
            "overall_varga_tone": "Favorable" if (k1_auspicious and k2_auspicious) else "Mixed" if (k1_auspicious or k2_auspicious) else "Challenging"
        }
