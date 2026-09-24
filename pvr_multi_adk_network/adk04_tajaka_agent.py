"""
ADK-04: Tajaka Varshaphal Dedicated Agent
=========================================
Specialized Agent for Annual Tropical Solar Return (Paper 04).
Receives incoming context from ADK-02 (Natal Vargas), ADK-03/09 (Active Dasas),
and ADK-08 (Stationary Transits), computes tropical return, Sahams, and Ithasala yogas,
and uses its dedicated LLM to recognize Tajaka patterns.
"""

from typing import Dict, Any, Optional
from pvr_multi_adk_network.base_adk import BasePVRADK
from pvr_annual_engine.tajaka_adk import ADK04TajakaVarshaphal

class ADK04TajakaAgent(BasePVRADK):
    def __init__(self):
        system_prompt = (
            "You are the Tajaka Varshaphal Specialist Agent in P.V.R. Narasimha Rao's multi-agent system. "
            "Your expertise is Tropical Solar Return horoscopy (Paper 04). You analyze Muntha, Sahams (Punya, Vidya, "
            "Karma, Vivaha, Putra, Paradesa), Deeptamsha aspect orbs, applying/separating Ithasala/Easarapha yogas, "
            "and tropical return D-1 and D-N placements. You synthesize how the annual solar return unlocks "
            "or constrains the promises of the natal chart and active dasa periods."
        )
        super().__init__(
            adk_id="ADK-04",
            name="Tajaka Varshaphal Specialist Agent",
            paper_ref="PVR Research Paper 04: Re-defining Tajaka Varshaphal Charts",
            system_prompt=system_prompt
        )
        self.engine = ADK04TajakaVarshaphal()

    def execute(self, birth_year: int, birth_month: int, birth_day: int,
                birth_hour: int, birth_minute: int, birth_second: float,
                target_year: int, latitude: float, longitude: float, timezone: float = 5.5,
                topic: str = "career_success",
                cross_adk_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculates Tajaka chart deterministically and invokes dedicated agent LLM.
        """
        vp_calc = self.engine.generate_varshaphal_chart(
            birth_year, birth_month, birth_day,
            birth_hour, birth_minute, birth_second,
            target_year, latitude, longitude, timezone
        )

        agent_evaluation = self.invoke_agent_llm(vp_calc, cross_adk_context)

        return {
            "adk_id": self.adk_id,
            "deterministic_data": vp_calc,
            "agent_llm_evaluation": agent_evaluation
        }
