import streamlit as st

from utils import load_data, prep_data, get_filters, load_css, apply_filter

load_css()
CENTER = (11.891783, 122.419922)
if "center" not in st.session_state:
    st.session_state["center"] = CENTER
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 6

df = load_data()
st.session_state["df"] = df
clean_df = prep_data(df)
inputs = get_filters(clean_df)
st.session_state["inputs"] = inputs
filtered_df = apply_filter(clean_df, inputs)
st.session_state["filtered_df"] = filtered_df

home_page = st.Page(
    page="views/overview.py",
    title="Overview",
    default=True
)

preparation_page = st.Page(
    page="views/preparation.py",
    title="Preparation",
)

data_exploration_page = st.Page(
    page="views/exploration.py",
    title="Exploration",
)

analysis_page = st.Page(
    page="views/analysis.py",
    title="Analysis",
)

conclusions_page = st.Page(
    page="views/conclusions.py",
    title="Conclusions",
)

pg = st.navigation({
    "Project Info": [home_page, conclusions_page],
    "Data Pipeline": [preparation_page, data_exploration_page, analysis_page]
})

pg.run()


with st.sidebar:
    st.markdown("""
        <div class="custom-box" style='margin-bottom: 15px;'>
                <b>Authors: The J's</b>
        </div>
    """, unsafe_allow_html=True)
    st.info("Joshua Arco")
    st.info("Jon Mari Casipong")
    st.info("John Kevin Muyco")
    st.info("Jive Tyler Revalde")
    st.info("John Michael Sayson")
