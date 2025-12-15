import streamlit as st
from utils import load_css

st.set_page_config(layout="centered", page_title="Conclusions")
load_css()

st.markdown('<div class="title-card">Conclusions & Recommendations</div>', unsafe_allow_html=True)

# Executive Summary Box
st.markdown("""
    <div>
        <div class="section-title">Summary</div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>The analysis reveals significant regional disparities in funding, with a concentration of capital in Luzon.</b>
        </div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>Conversely, Visayas and Mindanao are characterized by a high volume of low-cost, fragmented projects.</b>
        </div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>Markers indicate potential non-competitive bidding practices in most clusters, where contract costs align suspiciously 
    close to budget ceilings.</b>
        </div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>Further analysis identifies a risk of oligopoly, with a few contractors dominating the sector.</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Key Insights")

with st.expander("Geospatial Disparity", expanded=True):
    st.write("""
        * **Luzon Bias:** High-value projects are heavily concentrated in NCR and Region III.
        * **Fragmentation:** Visayas and Mindanao receive a high volume of projects, but they are significantly smaller in scale/cost, suggesting a fragmented approach to flood control.
        """)
with st.expander("Contractor Dominance", expanded=True):
    st.write("""
    The market is not evenly competitive. A small percentage of "Top Contractors" controls a disproportionately large share of the total contract value.""")
with st.expander("Ghost Projects", expanded=True):
    st.write("""
    Outlier detection identified a subset of projects with High Capital Expenditure but suspiciously Short Durations. Infrastructure projects worth billions cannot be completed in a few months
    """)

with st.expander("Corruption Risk", expanded=True):
    st.write("""
        Any project where the bid price is within 1% of the ABC should trigger an automatic detailed review to check for collusion or single-bidder anomalies.
        """)

st.markdown("### Recommendations")

with st.expander("Community Reporting", expanded=True):
    st.write("""
        Use FLOODGATE to find faults and discrepancies in the government's flood control projects and report them to the Commission on Audit (COA). Having the specific Project ID and Contract ID makes it much harder for agencies to ignore a complaint.
        """)

st.divider()
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
