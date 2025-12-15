import pandas as pd
import streamlit as st

from data.mapping_dicts import column_interpretations
from utils import load_data, prep_data, load_css

st.set_page_config(page_title="FloodGate", layout="centered")
if 'df' in st.session_state:
    df = st.session_state['df']
else:
    st.error("Data not initialized. Please run the app from main.")
    st.stop()

cols_to_clean = ['ContractCost', 'ApprovedBudgetForContract']
for col in cols_to_clean:
    if col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace(',', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')

st.markdown("""
    <div class="main-header">
    <h1 style="font-size:1.2rem; font-weight:700; text-align:center;">
    <span class="global-happiness" style="color: skyblue; stroke: white 1px; font-size:5.8rem;">FLOODGATE</span><br> 
    Transparency Dashboard for DPWH Flood Control Projects</h1>
    </div>""", unsafe_allow_html=True)

col1, col2 = st.columns([2,2], vertical_alignment="center")
with col1:
    st.markdown("""
        <div class="section-container">
        <div class="section-title">Project Overview</div>
        <p>
            Year after year, persistent flooding devastates Filipino communities, raising urgent questions about 
            public spending integrity. This project used the DPWH Flood Control Projects dataset to analyze and uncover 
            anomalies and possible corruption in funding allocation.
            We seek to find where flood mitigation funds are concentrated and why certain projects inflate into costly 
            anomalies.
        </p>""", unsafe_allow_html=True)

with col2:
    col2.metric("Total Projects", len(df), border=True)
    col2.metric("Average Approved Budget", f"₱{df['ApprovedBudgetForContract'].mean():,.0f}", border=True)
    col2.metric("Total Approved Budget", f"₱{df['ApprovedBudgetForContract'].sum():,.0f}", border=True)

st.markdown("""
    <div>
        <div class="section-title">The Research Questions</div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>How are DPWH flood-control projects distributed geographically across regions and provinces?</b>
        </div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>Are there anomalous projects that deviate from normal regional or national patterns?</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
    <div class="section-title">Methodology</div>
        <div class="grid-container">
            <div class="method-card" style="border-top-color: #17a2b8;">
                <h3>Geospatial Analysis</h3>
                <p><strong>Clustering & Map Projection</strong></p>
                <p>Examines the spatial distribution of flood-control projects by mapping coordinates, identifying geographic clusters, and highlighting regions with high or low project density. </p>
            </div>
            <div class="method-card" style="border-top-color: #dc3545;">
                <h3>Anomaly Detection</h3>
                <p><strong>Outliers & Anomalies</strong></p>
                <p>Identify rare events, observations, or data points that deviate significantly from the normal behavior or patterns within a dataset.</p>
            </div>
    </div>
    """, unsafe_allow_html=True)
st.divider()
st.title("Dataset Overview")

st.markdown(
    """
    <div class="section-border">
        This dataset contains detailed records of flood control and flood mitigation projects 
        across multiple regions in the Philippines. The data originates from 
        <i>sumbongsapangulo.ph</i>, a government transparency platform established in response 
        to President Ferdinand Marcos Jr.’s directive during his fourth State of the Nation Address (SONA). 
        The initiative aims to investigate potential irregularities, corruption, and misallocation of funds 
        in DPWH flood-control projects, particularly in areas that continue to suffer from severe flooding 
        during the typhoon season.  
    </div>
    """,
    unsafe_allow_html=True
)

with st.expander("View Dataset Source"):
    st.markdown("""
            <i><strong>Provided by BwandoWando</strong></i>  
            Kaggle Link: https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects/data
        """, unsafe_allow_html=True)

st.info("Dataset Columns and Their Interpretation")

col_df = pd.DataFrame({
    "Column Name": list(column_interpretations.keys()),
    "Interpretation": list(column_interpretations.values())
})

st.dataframe(col_df, width='stretch')

st.info("Dataset Structure")
structure_df = pd.DataFrame({
    "Column": df.columns,
    "Non-Null Count": df.notnull().sum(),
    "Data Type": df.dtypes.astype(str)
})
st.dataframe(structure_df, width='stretch')

st.info("Raw Dataset Preview")
st.dataframe(df, width='stretch')
st.markdown(
    """
    <div style="
        text-align: center;  
        font-size: 0.9rem;
        opacity: 0.7;
    ">
        <strong>Made with Streamlit by The J’s</strong>
    </div>
    """,
    unsafe_allow_html=True
)