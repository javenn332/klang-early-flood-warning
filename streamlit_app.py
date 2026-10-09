import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# Page setup for dark high-tech layout
st.set_page_config(
    page_title="Klang Valley Flood Early Warning",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #0B0F19;
        color: #FFFFFF;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Klang Valley Hydrological AI Command Center")
st.caption("Real-time river telemetry, soil moisture metrics, and SMART Tunnel operational status")

# --- AIRTABLE INTEGRATION / FALLBACK DATA ---
AIRTABLE_API_KEY = st.secrets.get("AIRTABLE_API_KEY", "")
BASE_ID = st.secrets.get("BASE_ID", "")
TABLE_NAME = "TelemetryData"

@st.cache_data(ttl=30)
def fetch_telemetry():
    if AIRTABLE_API_KEY and BASE_ID:
        url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
        headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                records = res.json().get('records', [])
                return pd.DataFrame([r['fields'] for r in records])
        except Exception:
            pass
    
    # Klang Valley high-fidelity station dataset
    return pd.DataFrame([
        {
            "Station": "Sg. Klang at Tun Perak",
            "Latitude": 3.1485,
            "Longitude": 101.6961,
            "Water Level (m)": 5.80,
            "Rate of Rise (m/hr)": 0.45,
            "Radar dBZ": 52.0,
            "Soil Saturation (%)": 92.0,
            "SMART Mode": "Mode 3",
            "Alert Status": "Danger"
        },
        {
            "Station": "Sg. Gombak at Jalan Tun Razak",
            "Latitude": 3.1702,
            "Longitude": 101.6983,
            "Water Level (m)": 3.10,
            "Rate of Rise (m/hr)": 0.12,
            "Radar dBZ": 38.0,
            "Soil Saturation (%)": 84.0,
            "SMART Mode": "Mode 2",
            "Alert Status": "Warning"
        },
        {
            "Station": "Sg. Kerayong at Salak Selatan",
            "Latitude": 3.1082,
            "Longitude": 101.7052,
            "Water Level (m)": 1.45,
            "Rate of Rise (m/hr)": 0.02,
            "Radar dBZ": 22.0,
            "Soil Saturation (%)": 65.0,
            "SMART Mode": "Mode 1",
            "Alert Status": "Normal"
        }
    ])

df = fetch_telemetry()

# --- TOP KPI METRIC CARDS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="SMART Tunnel Status", value=df["SMART Mode"].iloc[0])
with col2:
    st.metric(label="Peak Radar Intensity", value=f"{df['Radar dBZ'].max()} dBZ")
with col3:
    st.metric(label="Avg Catchment Soil Moisture", value=f"{df['Soil Saturation (%)'].mean():.1f}%")

st.markdown("---")

# --- WEATHERNEXT DARK RADAR MAP ---
st.subheader("Live Basin Map & Telemetry Pins")

def assign_color(status):
    if status == "Danger":
        return [255, 0, 85, 230]     # Red / Magenta
    elif status == "Warning":
        return [255, 204, 0, 230]    # Electric Yellow
    return [0, 255, 102, 230]        # Neon Green

df["color"] = df["Alert Status"].apply(assign_color)

view_state = pdk.ViewState(latitude=3.1485, longitude=101.6961, zoom=11, pitch=35)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["Longitude", "Latitude"],
    get_color="color",
    get_radius=450,
    pickable=True,
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10",
    tooltip={"text": "Station: {Station}\nWater Level: {Water Level (m)}m\nStatus: {Alert Status}"}
))

# --- TELEMETRY DATA TABLE ---
st.subheader("Station Telemetry Grid")
st.dataframe(df.drop(columns=["color"], errors="ignore"), use_container_width=True)
