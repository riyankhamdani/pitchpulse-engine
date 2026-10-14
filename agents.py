import os
import random
from typing import Dict, Any, List

class FeatureWorkerAgent:
    """Agent 1: Ingests raw coordinates and computes deterministic tactical metrics."""
    def process_event(self, raw_event: Dict[str, Any]) -> Dict[str, Any]:
        sx, sy = raw_event["start_pos"]
        ex, ey = raw_event["end_pos"]
        
        # Euclidean distance of ball progression
        distance = round(((ex - sx)**2 + (ey - sy)**2)**0.5, 2)
        
        # Pass difficulty formula based on pressure and distance
        pressure = raw_event["pressure_pct"]
        difficulty_score = round(min(1.0, (distance / 60.0) * 0.5 + (pressure / 100.0) * 0.5), 2)
        
        raw_event.update({
            "progression_distance_m": distance,
            "difficulty_rating": difficulty_score,
            "is_high_risk": difficulty_score > 0.65
        })
        return raw_event

class TacticalReasonerAgent:
    """Agent 2: Evaluates tactical context, turnovers, and structural vulnerability."""
    def __init__(self):
        self.api_key = os.environ.get("GITHUB_TOKEN")

    def analyze_phase(self, enriched_event: Dict[str, Any], recent_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        team = enriched_event["team"]
        event_type = enriched_event["event_type"]
        pressure = enriched_event["pressure_pct"]
        is_risky = enriched_event["is_high_risk"]

        # If GitHub Token is available, can query Azure Models; otherwise fallback to heuristic
        if pressure >= 75 and is_risky:
            tactical_state = "High Chaos / Vulnerability"
            reasoning = f"Severe defensive overload on {team}. Structural collapse detected with high-risk turnover probability."
        elif pressure < 40 and enriched_event["progression_distance_m"] > 25:
            tactical_state = "Controlled Progression"
            reasoning = f"{team} exploited open vertical channel, bypassing second defensive line with sustained control."
        else:
            tactical_state = "Stable Circulation"
            reasoning = f"{team} sustaining possession rhythm in neutral game phase."

        return {
            "tactical_state": tactical_state,
            "core_reasoning": reasoning
        }

class PersonaDispatcherAgent:
    """Agent 3: Translates structured tactical reasoning into broadcast-ready and fan-centric narratives."""
    def format_output(self, tactical_payload: Dict[str, Any], persona: str, language: str) -> str:
        state = tactical_payload["tactical_state"]
        reason = tactical_payload["core_reasoning"]

        if persona == "Pundit / Analyst":
            return f"[{state.upper()}] {reason}"
        
        # Casual Fan Mode
        if language == "Bahasa Indonesia":
            if "Chaos" in state:
                return "Pertahanan panik! Tekanan lawan memaksa kesalahan fatal di area krusial."
            elif "Controlled" in state:
                return "Penetrasi luar biasa! Umpan matang langsung membelah blok pertahanan lawan."
            return "Permainan berjalan seimbang, kedua tim saling membaca tempo."
            
        elif language == "Español":
            if "Chaos" in state:
                return "¡Alarma defensiva! Pérdida bajo asedio y riesgo total de contraataque."
            elif "Controlled" in state:
                return "¡Qué visión de juego! Rompen líneas defensivas con absoluta soltura."
            return "Control de ritmo paciente en el medio del campo."
            
        else: # English
            if "Chaos" in state:
                return "Massive danger! Defensive shape broken under immense pressing."
            elif "Controlled" in state:
                return "Brilliant vision! Slicing through the opponent's defensive structure."
            return "Steady tempo and controlled ball retention."
