import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time

DB_PATH = "shadow_vault.db"
st.set_page_config(
    page_title="Shadow Quant Oracle",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    h1, h2, h3 {
        color: #58a6ff; 
        font-family: 'Courier New', Courier, monospace;
    }
    .highlight {
        color: #3fb950;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

def load_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM posts ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Vault locked: {e}")
        return pd.DataFrame()

def main():
    st.title("Shadow Quant Oracle // Void Watch")
    st.markdown("*> Signals whispering from the deep web.*")

    if st.button("Refresh Signals"):
        st.rerun()

    df = load_data()

    if df.empty:
        st.warning("The vault is empty. Run the backend hunter first.")
        st.code("python3 oracle_backend.py --subs quant,ethereum --vader --web3")
        return

    col1, col2, col3 = st.columns(3)
    
    avg_sentiment = df['vader_compound'].mean()
    bull_count = df[df['vader_compound'] > 0.5].shape[0]
    whale_sightings = df[df['web3_signal'] == 'WHALE_ALERT'].shape[0]

    with col1:
        st.metric("Global Sentiment", f"{avg_sentiment:.3f}", delta="Bullish" if avg_sentiment > 0 else "Bearish")
    with col2:
        st.metric("Alpha Signals (>0.5)", bull_count)
    with col3:
        st.metric("Whale Ghosts", whale_sightings, delta_color="inverse")

    st.markdown("---")

    st.subheader(" Signal Heatmap")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.set_facecolor('#0e1117')
    fig.patch.set_facecolor('#0e1117')
    
    colors = {'LOW_GAS': 'gray', 'NORMAL': 'blue', 'WHALE_ALERT': 'red', 'N/A': 'green'}
    c_map = df['web3_signal'].map(colors).fillna('green')

    ax.scatter(df['timestamp'], df['vader_compound'], c=c_map, alpha=0.7)
    ax.axhline(0, color='white', linestyle='--', alpha=0.3)
    ax.set_ylabel("VADER Score (-1 to 1)", color='white')
    ax.set_title("Sentiment Timeline (Red = Whale Alert)", color='white')
    ax.tick_params(axis='x', colors='white', rotation=45)
    ax.tick_params(axis='y', colors='white')
    
    for spine in ax.spines.values():
        spine.set_visible(False)

    st.pyplot(fig)

    st.subheader(" The Feed")
    
    min_score = st.slider("Filter by VADER Score", -1.0, 1.0, 0.0)
    filtered_df = df[df['vader_compound'] >= min_score]

    st.dataframe(
        filtered_df[['sub', 'title', 'vader_compound', 'web3_signal', 'timestamp']],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("Build v3.0.1 | *Shadows don't sleep.*")

if __name__ == "__main__":
    main()
