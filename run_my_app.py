# run_my_app.py (Version 12.0 - The Ultimate Professional Workbench & Explorer)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import joblib

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="ExoSight AI Explorer", page_icon="🚀")

# --- 2. THEME INITIALIZATION & DYNAMIC CSS ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

light_theme_css = """
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #ffffff; color: #0d1117; }
    .main .block-container { max-width: 100%; padding: 1rem 2rem; }
    div[data-testid="stMetric"] { background-color: #f0f2f6; border: 1px solid #d1d5db; padding: 1rem; border-radius: 0.5rem; text-align: center; color: #0d1117; }
    h1, h2, h3, h4 { color: #0d1117; }
    [data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #d1d5db; }
</style>
"""
dark_theme_css = """
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .main .block-container { max-width: 100%; padding: 1rem 2rem; }
    div[data-testid="stMetric"] { background-color: #0d1117; border: 1px solid #30363d; padding: 1rem; border-radius: 0.5rem; text-align: center; }
    h1, h2, h3, h4 { color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
</style>
"""

if st.session_state.theme == 'light':
    st.markdown(light_theme_css, unsafe_allow_html=True)
    plotly_theme = "plotly_white"
else:
    st.markdown(dark_theme_css, unsafe_allow_html=True)
    plotly_theme = "plotly_dark"

# --- 3. DATA LOADING & MOCK DATA ---
@st.cache_data
def load_candidate_data():
    """Loads the AI-identified candidates."""
    try:
        df = pd.read_csv('ai_identified_candidates.csv')
        if 'kepoi_name' not in df.columns:
            st.error("FATAL ERROR: 'kepoi_name' column not found in 'ai_identified_candidates.csv'. Please re-run the latest 'create_model.py'.")
            return pd.DataFrame()
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_resource
def load_ml_assets():
    """Loads the trained model and scaler."""
    try:
        model = joblib.load('mlp_exoplanet_model.pkl')
        scaler = joblib.load('scaler_object.pkl')
        return model, scaler
    except FileNotFoundError:
        return None, None

def generate_mock_light_curve(planet):
    """Generates a realistic-looking light curve for a given planet."""
    period = planet['koi_period']
    duration_days = planet['koi_duration'] / 24.0
    time = np.linspace(0, period * 5, 2000)
    flux = np.ones_like(time)
    for i in range(6):
        transit_center = i * period
        transit_start = transit_center - (duration_days / 2)
        transit_end = transit_center + (duration_days / 2)
        in_transit = (time > transit_start) & (time < transit_end)
        flux[in_transit] = 1 - (planet['koi_prad']**2 / 15000)
    flux += np.random.normal(0, 0.00015, size=len(time))
    return pd.DataFrame({'Time (days)': time, 'Flux': flux})

exoplanet_library_data = {
    "TRAPPIST-1d": {"system": "TRAPPIST-1", "discovery_mission": "TRAPPIST", "planet_type": "Rocky, Earth-sized", "fun_fact": "One of seven rocky worlds in its system; its atmosphere is a key target for JWST."},
    "Kepler-186f": {"system": "Kepler-186", "discovery_mission": "Kepler", "planet_type": "Terrestrial", "fun_fact": "The first rocky planet discovered within the habitable zone of another star."},
    "51 Pegasi b": {"system": "51 Pegasi", "discovery_mission": "Observatoire de Haute-Provence", "planet_type": "Gas Giant (Hot Jupiter)", "fun_fact": "The first exoplanet discovered orbiting a sun-like star, awarded the 2019 Nobel Prize in Physics."},
    "TOI 700 d": {"system": "TOI 700", "discovery_mission": "TESS", "planet_type": "Earth-sized", "fun_fact": "The first Earth-sized planet discovered by TESS in its star's habitable zone."},
}

ai_planets_df = load_candidate_data()
mlp_model, scaler = load_ml_assets()
FEATURE_COLUMNS = ['koi_period', 'koi_prad', 'koi_teq', 'koi_duration', 'koi_impact', 'koi_insol']

