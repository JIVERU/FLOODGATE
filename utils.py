import branca.element
import folium as fm
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from folium import TileLayer
from sklearn.cluster import KMeans
from data.mapping_dicts import TypeOfWork_full_color, TypeOfWork_dict, CLUSTER_COLORS
import numpy as np

def load_css():
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        dataframe = pd.read_csv("data/dpwh_flood_control_projects.csv")
        return dataframe
    except FileNotFoundError:
        st.error("File 'dpwh_flood_control_projects.csv' not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def prep_data(data):

    if data.empty: return data
    clean = data.copy()

    cols_to_clean = ['ContractCost', 'ApprovedBudgetForContract']
    for col in cols_to_clean:
        if col in clean.columns:
            if clean[col].dtype == 'object':
                clean[col] = clean[col].astype(str).str.replace(',', '', regex=True)
            clean[col] = pd.to_numeric(clean[col], errors='coerce')

    clean = clean.dropna(subset=['ContractCost', 'ApprovedBudgetForContract'])

    clean['StartDate'] = pd.to_datetime(clean['StartDate'], errors='coerce')
    clean['ActualCompletionDate'] = pd.to_datetime(clean['ActualCompletionDate'], errors='coerce')

    clean['Duration'] = (clean['ActualCompletionDate'] - clean['StartDate']).dt.days

    clean['StartDate'] = clean['StartDate'].dt.strftime('%B-%d-%Y')
    clean['ActualCompletionDate'] = clean['ActualCompletionDate'].dt.strftime('%B-%d-%Y')

    clean['FundingYear'] = pd.to_numeric(clean['FundingYear'], errors='coerce')
    clean = clean.loc[~clean['FundingYear'].isin([2018, 2019, 2020, 2021, 2025])]

    clean['BudgetDifference'] = clean['ApprovedBudgetForContract'] - clean['ContractCost']
    clean['BudgetVariance'] = (clean['BudgetDifference'] / clean['ApprovedBudgetForContract']) * 100
    clean['RiskScore'] = (clean['ContractCost'] / clean['ApprovedBudgetForContract'])
    clean['IsSuspicious'] = clean['RiskScore'] > 1

    col_map = {'ProjectLatitude': 'latitude', 'ProjectLongitude': 'longitude'}
    clean = clean.rename(columns=col_map)
    clean = clean.dropna(subset=['latitude', 'longitude'])

    return clean

def apply_filter(df, inputs):
    df = df.copy()

    mask = pd.Series([True] * len(df), index=df.index)

    if inputs['search_term']:
        mask &= df['ProjectName'].str.contains(inputs['search_term'], case=False, na=False)
    if inputs['search_id']:
        mask &= df['ProjectId'].astype(str).str.contains(inputs['search_id'], case=False, na=False)
    if inputs['selected_regions']:
        mask &= df['Region'].isin(inputs['selected_regions'])
    if inputs['selected_provinces']:
        mask &= df['Province'].isin(inputs['selected_provinces'])
    if inputs['selected_contractors']:
        mask &= df['Contractor'].isin(inputs['selected_contractors'])
    if inputs['selected_works']:
        mask &= df['TypeOfWork'].isin(inputs['selected_works'])
    if inputs['selected_years']:
        mask &= (df['FundingYear'] >= inputs['selected_years'][0]) & (df['FundingYear'] <= inputs['selected_years'][1])
    if inputs.get('cost_range'):
        min_c, max_c = inputs['cost_range']
        mask &= (df['ContractCost'] >= min_c) & (df['ContractCost'] <= max_c)
    if inputs.get('duration_range'):
        min_d, max_d = inputs['duration_range']
        mask &= (df['Duration'] >= min_d) & (df['Duration'] <= max_d)
    risk_option = inputs.get('risk_filter')
    if risk_option == "Exact Match (Score = 1.0)":
        mask &= np.isclose(df['RiskScore'], 1.0)
    elif risk_option == "Over Budget (Score > 1.0)":
        mask &= (df['RiskScore'] > 1.0)
    elif risk_option == "At or Above Budget (Score ≥ 1.0)":
        mask &= (df['RiskScore'] >= 1.0)
    return df[mask]

def get_filters(df):
    inputs = {}

    with st.sidebar:
        st.header("Project Filters")
        inputs['risk_filter'] = st.radio("Filter by Risk Score",["All Projects", "Exact Match (Score = 1.0)", "Over Budget (Score > 1.0)", "At or Above Budget (Score ≥ 1.0)"],index=0,key=f"risk_radio")
        inputs['search_term'] = st.text_input("Project Name", placeholder="e.g., River Wall", key="search_term")
        inputs['search_id'] = st.text_input("Project ID", placeholder="e.g., P00...", key="search_id")

        regions = sorted(df['Region'].unique().tolist())
        inputs['selected_regions'] = st.multiselect("Region", regions)

        provinces = sorted(df['Province'].unique().tolist())
        inputs['selected_provinces'] = st.multiselect("Province", provinces)

        top_contractors = df['Contractor'].value_counts().index.tolist()
        inputs['selected_contractors'] = st.multiselect("Contractor", top_contractors)

        work_keys = sorted(TypeOfWork_dict.keys())
        selected_work_keys = st.multiselect("Type of Work", work_keys)
        inputs['selected_works'] = [TypeOfWork_dict[k] for k in selected_work_keys]

        if 'FundingYear' in df.columns:
            min_y = int(df['FundingYear'].min())
            max_y = int(df['FundingYear'].max())
            inputs['selected_years'] = st.slider("Funding Year", min_y, max_y, (min_y, max_y))
        else:
            inputs['selected_years'] = None
        min_cost = int(df['ContractCost'].min())
        max_cost = int(df['ContractCost'].max())
        if pd.isna(min_cost): min_cost = 0
        if pd.isna(max_cost): max_cost = 1

        manual = st.toggle("Manual Cost Input", value=False, key=f"toggle_cost")

        if manual:
            c1, c2 = st.columns(2)
            min_val = c1.number_input("Min Cost (PHP)", value=min_cost, min_value=0, key=f"min_cost")
            max_val = c2.number_input("Max Cost (PHP)", value=max_cost, min_value=0, key=f"max_cost")
            inputs['cost_range'] = (min_val, max_val)
        else:
            inputs['cost_range'] = st.slider("Contract Cost Range",min_value=min_cost,max_value=max_cost,value=(min_cost, max_cost),format="₱%d",key="cost_range")
        use_manual_dur = st.toggle("Manual Duration Input", value=False, key=f"toggle_dur")

        min_dur = int(df['Duration'].min())
        max_dur = int(df['Duration'].max())
        if use_manual_dur:
            c3, c4 = st.columns(2)
            min_d_val = c3.number_input("Min Duration (Days)", value=min_dur, key=f"min_dur")
            max_d_val = c4.number_input("Max Duration (Days)", value=max_dur, key=f"max_dur")
            inputs['duration_range'] = (min_d_val, max_d_val)
        else:
            inputs['duration_range'] = st.slider(
                "Duration Range (Days)",
                min_value=min_dur,
                max_value=max_dur,
                value=(min_dur, max_dur),
                format="%d days",
                key=f"slider_dur"
            )

        inputs['enable_clustering'] = st.toggle("Enable Clustering")
        if inputs['enable_clustering']:
            inputs['n_clusters'] = st.slider("Number of Zones (k)", 2, 10, 3)
        else:
            inputs['n_clusters'] = 3
    return inputs

@st.cache_data
def get_island_fig(df, chart_type):
    island_counts = df['MainIsland'].value_counts().reset_index()
    island_counts.columns = ['MainIsland', 'Count']
    if island_counts.empty: return None

    if chart_type == "Donut Chart":
        fig = px.pie(island_counts, values='Count', names='MainIsland', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Prism)
    else:
        fig = px.bar(island_counts, x='MainIsland', y='Count', color='Count',
                     color_continuous_scale='Viridis')
    fig.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=350)
    return fig

