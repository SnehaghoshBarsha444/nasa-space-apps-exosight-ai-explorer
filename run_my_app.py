# run_my_app.py (Version 10.0 - Final Merged Version with Exoplanet Library)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(layout="wide", page_title="ExoSight AI Explorer", page_icon="🚀")

# --- 2. ADVANCED CSS for a professional look ---
st.markdown("""
<style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    .main .block-container { max-width: 95%; padding: 1rem 2rem; }
    div[data-testid="stMetric"] { background-color: #0d1117; border: 1px solid #30363d; padding: 1rem; border-radius: 0.5rem; }
    h1, h2, h3, h4 { color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA SOURCES ---
# Static "fun facts" data from your explorer.py
exoplanet_library_data = {
    "TRAPPIST-1d": {"system": "TRAPPIST-1", "discovery_mission": "TRAPPIST", "planet_type": "Rocky, Earth-sized", "fun_fact": "One of seven rocky worlds in its system; its atmosphere is a key target for JWST."},
    "Kepler-186f": {"system": "Kepler-186", "discovery_mission": "Kepler", "planet_type": "Terrestrial", "fun_fact": "The first rocky planet discovered within the habitable zone of another star."},
    "51 Pegasi b": {"system": "51 Pegasi", "discovery_mission": "Observatoire de Haute-Provence", "planet_type": "Gas Giant (Hot Jupiter)", "fun_fact": "The first exoplanet discovered orbiting a sun-like star, awarded the 2019 Nobel Prize in Physics."},
    "TOI 700 d": {"system": "TOI 700", "discovery_mission": "TESS", "planet_type": "Earth-sized", "fun_fact": "The first Earth-sized planet discovered by TESS in its star's habitable zone."},
    "Wolf 503b": {"system": "Wolf 503", "discovery_mission": "Kepler", "planet_type": "Super-Earth", "fun_fact": "Twice the size of Earth, it falls into a rarely observed size category known as the 'Fulton gap'."},
    "TRAPPIST-1e": {"system": "TRAPPIST-1", "discovery_mission": "TRAPPIST", "planet_type": "Rocky, Earth-sized", "fun_fact": "Considered one of the most promising of the TRAPPIST-1 planets for habitability."},
    "Kepler-452b": {"system": "Kepler-452", "discovery_mission": "Kepler", "planet_type": "Super-Earth", "fun_fact": "Sometimes nicknamed 'Earth's cousin' due to its similar orbit around a Sun-like star."},
}

# Functions to load dynamic data from your AI model
@st.cache_resource
def load_ml_assets():
    try:
        model = joblib.load('mlp_exoplanet_model.pkl')
        scaler = joblib.load('scaler_object.pkl')
        return model, scaler
    except Exception: return None, None

@st.cache_data
def load_candidate_data():
    try:
        df = pd.read_csv('ai_identified_candidates.csv')
        return df
    except Exception: return pd.DataFrame()

@st.cache_data
def load_full_kepler_data():
    try:
        df = pd.read_csv("cumulative_2025.10.03_00.23.38.csv", skiprows=53)
        stars_df = df[['kepid', 'koi_srad', 'koi_steff']].drop_duplicates(subset=['kepid'])
        stars_df.dropna(subset=['koi_srad'], inplace=True)
        return stars_df
    except Exception: return pd.DataFrame()

mlp_model, scaler = load_ml_assets()
ai_planets_df = load_candidate_data()
host_stars_df = load_full_kepler_data()
FEATURE_COLUMNS = ['koi_period', 'koi_prad', 'koi_teq', 'koi_duration', 'koi_impact', 'koi_insol']

if 'selected_star_kepid' not in st.session_state:
    st.session_state.selected_star_kepid = None

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🚀 ExoSight Controls")
    app_mode = st.radio(
        "Choose a tool:",
        ("AI Dashboard & Explorer", "Live Prediction Tool", "Exoplanet Library")
    )
    st.markdown("---")
    
    filtered_planets = ai_planets_df.copy()
    if app_mode == "AI Dashboard & Explorer" and not ai_planets_df.empty:
        st.header("Candidate List Filters")
        search_id = st.text_input("Search AI Candidates by Kepler ID")
        if search_id:
            filtered_planets = filtered_planets[filtered_planets['kepid'].astype(str).str.contains(search_id)]
        
        confidence_threshold = st.slider('Filter by AI Confidence Score', 0.80, 1.0, 0.80, 0.01)
        filtered_planets = filtered_planets[filtered_planets['confidence'] >= confidence_threshold]

# --- 5. MAIN PAGE LAYOUT ---
st.title("ExoSight AI Explorer")

# --- PAGE 1: AI DASHBOARD & EXPLORER ---
if app_mode == "AI Dashboard & Explorer":
    st.markdown("An integrated dashboard to search, filter, and visually explore AI-discovered exoplanet candidates.")
    st.markdown("---")
    
    if ai_planets_df.empty or host_stars_df.empty:
        st.error("Data files not found. Please run create_model.py and ensure all .csv files are in the same directory.")
    else:
        st.subheader("Key Discoveries")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total AI Candidates", len(ai_planets_df))
        col2.metric("Highest Confidence", f"{ai_planets_df['confidence'].max():.2%}")
        col3.metric("Candidates in View", len(filtered_planets))
        st.markdown("---")

        st.subheader("Filterable AI Candidate List")
        if not filtered_planets.empty:
            st.dataframe(filtered_planets.style.format({'confidence': "{:.2%}"}))
        else:
            st.warning("No candidates match your filters.")
        st.markdown("---")

        st.subheader("Galaxy Explorer")
        st.markdown("Click a host star in the 'Galaxy View' (left) to explore its system in the 'System View' (right).")
        exp_col1, exp_col2 = st.columns([2, 1])

        with exp_col1:
            st.subheader("Galaxy View: Host Stars")
            fig_galaxy = px.scatter(
                host_stars_df, x='kepid', y='koi_steff', size='koi_srad', color='koi_steff',
                hover_name='kepid', custom_data=['kepid'],
                color_continuous_scale=px.colors.sequential.Plasma, title="Kepler Host Stars"
            )
            fig_galaxy.update_layout(xaxis_title="Kepler ID", yaxis_title="Stellar Temperature (K)", plot_bgcolor='#0d1117', paper_bgcolor='#0d1117', font_color='white')
            
            click_data = st.plotly_chart(fig_galaxy, use_container_width=True, on_select="rerun")
            if click_data.selection and click_data.selection['points']:
                st.session_state.selected_star_kepid = click_data.selection['points'][0]['x']

        with exp_col2:
            st.subheader("System View")
            if st.session_state.selected_star_kepid:
                selected_id = st.session_state.selected_star_kepid
                star_info = host_stars_df.query("kepid == @selected_id").iloc[0]
                planets_in_system = ai_planets_df.query("kepid == @selected_id")
                
                st.metric("Exploring System", f"Kepler ID: {selected_id}")
                
                fig_system = go.Figure()
                fig_system.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(size=star_info['koi_srad'] * 20, color='yellow'), name=f'Star {selected_id}'))
                
                if not planets_in_system.empty:
                    fig_system.add_trace(go.Scatter(
                        x=planets_in_system['koi_period'], y=[0] * len(planets_in_system), mode='markers',
                        marker=dict(size=planets_in_system['koi_prad'] * 5, color=planets_in_system['koi_teq'], colorscale='cividis', showscale=True, colorbar_title='Planet Temp (K)'),
                        hovertext=planets_in_system.apply(lambda r: f"Planet: {r.get('kepoi_name', 'N/A')}<br>Confidence: {r['confidence']:.2%}", axis=1),
                        hoverinfo="text", name='Planets'
                    ))
                fig_system.update_layout(title=f'Planetary System for Star {selected_id}', xaxis_title="Orbital Period (days)", yaxis=dict(visible=False), plot_bgcolor='#0d1117', paper_bgcolor='#0d1117', font_color='white')
                st.plotly_chart(fig_system, use_container_width=True)
            else:
                st.info("Click a star to see its system here.")

# --- PAGE 2: LIVE PREDICTION TOOL ---
elif app_mode == "Live Prediction Tool":
    st.subheader("Live MLP Prediction Tool")
    st.markdown("Enter the parameters of a potential transit to get a real-time prediction from our AI model.")
    if mlp_model and scaler:
        with st.container():
            cols = st.columns(3)
            period = cols[0].number_input('Orbital Period (days)', value=5.0, format="%.4f")
            prad = cols[1].number_input('Planet Radius (Earth radii)', value=1.5, format="%.2f")
            teq = cols[2].number_input('Equilibrium Temp (K)', value=700.0, format="%.1f")
            duration = cols[0].number_input('Transit Duration (hrs)', value=3.0, format="%.2f")
            impact = cols[1].number_input('Impact Parameter', value=0.5, format="%.2f")
            insol = cols[2].number_input('Insolation Flux (Earth flux)', value=100.0, format="%.2f")

            if st.button('Analyze with AI', type="primary", use_container_width=True):
                input_data = pd.DataFrame([[period, prad, teq, duration, impact, insol]], columns=FEATURE_COLUMNS)
                input_scaled = scaler.transform(input_data)
                prediction_prob = mlp_model.predict_proba(input_scaled)[0, 1] * 100
                st.subheader("AI Analysis Result:")
                st.metric(label="Probability of being a real Exoplanet Candidate", value=f"{prediction_prob:.2f}%")
    else:
        st.error("AI Model not loaded! Please ensure create_model.py was run and .pkl files are present.")

# --- PAGE 3: NEW EXOPLANET LIBRARY ---
elif app_mode == "Exoplanet Library":
    st.subheader("Featured Exoplanets Library")
    st.markdown("Discover some of the most famous and interesting exoplanets found to date.")
    
    list_col, detail_col = st.columns([1, 2])

    with list_col:
        st.subheader("Select a Planet")
        selected_planet_name = st.radio(
            "Exoplanets:",
            options=sorted(exoplanet_library_data.keys()) # Sort the list alphabetically
        )

    with detail_col:
        if selected_planet_name:
            planet_info = exoplanet_library_data[selected_planet_name]
            
            st.header(selected_planet_name)
            st.markdown(f"*System:* {planet_info['system']}")
            st.markdown(f"*Discovery Mission:* {planet_info['discovery_mission']}")
            st.markdown(f"*Planet Type:* {planet_info['planet_type']}")
            st.markdown("---")
            st.subheader("Fun Fact")
            st.info(planet_info['fun_fact'])
