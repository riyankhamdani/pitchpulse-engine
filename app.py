import streamlit as st
import pandas as pd
import random
import time
from mplsoccer import Pitch
from agents import FeatureWorkerAgent, TacticalReasonerAgent, PersonaDispatcherAgent

st.set_page_config(page_title="PitchPulse Studio", layout="wide", page_icon="⚽")

worker_agent = FeatureWorkerAgent()
reasoner_agent = TacticalReasonerAgent()
dispatcher_agent = PersonaDispatcherAgent()

st.title("⚽ PitchPulse: Multi-Agent Match Intelligence")
st.caption("Microsoft + Premier League Hackathon Engine • 3-Agent Collaborative Pipeline")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Studio Controls")
persona_mode = st.sidebar.selectbox("Audience Mode", ["Pundit / Analyst", "Casual Fan (Global)"])
lang_choice = st.sidebar.selectbox("Language Output", ["English", "Bahasa Indonesia", "Español"])

st.sidebar.markdown("---")
# Fitur baru: Toggle Auto-Play
auto_play = st.sidebar.toggle("▶️ Live Auto-Play Stream", value=False)
stream_speed = st.sidebar.slider("Stream Speed (seconds)", 1.0, 5.0, 2.5)

TEAMS = ["Arsenal", "Chelsea"]
EVENT_TYPES = ["Pass", "Tackle", "Interception", "Counter-Attack", "Shot"]

def run_agent_pipeline():
    team = random.choice(TEAMS)
    event_type = random.choice(EVENT_TYPES)
    pressure = random.randint(20, 95)
    
    start_x = round(random.uniform(10, 95), 1)
    start_y = round(random.uniform(5, 63), 1)
    end_x = round(min(105, max(0, start_x + random.uniform(-20, 25))), 1)
    end_y = round(min(68, max(0, start_y + random.uniform(-15, 15))), 1)

    raw_event = {
        "timestamp": time.strftime("%H:%M:%S"),
        "team": team,
        "event_type": event_type,
        "pressure_pct": pressure,
        "start_pos": (start_x, start_y),
        "end_pos": (end_x, end_y)
    }

    enriched = worker_agent.process_event(raw_event)
    tactical_out = reasoner_agent.analyze_phase(enriched, st.session_state.get("history", []))
    narrative = dispatcher_agent.format_output(tactical_out, persona_mode, lang_choice)

    return {
        "Time": enriched["timestamp"],
        "Team": enriched["team"],
        "Event": enriched["event_type"],
        "Pressure": f"{enriched['pressure_pct']}%",
        "Diff_Rating": enriched["difficulty_rating"],
        "State": tactical_out["tactical_state"],
        "Start": enriched["start_pos"],
        "End": enriched["end_pos"],
        "Narrative": narrative,
        "RawPressure": enriched["pressure_pct"]
    }

if "history" not in st.session_state:
    st.session_state.history = [run_agent_pipeline() for _ in range(4)]

col_left, col_right = st.columns([1.1, 1.3])

with col_left:
    st.subheader("📡 Multi-Agent Pipeline Ingestion")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Simulate Match Event", use_container_width=True, disabled=auto_play):
            st.session_state.history.insert(0, run_agent_pipeline())
    with col_btn2:
        if st.button("Reset Feed", use_container_width=True):
            st.session_state.history = [run_agent_pipeline() for _ in range(4)]

    df_table = pd.DataFrame([{
        "Time": e["Time"],
        "Team": e["Team"],
        "Action": e["Event"],
        "Pressure": e["Pressure"],
        "Diff Score": e["Diff_Rating"],
        "Tactical State": e["State"]
    } for e in st.session_state.history])
    st.dataframe(df_table, use_container_width=True, height=240)

    st.markdown("### 📺 Broadcast Lower-Third Overlay")
    latest = st.session_state.history[0]
    st.info(f"**[{latest['Team'].upper()} • {latest['Event'].upper()}]**  \n{latest['Narrative']}")
    st.progress(latest["RawPressure"] / 100, text=f"Defensive Pressure Index: {latest['Pressure']}")

with col_right:
    st.subheader("📍 Live Tactical Radar & Coordinates")
    pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68, 
                  pitch_color='#1a1d24', line_color='#4a5568')
    fig, ax = pitch.draw(figsize=(8, 5))
    
    sx, sy = latest["Start"]
    ex, ey = latest["End"]
    team_color = "#00ff87" if latest["Team"] == "Arsenal" else "#38bdf8"
    
    pitch.arrows(sx, sy, ex, ey, ax=ax, width=3, color=team_color, headwidth=5)
    pitch.scatter(sx, sy, ax=ax, c=team_color, s=130, edgecolors='white', zorder=3)
    ax.set_title(f"Live Vector: {latest['Team']} ({sx}, {sy} -> {ex}, {ey}) | Phase: {latest['State']}", 
                 color='white', fontsize=10, pad=10)
    st.pyplot(fig)

# --- AUTO-PLAY LOGIC ---
if auto_play:
    time.sleep(stream_speed)
    st.session_state.history.insert(0, run_agent_pipeline())
    st.rerun()