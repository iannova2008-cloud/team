import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="전기차 화재 발생 현황",
    layout="wide"
)

# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "소방청_전기차 화재 발생 현황_20241231(1).csv",
        encoding="cp949"
    )
    return df

df = load_data()

st.title("🚗 전기차 화재 발생 현황 분석")

tab1, tab2 = st.tabs(["📊 발생 원인", "🗺 지역별 발생 건수"])

# ======================================================
# 탭1
# ======================================================
with tab1:

    st.subheader("발화요인(대분류)")

    cause = (
        df["발화요인대분류"]
        .value_counts()
        .reset_index()
    )

    cause.columns = ["발화요인", "건수"]

    fig = px.bar(
        cause,
        x="발화요인",
        y="건수",
        text="건수",
        color="건수"
    )

    fig.update_layout(
        xaxis_title="발화요인",
        yaxis_title="발생건수"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("발화요인(소분류)")

    sub = (
        df["발화요인소분류"]
        .value_counts()
        .reset_index()
    )

    sub.columns = ["세부 원인", "건수"]

    fig2 = px.bar(
        sub,
        x="세부 원인",
        y="건수",
        text="건수",
        color="건수"
    )

    fig2.update_layout(
        xaxis_title="세부 원인",
        yaxis_title="발생건수"
    )

    st.plotly_chart(fig2, use_container_width=True)

# ======================================================
# 탭2
# ======================================================
with tab2:

    st.subheader("① 대한민국 지역별 발생 현황")

    region = (
        df["시도"]
        .value_counts()
        .reset_index()
    )

    region.columns = ["시도", "건수"]

    fig3 = px.scatter_geo(
        region,
        locations="시도",
        locationmode="country names",
        size="건수",
        hover_name="시도",
        projection="mercator"
    )

    fig3.update_geos(
        fitbounds="locations",
        visible=False
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    st.subheader("② 지역별 발생 건수")

    fig4 = px.bar(
        region,
        x="시도",
        y="건수",
        text="건수",
        color="건수"
    )

    fig4.update_layout(
        xaxis_title="지역",
        yaxis_title="발생건수"
    )

    st.plotly_chart(fig4, use_container_width=True)
