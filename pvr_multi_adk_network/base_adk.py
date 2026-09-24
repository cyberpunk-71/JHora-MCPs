"""
Base ADK Module for Multi-Agent PVR Network
===========================================
Provides standardized mathematical execution, context passing, and dedicated
LLM agent invocation via Gemini 3.8 Flash High (Port 8090).
"""

import json
import requests
from typing import Dict, Any, List, Optional

LLM_PROXY_URL = "http://127.0.0.1:8090/v1/chat/completions"
DEFAULT_MODEL = "gemini-3.8-flash-high"

class BasePVRADK:
    """Base class for all specialized PVR Astrological ADKs."""

    def __init__(self, adk_id: str, name: str, paper_ref: str, system_prompt: str):
        self.adk_id = adk_id
        self.name = name
        self.paper_ref = paper_ref
        self.system_prompt = system_prompt

    def invoke_agent_llm(self, structured_data: Dict[str, Any], context_from_other_adks: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sends the ADK's deterministic calculation payload and incoming context
        from other ADKs to its dedicated LLM agent.
        """
        prompt_payload = {
            "adk_id": self.adk_id,
            "adk_name": self.name,
            "research_reference": self.paper_ref,
            "deterministic_calculation": structured_data,
            "incoming_cross_adk_context": context_from_other_adks or {}
        }

        user_prompt = f"""
You are the dedicated {self.name} Agent operating under P.V.R. Narasimha Rao's research methodology ({self.paper_ref}).

Analyze the following deterministic calculation data and incoming cross-ADK context:
{json.dumps(prompt_payload, indent=2)}

Provide your specialized astrological evaluation in structured JSON format with the following keys:
1. "domain_verdict": Clear statement of findings for your domain.
2. "pattern_highlights": Key astrological combinations and yogas identified.
3. "strength_score_pct": Score from 0.0 to 100.0 indicating positive potential or activation strength.
4. "supportive_factors": List of specific supportive factors.
5. "friction_factors": List of specific challenges or mitigating points.
6. "cross_adk_insights": How your findings reinforce or modulate the inputs received from other ADKs.
7. "scholarly_notes": Concise rationale adhering strictly to PVR's published principles.
"""

        try:
            headers = {"Content-Type": "application/json"}
            body = {
                "model": DEFAULT_MODEL,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 1200
            }
            resp = requests.post(LLM_PROXY_URL, headers=headers, json=body, timeout=45)
            if resp.status_code == 200:
                raw_content = resp.json()["choices"][0]["message"]["content"]
                # Try to extract JSON if enclosed in code block
                cleaned = raw_content.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].split("```")[0].strip()
                try:
                    parsed = json.loads(cleaned)
                    return parsed
                except Exception:
                    return {
                        "domain_verdict": raw_content[:200],
                        "raw_agent_response": raw_content,
                        "strength_score_pct": 75.0
                    }
            else:
                return {
                    "domain_verdict": f"Agent LLM status {resp.status_code}",
                    "strength_score_pct": 50.0
                }
        except Exception as e:
            return {
                "domain_verdict": f"Agent LLM connection notice: {e}",
                "strength_score_pct": 50.0
            }