@st.cache_data
def get_region_fig(df, top_n):
    region_counts = df['Region'].value_counts().reset_index().head(top_n)
    region_counts.columns = ['Region', 'Count']
    if region_counts.empty: return None
    dynamic_height = 150 + (len(region_counts) * 25)
    fig = px.bar(region_counts, x='Count', y='Region', orientation='h',
                 text='Count', color='Count', color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=0, l=0, r=0), height=dynamic_height)
    return fig

@st.cache_data
def get_cost_hist_fig(df, dist_type, bin_count, use_log):
    if df.empty: return None
    if dist_type == "Contract Cost":
        fig = px.histogram(df, x="ContractCost", nbins=bin_count, title="Distribution of Contract Costs")
    else:
        fig = px.histogram(df, x="ApprovedBudgetForContract", nbins=bin_count, title="Distribution of Approved Budgets")
    if use_log:
        fig.update_layout(yaxis_type="log")
    fig.update_layout(bargap=0.1, margin=dict(t=30, b=0, l=0, r=0))
    return fig

@st.cache_data
def get_project_type_fig(df, chart_type):
    tow_counts = df['TypeOfWork'].value_counts().reset_index().head(10)
    tow_counts.columns = ['TypeOfWork', 'Count']
    if tow_counts.empty: return None
    dynamic_height = 400
    if chart_type == "Bar Chart":
        dynamic_height = 150 + (len(tow_counts) * 30)
        fig = px.bar(tow_counts, x='TypeOfWork', y='Count', color='TypeOfWork', title="Top 10 Project Types by Volume")
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    else:
        fig = px.pie(tow_counts, values='Count', names='TypeOfWork', title="Top 10 Project Types by Volume")
    fig.update_layout(height=dynamic_height)
    return fig

