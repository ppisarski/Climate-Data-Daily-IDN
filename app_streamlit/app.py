"""
Copyright © 2022 Pawel Pisarski
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import streamlit as st
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

pio.templates.default = "plotly_white"

PLOTLY_CONFIG = dict(displayModeBar=True, displaylogo=False)
PLOTLY_LAYOUT = dict(margin=dict(r=0, t=0, l=0, b=0), plot_bgcolor="rgba(0,0,0,0)")

STREAMLIT_STYLE = """
    <style>
        footer {visibility: hidden;}
        footer:after {
            content:'Copyright © 2022 Pawel Pisarski';
            visibility: visible;
            display: block;
            position: relative;
            padding: 5px;
            top: 2px;
        }
    </style>
"""


LABELS = dict(
    Tn="min temperature (°C)",
    Tx="max temperature (°C)",
    Tavg="avg temperature (°C)",
    RH_avg="avg humidity (%)",
    RR="rainfall (mm)",
    ss="sunshine duration (hour)",
    ff_x="max wind speed (m/s)",
    ddd_x="wind direction at maximum speed (°)",
    ff_avg="avg wind speed (m/s)",
    ddd_car="wind direction",
    station_name="Station",
    region_name="Region",
    province_name="Province",
)

MODELS = [
    "Bayesian Normal Prior",
    "Bayesian StudentT Prior",
    "Bayesian Cauchy Prior",
    "Frequentist LR",
    "Frequentist Ridge",
]


@st.cache(persist=False, allow_output_mutation=True)
def get_province_detail() -> pd.DataFrame:
    """
    Province in Indonesia identifier.
    """
    df = pd.read_csv(os.path.join("data", "province_detail.csv")).astype(dict(province_id="int8"))
    # print(df.info(memory_usage='deep'))
    return df.sort_values(by=["province_id"])


@st.cache(persist=False, allow_output_mutation=True)
def get_station_detail() -> pd.DataFrame:
    """
    The station which the data is recorded.
    Station id is included in climate data to differentiate which station record which data.
    """
    df = pd.read_csv(os.path.join("data", "station_detail.csv"))\
        .astype(dict(province_id="int8", region_id="int16", station_id="int16", latitude="float16", longitude="float16"))
    df = pd.merge(df, get_province_detail(), on="province_id", how="left")
    # print(df.info(memory_usage='deep'))
    return df.sort_values(by=["province_id", "region_id", "station_id"])


@st.cache(persist=False, allow_output_mutation=True)
def get_climate_data() -> pd.DataFrame:
    """
    Climate data in Indonesia from 2010 to 2020.
    """
    df = pd.read_csv(os.path.join("data", "climate_data.csv"))\
        .astype(dict(station_id="int16", Tn="float16", Tx="float16", Tavg="float16",
                     RH_avg="float16", RR="float16", ss="float16", ff_x="float16", ddd_x="float16", ff_avg="float16"))
    df.date = pd.to_datetime(df.date, dayfirst=True)
    df = pd.merge(df, get_station_detail(), on="station_id", how="left")
    # print(df.info(memory_usage='deep'))
    return df.sort_values(by=["province_id", "region_id", "station_id", "date"])


def show_station_map(df: pd.DataFrame):
    st.header("Stations Map")
    fig = go.Figure(layout=PLOTLY_LAYOUT)
    trace = go.Scattermapbox(
            name="Station?",
            lon=df.longitude,
            lat=df.latitude,
            text=df.station_name,
            mode="markers",
        )
    fig.add_trace(trace)
    # center on geometry from the dataframe
    # center = gdf.geometry.unary_union.centroid
    # center on indonesia geometry
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    center = world[world.name == 'Indonesia'].geometry.unary_union.centroid
    fig.update_layout(dict(
        mapbox_style="carto-positron",
        mapbox_center_lon=float(center.x),
        mapbox_center_lat=float(center.y),
        mapbox_zoom=3.8,
    ))
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)
    # with st.expander("Filtered Dataset"):
    #     st.dataframe(gdf[["station_id", "province_name", "region_name", "station_name"]].set_index("station_id")
    #                  .rename({"province_name": "Province", "region_name": "Region", "station_name": "Station"}))


def show_timeseries(df: pd.DataFrame):
    st.header("Timeseries")
    df = df.rename(columns=LABELS).set_index("date")
    var = st.selectbox("Variable", df.columns, index=2)

    col1, col2, col3 = st.columns(3)
    resample = col1.selectbox("Resample timeseries and average the data", [None, "Daily", "Weekly", "Monthly", "Quarterly", "Annually"])
    groupby = col2.selectbox("Group by and average the data", [None, "Province", "Region", "Station"])
    mode = col3.radio("Mode", ["lines", "markers"])

    if resample is None:
        if groupby is None:
            data = df.groupby("date").mean(numeric_only=True)
            data["date"] = data.index.get_level_values(0)
        else:
            data = df.groupby([groupby, "date"]).mean(numeric_only=True)
            data[groupby] = data.index.get_level_values(0)
            data["date"] = data.index.get_level_values(1)
    else:
        if groupby is None:
            data = df.resample(resample[0]).mean(numeric_only=True)
            data["date"] = data.index.get_level_values(0)
        else:
            data = df.groupby(groupby).resample(resample[0]).mean(numeric_only=True)
            data[groupby] = data.index.get_level_values(0)
            data["date"] = data.index.get_level_values(1)
    data = data.reset_index(drop=True)

    if "lines" in mode:
        fig = px.line(data, x="date", y=var, color=groupby)
    else:
        fig = px.scatter(data, x="date", y=var, color=groupby)

    fig.update_xaxes(rangeslider_visible=True)
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with st.expander("Correlation with other variables"):
        var2 = st.selectbox(f"{var} vs", data.columns, label_visibility="collapsed")
        fig = px.scatter(data, x=var, y=var2, color=groupby)
        st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)

    with st.expander("Dataset Summary"):
        if groupby is None:
            st.dataframe(data.describe())
        else:
            st.dataframe(data.set_index(groupby).describe())


def main():
    st.set_page_config(page_title="Climate Data", layout="wide")
    st.sidebar.title("Analysis")
    layout = st.sidebar.selectbox("Type", [
        "Explore Timeseries",
        "Model Timeseries",
    ])
    st.title(f"Climate Data - {layout}")
    climate_data_df = get_climate_data()
    station_detail_df = get_station_detail()

    col1, col2, col3 = st.columns(3)
    province = col1.selectbox("Province", [None, *np.sort(station_detail_df.province_name.unique())])
    if province is not None:
        station_detail_df = station_detail_df[station_detail_df.province_name == province]
    region = col2.selectbox("Region", [None, *np.sort(station_detail_df.region_name.unique())])
    if region is not None:
        station_detail_df = station_detail_df[station_detail_df.region_name == region]
    station = col3.selectbox("Station", [None, *np.sort(station_detail_df.station_name.unique())])
    if station is not None:
        station_detail_df = station_detail_df[station_detail_df.station_name == station]

    show_station_map(station_detail_df)
    stations = station_detail_df.station_id.tolist()

    if layout in ["Explore Timeseries"]:
        show_timeseries(climate_data_df[climate_data_df.station_id.isin(stations)])
    if layout in ["Model Timeseries"]:
        show_timeseries(climate_data_df[climate_data_df.station_id.isin(stations)])
    st.markdown(__doc__)
    # st.markdown(STREAMLIT_STYLE, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
