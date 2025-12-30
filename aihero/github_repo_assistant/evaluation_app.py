import glob
import json
import os

import pandas as pd
import plotly.express as px
import streamlit as st

# Set page config
st.set_page_config(layout="wide", page_title="Evaluation Dashboard", page_icon="📊")

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    .metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #0b57d0;
    }
    .metric-label {
        color: #4b5563;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Agent Evaluation Dashboard")
st.markdown("Visualize the performance of your AI Agent evaluations.")

# Load Data directly from CSV
@st.cache_data
def load_results():
    if os.path.exists("evaluation_results.csv"):
        return pd.read_csv("evaluation_results.csv")
    return None

df = load_results()

if df is None:
    st.warning("⚠️ No 'evaluation_results.csv' found.")
    st.info("Run the evaluation script first: `python evaluation.py`")
    
    # Check if we have logs at all
    log_count = len(glob.glob("evaluation_data/*.json")) if os.path.exists("evaluation_data") else 0
    st.caption(f"Note: Found {log_count} log files in `evaluation_data/` waiting to be processed.")

elif df.empty:
    st.warning("Evaluation CSV found but it is empty.")
else:
    # 1. High-Level Metrics
    st.header("📈 Overall Performance")
    
    # Calculate pass rates
    metadata_cols = ['log_file', 'source', 'model']
    # Filter for check columns (boolean-like)
    check_cols = [c for c in df.columns if c not in metadata_cols and df[c].dtype == bool]
    
    # Handle case where CSV reading might interpret booleans as strings or ints
    # Force conversion to ensure mean() works
    for c in check_cols:
        df[c] = df[c].astype(bool)
        
    if not check_cols:
        # Fallback if detection fails (e.g. all True/False strings)
        check_cols = [c for c in df.columns if c not in metadata_cols]
        # Attempt conversion
        # df[check_cols] = df[check_cols].applymap(...)

    # Calculate means (pass rates)
    if check_cols:
        pass_rates = df[check_cols].mean() * 100
        
        # Display Key Metrics in Columns
        num_cols = len(check_cols)
        cols = st.columns(min(num_cols, 4))
        for i, col_name in enumerate(check_cols):
            rate = pass_rates[col_name]
            with cols[i % 4]: # Wrap every 4 columns
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{rate:.1f}%</div>
                    <div class="metric-label">{col_name.replace('_', ' ').title()}</div>
                </div>
                """, unsafe_allow_html=True)

    # 2. Detailed visualisations
    st.markdown("---")
    st.header("🔍 Detailed Breakdown")
    
    col_chart, col_df = st.columns([1, 1])
    
    with col_chart:
        if check_cols:
            pass_rates_df = pass_rates.reset_index()
            pass_rates_df.columns = ['Check', 'Pass Rate (%)']
            
            fig = px.bar(
                pass_rates_df, 
                x='Check', 
                y='Pass Rate (%)', 
                text_auto='.1f',
                color='Pass Rate (%)',
                color_continuous_scale='RdYlGn',
                range_y=[0, 100],
                title="Pass Rate by Check Criteria"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No check columns found to visualize.")

    with col_df:
        st.markdown("**Filters**")
        selected_checks = st.multiselect("Filter by Failed Check", check_cols)
        
        display_df = df
        if selected_checks:
            for check in selected_checks:
                display_df = display_df[~display_df[check]]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=400
        )
        st.caption(f"Showing {len(display_df)} records.")
    
    # 3. Log Inspector
    st.markdown("---")
    st.subheader("🕵️‍♂️ Log Inspector")
    
    col_sel, col_content = st.columns([1, 2])
    
    with col_sel:
        selected_file = st.selectbox("Select Log File", display_df['log_file'].unique())
        if selected_file:
            # Show summary for selected file
            file_results = df[df['log_file'] == selected_file].iloc[0]
            st.markdown("#### Check Status")
            for check in check_cols:
                status = "✅ PASS" if file_results[check] else "❌ FAIL"
                st.write(f"**{check}**: {status}")

    with col_content:
        if selected_file:
            log_path = os.path.join("evaluation_data", selected_file)
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
                st.json(log_data)
            else:
                st.error(f"Log file not found at {log_path}")