@st.cache_data
def get_contractor_figs(df):
    con_val = df.groupby('Contractor')['ContractCost'].sum().sort_values(ascending=False).head(20).reset_index()
    dynamic_height = 150 + (20 * 25)
    if not con_val.empty:
        fig_val = px.bar(con_val, x='ContractCost', y='Contractor', orientation='h',
                         title=f"Top {20} Contractors by Value",
                         text_auto='.2~s', color='ContractCost', color_continuous_scale='Viridis')
        fig_val.update_layout(yaxis={'categoryorder':'total ascending'}, height=dynamic_height)
    else:
        fig_val = None

    con_count = df['Contractor'].value_counts().head(20).rename_axis('Contractor').reset_index(name='Count')
    if not con_count.empty:
        fig_vol = px.bar(con_count, x='Count', y='Contractor', orientation='h',
                         title=f"Top {20} Contractors by Volume",
                         text_auto=True, color='Count', color_continuous_scale='Inferno')
        fig_vol.update_layout(yaxis={'categoryorder':'total ascending'}, height=dynamic_height)
    else:
        fig_vol = None
    return fig_val, fig_vol

def plot_bid_variance(df):
    df_zoom = df[(df['BudgetVariance'] > -5) & (df['BudgetVariance'] < 10)]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_zoom['BudgetVariance'], bins=50, kde=True, color='darkred', ax=ax)
    ax.axvline(0, color='black', linestyle='--', label='Exact Budget Match')
    ax.set_title("Bid Variance Distribution")
    ax.set_xlabel("Variance % (0 = Bid matched Budget exactly)")
    ax.legend()
    return fig


def perform_clustering(df, n_clusters):
    cluster_df = df.copy()

    if len(cluster_df) < n_clusters:
        return None, None

    X = cluster_df[['latitude', 'longitude']]

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)

    cluster_df['Cluster_ID'] = kmeans.fit_predict(X)

    stats = cluster_df.groupby('Cluster_ID').agg({
        'ContractCost': ['count', 'mean', 'min', 'max'],
        'Duration': 'mean',
        'RiskScore': 'mean'
    }).reset_index()

    stats.columns = ['Cluster Zone', 'Project Count', 'Avg Cost', 'Min Cost', 'Max Cost', 'Avg Duration (Days)', 'Avg Risk Score']

    stats['Avg Cost'] = stats['Avg Cost'].apply(lambda x: f"₱{x:,.0f}")
    stats['Min Cost'] = stats['Min Cost'].apply(lambda x: f"₱{x:,.0f}")
    stats['Max Cost'] = stats['Max Cost'].apply(lambda x: f"₱{x:,.0f}")
    stats['Avg Duration (Days)'] = stats['Avg Duration (Days)'].round(0)
    stats['Avg Risk Score'] = stats['Avg Risk Score'].round(4)
    return cluster_df, stats

