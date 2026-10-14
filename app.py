import streamlit as st
import pandas as pd
import random
import time
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="PitchPulse Studio", layout="wide", page_icon="⚽")

# Custom CSS styling ala broadcast feed
st.markdown("""
<style>
    .metric-card {
        background-color: #0e1117;
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #00ff87;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚽ PitchPulse: Real-Time Tactical Stream")
st.caption("Microsoft + Premier League Hackathon Prototype — Powered by Synthetic Match Intelligence")

# Sidebar Configuration
st.sidebar.header("🕹️ Match Feed Controls")
persona_mode = st.sidebar.selectbox("Audience Mode", ["Pundit / Analyst", "Casual Fan (Global)"])
lang_choice = st.sidebar.selectbox("Language Output", ["English", "Bahasa Indonesia", "Español"])

TEAMS = ["Arsenal", "Chelsea"]
EVENT_TYPES = ["Pass", "Tackle", "Shot", "Counter-Attack", "Interception"]

def generate_tactical_event():
    team = random.choice(TEAMS)
    event_type = random.choice(EVENT_TYPES)
    pressure = random.randint(15, 95)
    
    # Koordinat lapangan sepak bola standar (105 x 68 meter)
    start_x = round(random.uniform(10, 95), 1)
    start_y = round(random.uniform(5, 63), 1)
    end_x = round(min(105, max(0, start_x + random.uniform(-20, 25))), 1)
    end_y = round(min(68, max(0, start_y + random.uniform(-15, 15))), 1)
    
    # Multi-Persona Context Reasoning
    if persona_mode == "Pundit / Analyst":
        if pressure > 70:
            tactical_insight = f"High defensive transition risk. Defensive line overloaded in zone 14 ({pressure}% pressure)."
        else:
            tactical_insight = f"Progressive build-up maintained. Efficient vertical circulation detected."
    else:
        # Casual Fan Mode
        if lang_choice == "Bahasa Indonesia":
            tactical_insight = "Chelsea dalam bahaya! Lini pertahanan mulai goyah akibat tekanan bertubi-tubi." if pressure > 70 else "Membangun serangan dengan tenang dari lini belakang."
        elif lang_choice == "Español":
            tactical_insight = "¡Peligro defensivo! Presión sofocante en el último tercio." if pressure > 70 else "Construcción paciente desde el fondo."
        else:
            tactical_insight = "Massive pressure! The defense is on the verge of breaking." if pressure > 70 else "Calm, controlled ball circulation."

    return {
        "Timestamp": time.strftime("%H:%M:%S"),
        "Team": team,
        "Event": event_type,
        "Pressure (%)": pressure,
        "Start": (start_x, start_y),
        "End": (end_x, end_y),
        "Insight": tactical_insight
    }

# Session State Storage
if "event_log" not in st.session_state:
    st.session_state.event_log = [generate_tactical_event() for _ in range(4)]

col_stream, col_viz = st.columns([1.1, 1.3])

with col_stream:
    st.subheader("📡 Real-Time Match Events")
    
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("Simulate Next Event", use_container_width=True):
            st.session_state.event_log.insert(0, generate_tactical_event())
    with btn_col2:
        if st.button("Reset Feed", use_container_width=True):
            st.session_state.event_log = [generate_tactical_event() for _ in range(4)]

    # Display tabular event history
    display_df = pd.DataFrame([
        {
            "Time": e["Timestamp"],
            "Team": e["Team"],
            "Event": e["Event"],
            "Pressure": f"{e['Pressure (%)']}%",
            "Insight": e["Insight"]
        } for e in st.session_state.event_log
    ])
    st.dataframe(display_df, use_container_width=True, height=260)
    
    # Broadcast Lower-Third Card
    st.markdown("### 📺 Broadcast Lower-Third Overlay")
    latest = st.session_state.event_log[0]
    st.info(f"**[{latest['Team'].upper()} • {latest['Event'].upper()}]**  \n{latest['Insight']}")
    st.progress(latest["Pressure (%)"] / 100, text=f"Defensive Pressure Intensity: {latest['Pressure (%)']}%")

with col_viz:
    st.subheader("📍 Live Tactical Radar & Coordinates")
    
    # Rendering visual 2D pitch using mplsoccer
    pitch = Pitch(pitch_type='custom', pitch_length=105, pitch_width=68, 
                  pitch_color='#1a1d24', line_color='#4a5568')
    fig, ax = pitch.draw(figsize=(8, 5))
    
    latest_event = st.session_state.event_log[0]
    sx, sy = latest_event["Start"]
    ex, ey = latest_event["End"]
    
    color = "#00ff87" if latest_event["Team"] == "Arsenal" else "#38bdf8"
    
    # Plot arrow for the latest action
    pitch.arrows(sx, sy, ex, ey, ax=ax, width=3, color=color, headwidth=5, label=f"Latest Action: {latest_event['Team']}")
    pitch.scatter(sx, sy, ax=ax, c=color, s=120, edgecolors='white', zorder=3)
    
    ax.set_title(f"Active Phase: {latest_event['Team']} {latest_event['Event']} (Coords: {sx}, {sy} -> {ex}, {ey})", 
                 color='white', fontsize=11, pad=10)
    st.pyplot(fig)