# --- 5. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🚀 ExoSight Pro")
    if st.button("Switch Theme", use_container_width=True):
        st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
        st.rerun()

    app_mode = st.radio("Select Tool:", ("Analysis Workbench", "Live Prediction Tool", "Exoplanet Library"))
    st.markdown("---")
    
    selected_planet = None
    if app_mode == "Analysis Workbench" and not ai_planets_df.empty:
        st.header("Target Selection")
        target_planet_name = st.selectbox(
            "AI-Discovered Candidates:",
            options=ai_planets_df['kepoi_name'],
            format_func=lambda x: f"{x} (AI Conf: {ai_planets_df.loc[ai_planets_df['kepoi_name'] == x, 'confidence'].iloc[0]:.1%})"
        )
        if target_planet_name:
            selected_planet = ai_planets_df[ai_planets_df['kepoi_name'] == target_planet_name].iloc[0]

# --- 6. MAIN PAGE LAYOUT ---
st.title("ExoSight AI Explorer")

# --- PAGE 1: ANALYSIS WORKBENCH ---
if app_mode == "Analysis Workbench":
    if selected_planet is None:
        st.warning("No AI candidate data loaded or selected. Please ensure `create_model.py` was run, and select a candidate from the sidebar.")
    else:
        st.header(f"Analysis Workbench: {selected_planet['kepoi_name']}")
        plot_col, analysis_col = st.columns([2, 1])

        with plot_col:
            st.subheader("Light Curve Analysis")
            light_curve_df = generate_mock_light_curve(selected_planet)
            fig_lc = px.line(light_curve_df, x='Time (days)', y='Flux', title="Full Time Series Data (Simulated)")
            fig_lc.update_layout(template=plotly_theme)
            st.plotly_chart(fig_lc, use_container_width=True)

            st.subheader("Phased Light Curve")
            phased_time = (light_curve_df['Time (days)'] % selected_planet['koi_period'])
            phased_df = pd.DataFrame({'Phase': phased_time, 'Flux': light_curve_df['Flux']}).sort_values('Phase')
            fig_phased = px.scatter(phased_df, x='Phase', y='Flux', title=f"Data Phased to Period: {selected_planet['koi_period']:.4f} days")
            fig_phased.update_traces(marker=dict(size=3, opacity=0.7))
            fig_phased.update_layout(template=plotly_theme)
            st.plotly_chart(fig_phased, use_container_width=True)

        with analysis_col:
            st.subheader("Analysis & Data")
            param_tab, ai_tab, raw_tab = st.tabs(["Key Parameters", "AI Insights", "Raw Data"])
            with param_tab:
                st.metric("Orbital Period (days)", f"{selected_planet['koi_period']:.4f}")
                st.metric("Planet Radius (Earth radii)", f"{selected_planet['koi_prad']:.2f}")
            with ai_tab:
                st.metric("AI Confidence Score", f"{selected_planet['confidence']:.2%}")
                st.info(f"Originally labeled '{selected_planet['koi_pdisposition']}', our AI re-classified it as a high-confidence candidate.")
            with raw_tab:
                st.write(selected_planet)

# --- PAGE 2: LIVE PREDICTION TOOL ---
elif app_mode == "Live Prediction Tool":
    st.header("Live MLP Prediction Tool")
    if mlp_model and scaler:
        # Form layout
        # ... (rest of the code is the same)
    else:
        st.error("AI Model not loaded! The Live Prediction Tool is unavailable.")

# --- PAGE 3: EXOPLANET LIBRARY ---
elif app_mode == "Exoplanet Library":
    st.header("Featured Exoplanets Library")
    list_col, detail_col = st.columns([1, 2])
    with list_col:
        selected_planet_name = st.radio("Exoplanets:", options=sorted(exoplanet_library_data.keys()))
    with detail_col:
        if selected_planet_name:
            planet_info = exoplanet_library_data[selected_planet_name]
            st.subheader(selected_planet_name)
            st.info(planet_info['fun_fact'])