def create_map(df, center, zoom, n_clusters=3, enabled_clustering=False):
    if enabled_clustering:
        df, stats = perform_clustering(df, n_clusters)
    else:
        stats = []

    m = fm.Map(location=center, zoom_start=zoom, control_scale=True, prefer_canvas=True, tiles=None)
    TileLayer(
        tiles="https://controlmap.mgb.gov.ph/arcgis/rest/services/GeospatialDataInventory_Public/GDI_Detailed_Flood_Susceptibility_Public/MapServer/tile/{z}/{y}/{x}",
        attr="MGB Flood Hazard", name="MGB Flood Susceptibility", overlay=True, control=True, show=False, opacity=0.5
    ).add_to(m)
    TileLayer(
        tiles="https://controlmap.mgb.gov.ph/arcgis/rest/services/GeospatialDataInventory_Public/GDI_Detailed_Rain_induced_Landslide_Susceptibility_Public/MapServer/tile/{z}/{y}/{x}",
        attr="MGB Rain/Landslide",
        name="MGB Rain Induced Landslide Susceptibility",
        overlay=True,
        control=True,
        show=False,
        opacity=0.5
    ).add_to(m)

    TileLayer("Esri.WorldImagery", name="Satellite", show=True).add_to(m)
    TileLayer("CartoDB.DarkMatter", name="Dark Mode", show=False).add_to(m)
    TileLayer("OpenStreetMap", name="Street Map", show=False).add_to(m)

    fm.plugins.Fullscreen(position="bottomleft", title="Expand me", title_cancel="Exit me", force_separate_button=True).add_to(m)
    fg = fm.FeatureGroup(name="DPWH Projects)")

    if not df.empty:
        id, lats, lons = df['ProjectId'].values, df['latitude'].values, df['longitude'].values
        names, regions, costs = df['ProjectName'].values, df['Region'].values, df['ContractCost'].values
        startdates, enddates, durations = df['StartDate'].values, df['ActualCompletionDate'].values, df['Duration'].values
        contractors, fundingyears = df['Contractor'].values, df['FundingYear'].values
        legDist, Municipality, engDist = df['LegislativeDistrict'].values, df['Municipality'].values, df['DistrictEngineeringOffice'].values
        risks, tow_vals = df['RiskScore'].values, df['TypeOfWork'].values

        if enabled_clustering:
            cluster_ids = df['Cluster_ID'].values
        else:
            cluster_ids = [0] * len(df)

        for pid, lat, lon, name, region, cost, start, end, dur, cont, fund, ld, mun, ed, risk, tow, cluster_id in zip(id, lats, lons, names, regions, costs, startdates, enddates, durations, contractors, fundingyears, legDist, Municipality, engDist, risks, tow_vals, cluster_ids):
            formatted_cost = f"₱{cost:,.2f}"
            cid = int(cluster_id)
            if enabled_clustering:
                color = CLUSTER_COLORS[cid % len(CLUSTER_COLORS)]
            else:
                color = TypeOfWork_full_color.get(tow, 'blue')
            popup_html = f"""
                            <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; color: #333;">
                                <b style="font-size: 14px; color: #000;">{name}</b><br>
                                <span style="color: #006400; font-weight: bold;">{formatted_cost}</span> &bull; {tow} &bull; FY {fund}
                                <span style="color:{color}; font-weight:bold;"> {"Zone "+ str(cid) if enabled_clustering else ""}</span><br>
                                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ccc;">
                                <b>Loc:</b> {mun}, {ld} ({region})<br>
                                <b>Eng:</b> {ed}<br>
                                <b>Time:</b> {start} &ndash; {end} <i>({dur} days)</i><br>
                                <b>By:</b> {cont}<br>
                                <b>Risk Score: {risk:.2f} </b>
                            </div>
                        """
            iframe = branca.element.IFrame(html=popup_html, width="520px", height="190px")
            pp = fm.Popup(iframe, max_width=500)
            mark = fm.CircleMarker(
                location=[lat, lon], radius=3, fill=True, fill_opacity=0.7, tooltip=f"Project ID: {pid}", popup=pp,
                fill_color=color, color=color
            )
            fg.add_child(mark)
    fg.add_to(m)
    fm.LayerControl(position='bottomleft').add_to(m)
    return m, stats
