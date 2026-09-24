"""
ADK-05: Tithi Pravesha Dedicated Agent
======================================
Specialized Agent for Annual Soli-Lunar Return & Year Ruler Horoscopy (Paper 05).
Receives incoming context from ADK-02 (Natal Vargas), ADK-03/09 (Active Dasas),
and ADK-04 (Tajaka Solar Return), computes the preceding New Moon Soli-Lunar return,
and uses its dedicated LLM to evaluate the Year Ruler (Varadhipati) and emotional/karmic timing.
"""

from typing import Dict, Any, Optional
from pvr_multi_adk_network.base_adk import BasePVRADK
from pvr_annual_engine.tithi_pravesha_adk import ADK05TithiPravesha

class ADK05TithiPraveshaAgent(BasePVRADK):
    def __init__(self):
        system_prompt = (
            "You are the Tithi Pravesha Specialist Agent in P.V.R. Narasimha Rao's multi-agent system. "
            "Your expertise is Annual Soli-Lunar Return horoscopy (Paper 05). You analyze the preceding New Moon "
            "tropical sign, the exact natal tithi angle return, the Weekday Lord (Vara Lord / Varadhipati) ruling "
            "the year, its house placement and dignity in TP D-1 and D-N, and the emotional/experiential fruition "
            "of the year in resonance with Tajaka solar return and active dasas."
        )
        super().__init__(
            adk_id="ADK-05",
            name="Tithi Pravesha Specialist Agent",
            paper_ref="PVR Research Paper 05: Re-defining Tithi Pravesha Chart",
            system_prompt=system_prompt
        )
        self.engine = ADK05TithiPravesha()

    def execute(self, birth_year: int, birth_month: int, birth_day: int,
                birth_hour: int, birth_minute: int, birth_second: float,
                target_year: int, latitude: float, longitude: float, timezone: float = 5.5,
                topic: str = "career_success",
                cross_adk_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Calculates Tithi Pravesha chart deterministically and invokes dedicated agent LLM.
        """
        tp_calc = self.engine.generate_tp_chart(
            birth_year, birth_month, birth_day,
            birth_hour, birth_minute, birth_second,
            target_year, latitude, longitude, timezone
        )

        agent_evaluation = self.invoke_agent_llm(tp_calc, cross_adk_context)

        return {
            "adk_id": self.adk_id,
            "deterministic_data": tp_calc,
            "agent_llm_evaluation": agent_evaluation
        }
