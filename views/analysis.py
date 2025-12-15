import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

from utils import (
    create_map, plot_bid_variance,
    TypeOfWork_full_color
)

st.set_page_config(layout="centered", page_title="Analysis")
if 'filtered_df' in st.session_state and 'inputs' in st.session_state:
    filtered_df = st.session_state['filtered_df']
    inp = st.session_state['inputs']
else:
    st.error("Data not initialized. Please run the app from main.")

st.markdown("""<div class="title-card">Analysis</div>""", unsafe_allow_html=True)
st.info("""
        **What is the ABC?**
        The **Approved Budget for the Contract (ABC)** is the budget ceiling for a project. 
        According to the Commission on Audit (COA), it is the maximum amount the government is willing to pay. 
        Source: [COA FAQs](https://www.coa.gov.ph/FAQS/what-is-the-approved-budget-for-the-contract-abc/)
        """)
st.info(""""
        **Why is >100% Cost Suspicious?**
        Under **RA 9184** (Government Procurement Reform Act), a contract award **cannot exceed the ABC**. 
        Bids above the ABC are automatically disqualified.
        """)
st.info("""
    **Exceptions (GPPB Resolution 07-2005):**
    The ABC can only be adjusted upwards if:
    1. Bidding has failed twice (all bids exceeded ABC).
    2. Technical specifications were modified (unless the project is indivisible).
    
    *If a project cost exceeds the ABC without these specific conditions, it is a major red flag for audit.*
    """)
if filtered_df.empty:
    st.warning("No data matches filters.")
else:
    st.markdown("""
    <div class="section-title">Geospatial Analysis</div>
    """, unsafe_allow_html=True)
    if inp['enable_clustering']:
        m, stats = create_map(filtered_df, st.session_state["center"], st.session_state["zoom"], inp['n_clusters'], True)
    else:
        m, stats = create_map(filtered_df, st.session_state["center"], st.session_state["zoom"], inp['n_clusters'], False)
    st_folium(m, height=500, returned_objects=[], width=1000)

    if not inp['enable_clustering']:
        with st.expander("Type of Work Legend"):
            html = """
            <div style="font-family: 'Segoe UI', Roboto, sans-serif;">
              <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:14px;">
            """
            for work_type, color in TypeOfWork_full_color.items():
                html += f'''
                  <div style="display:flex; align-items:center;">
                    <div style="width:14px; height:14px; background:{color}; border:1px solid #444; margin-right:8px;"></div>
                    <div style="line-height:14px; color: white">{work_type}</div>
                  </div>
                '''
            html += "</div></div>"
            components.html(html, height=300, scrolling=True)
    else:
        if not stats.empty:
            st.write("Clustering Statistics:")
            st.dataframe(stats)

    with st.expander("Map Susceptibility Legend"):
        c1, c2 = st.columns(2, vertical_alignment="center")

        with c1:
            st.markdown("**Flood Susceptibility**")
            st.markdown("""
            <div style="font-size: 12px; margin-bottom: 5px;">
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#002673; border:1px solid #ccc;"></span> Very High Susceptibility
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#5900ff; border:1px solid #ccc;"></span> High Susceptibility
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#b045ff; border:1px solid #ccc;"></span> Moderate Susceptibility
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#e3d1ff; border:1px solid #ccc;"></span> Low Susceptibility
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("""
                    <div style="font-size: 12px;">
                        <p><b>Source:</b> Department of Environment and Natural Resources, Mines and Geoscience Bureau</p> 
                    </div>
                    """, unsafe_allow_html=True)

        with c2:
            st.markdown("**Landslide Susceptibility**")
            st.markdown("""
                    <div style="font-size: 12px;">
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color:#902400; border:1px solid #ccc;"></span> Very High Susceptibility
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color: red; border:1px solid #ccc;"></span> High Susceptibility
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color: green ; border:1px solid #ccc;"></span> Moderate Susceptibility
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color: yellow ; border:1px solid #ccc;"></span> Low Susceptibility
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("""
                    <div style="font-size: 12px;">
                        <p><b>Source:</b> Department of Environment and Natural Resources, Mines and Geoscience Bureau</p> 
                    </div>
                    """, unsafe_allow_html=True)

    if not filtered_df.empty:
        top_type = filtered_df['TypeOfWork'].mode()[0]
        st.info(f"Most Common Work:\n**{top_type}**")

        avg_dur = filtered_df['Duration'].mean()
        st.success(f"Avg Duration:\n**{avg_dur:.0f} Days**")

        max_proj = filtered_df.loc[filtered_df['ContractCost'].idxmax()]
        st.warning(f"Most Expensive:\n**{max_proj['ProjectName'][:50]}...**\n(₱{max_proj['ContractCost']/1e6:.1f} M)")

    st.markdown("""
    <div class="section-title">Anomaly Detection</div>
    """, unsafe_allow_html=True)
    total_cost = (filtered_df['ContractCost'].sum())
    suspicious_df = filtered_df[filtered_df['IsSuspicious']]
    suspicious_val = suspicious_df['ContractCost'].sum()

    c1, c2= st.columns(2)
    c1.metric("Total Contract Value", f"₱{total_cost:,.0f}", border=True)
    c2.metric("Suspicious Capital", f"₱{suspicious_val:,.0f}", help="Projects with cost >= 100% of budget", border=True)
    c1.metric("Flagged Projects", f"{len(suspicious_df)}", delta_color="inverse", border=True)
    c2.metric("Projects Found", f"{len(filtered_df)}", border=True)
    st.info("""
        **What do these scores mean?**
        
        * **Risk Score = 1**: The Contract Cost matches the Approved Budget (ABC) exactly. This suggests there is no competition involved in the bidding process.
        * **Risk Score > 1**: The cost exceeds the legal budget ceiling. Under **RA 9184**, bids above the ABC are automatically disqualified unless specific "failure of bidding" conditions are met.
        * **Risk Score ≥ 1**: The total number of projects that hit or exceeded the maximum allowable government cost.
        """)
    st.subheader("**Bid Variance**")
    fig_var = plot_bid_variance(filtered_df)
    st.pyplot(fig_var)

    with st.expander("View Raw Data Table"):
        st.dataframe(filtered_df, width='stretch')


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