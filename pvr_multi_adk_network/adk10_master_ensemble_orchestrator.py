"""
ADK-10: Master Ensemble Orchestrator & Multi-Agent Network
==========================================================
Executes the multi-agent dependency graph, routes cross-ADK context, collects
individual domain agent LLM outputs, and executes the final Master Synthesis LLM call.
"""

import json
import requests
from typing import Dict, Any, List, Optional
from pvr_multi_adk_network.base_adk import DEFAULT_MODEL, LLM_PROXY_URL
from pvr_multi_adk_network.adk04_tajaka_agent import ADK04TajakaAgent
from pvr_multi_adk_network.adk05_tithi_pravesha_agent import ADK05TithiPraveshaAgent
from pvr_annual_engine.annual_convergence_evaluator import PVRAnnualConvergenceEvaluator

class MasterEnsembleOrchestrator:
    """Master Multi-Agent Orchestrator for PVR Research Methodology."""

    def __init__(self):
        self.tajaka_agent = ADK04TajakaAgent()
        self.tp_agent = ADK05TithiPraveshaAgent()
        self.evaluator = PVRAnnualConvergenceEvaluator()

    def run_multi_agent_prediction(self, birth_year: int, birth_month: int, birth_day: int,
                                   birth_hour: int, birth_minute: int, birth_second: float,
                                   target_year: int, latitude: float, longitude: float, timezone: float = 5.5,
                                   topic: str = "career_success",
                                   native_label: str = "Native") -> Dict[str, Any]:
        """
        Executes the full multi-agent pipeline with interlinked context passing
        and final master synthesis.
        """
        # Step 1: Execute Tajaka Agent with initial context
        tajaka_result = self.tajaka_agent.execute(
            birth_year, birth_month, birth_day,
            birth_hour, birth_minute, birth_second,
            target_year, latitude, longitude, timezone,
            topic=topic,
            cross_adk_context={"query_topic": topic, "stage": "solar_return_audit"}
        )

        # Step 2: Execute Tithi Pravesha Agent incorporating Tajaka findings
        tp_result = self.tp_agent.execute(
            birth_year, birth_month, birth_day,
            birth_hour, birth_minute, birth_second,
            target_year, latitude, longitude, timezone,
            topic=topic,
            cross_adk_context={
                "query_topic": topic,
                "tajaka_agent_verdict": tajaka_result["agent_llm_evaluation"].get("domain_verdict"),
                "tajaka_score_pct": tajaka_result["agent_llm_evaluation"].get("strength_score_pct"),
                "tajaka_muntha": tajaka_result["deterministic_data"].get("muntha")
            }
        )

        # Step 3: Mathematical convergence evaluation
        conv_payload = self.evaluator.evaluate_combined_annual_potential(
            tajaka_result["deterministic_data"],
            tp_result["deterministic_data"],
            topic
        )

        # Step 4: Final Master Synthesis LLM Call
        master_prompt = f"""
You are the Master Astrological Synthesizer embodying P.V.R. Narasimha Rao's complete multi-method research tradition.

You have received the specialized evaluations from our dedicated domain agent sub-systems for {native_label} on topic '{conv_payload['topic_title']}' for the year {target_year}:

--- AGENT 1: TAJAKA VARSHAPHAL SPECIALIST (ADK-04) ---
{json.dumps(tajaka_result['agent_llm_evaluation'], indent=2)}

--- AGENT 2: TITHI PRAVESHA SPECIALIST (ADK-05) ---
{json.dumps(tp_result['agent_llm_evaluation'], indent=2)}

--- MATHEMATICAL MULTI-FACTOR CONVERGENCE AUDIT ---
Potential Score: {conv_payload['potential_score_pct']}% ({conv_payload['potential_level']})
Favorable Factors ({len(conv_payload['favorable_indications'])}):
{json.dumps(conv_payload['favorable_indications'], indent=2)}
Challenging Factors ({len(conv_payload['challenging_indications'])}):
{json.dumps(conv_payload['challenging_indications'], indent=2)}

Synthesize these independent agent findings into a final, unified scholarly judgment:
1. Executive Consensus & Potential Rating (Definitive fruition statement).
2. Physical Stage vs. Consciousness Resonance (Harmonizing Tajaka Solar and TP Soli-Lunar findings).
3. Divisional Execution Engine ({conv_payload['varga_evaluated']}).
4. Year Ruler Mandate & Critical Turning Points.
5. Final Strategic Directive & Remedial Prescriptions.
"""

        try:
            headers = {"Content-Type": "application/json"}
            body = {
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are P.V.R. Narasimha Rao conducting the final master synthesis of all multi-agent astrological streams."},
                    {"role": "user", "content": master_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1500
            }
            resp = requests.post(LLM_PROXY_URL, headers=headers, json=body, timeout=45)
            master_synthesis = resp.json()["choices"][0]["message"]["content"] if resp.status_code == 200 else "Master synthesis fallback."
        except Exception as e:
            master_synthesis = f"Master synthesis connection notice: {e}"

        return {
            "orchestrator_status": "success",
            "target_year": target_year,
            "topic": topic,
            "tajaka_agent_output": tajaka_result,
            "tithi_pravesha_agent_output": tp_result,
            "mathematical_convergence": conv_payload,
            "final_master_synthesis": master_synthesis
        }
