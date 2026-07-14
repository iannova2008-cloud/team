import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="전기차 화재 발생 현황 대시보드", layout="wide")
st.title("🚗 전기차 화재 발생 현황 분석 웹앱")
st.markdown("소방청 데이터를 기반으로 한 전기차 화재 발생 현황 대시보드입니다.")

# 2. 데이터 로드 함수 (캐싱 적용)
@st.cache_data
def load_data():
    # 파일 경로를 사용자 환경에 맞게 지정하세요.
    # 동일 폴더에 있다면 파일명만 적으시면 됩니다.
    df = pd.read_csv("소방청_전기차 화재 발생 현황_20241231.csv", encoding="cp949")
    
    # [탭2-① 지도 시각화용] 대한민국 주요 시도별 위경도 좌표 매핑 딕셔너리
    geo_coords = {
        '서울특별시': [37.5665, 126.9780],
        '부산광역시': [35.1796, 129.0756],
        '대구광역시': [35.8714, 128.6014],
        '인천광역시': [37.4563, 126.7052],
        '광주광역시': [35.1595, 126.8526],
        '대전광역시': [36.3504, 127.3848],
        '울산광역시': [35.5389, 129.3114],
        '세종특별자치시': [36.4800, 127.2890],
        '경기도': [37.4138, 127.5183],
        '강원특별자치도': [37.8228, 128.1555],
        '충청북도': [36.6356, 127.4913],
        '충청남도': [36.5184, 126.8000],
        '전북특별자치도': [35.7175, 127.1530],
        '전라남도': [34.8679, 126.9910],
        '경상북도': [36.5760, 128.5056],
        '경상남도': [35.4606, 128.2132],
        '제주특별자치도': [33.4996, 126.5312]
    }
    
    # 데이터프레임에 위도(latitude)와 경도(longitude) 컬럼 추가
    df['latitude'] = df['시도'].map(lambda x: geo_coords.get(x, [None, None])[0])
    df['longitude'] = df['시도'].map(lambda x: geo_coords.get(x, [None, None])[1])
    
    # 위경도 매핑 실패한 데이터(결측치) 제거
    df = df.dropna(subset=['latitude', 'longitude'])
    
    return df

# 데이터 불러오기
try:
    data = load_data()
except FileNotFoundError:
    st.error("데이터 파일을 찾을 수 없습니다. 파일명이 정확한지 확인해주세요.")
    st.stop()

# 3. 탭 구성 (발생 원인, 지역별 건수)
tab1, tab2 = st.tabs(["🔥 발생 원인 분석", "📍 지역별 건수 분석"])

# --- [탭1: 발생 원인] ---
with tab1:
    st.header("1. 화재 발생 요인별 현황")
    
    # 발화요인대분류별 건수 집계 및 정렬
    cause_df = data['발화요인대분류'].value_counts().reset_index()
    cause_df.columns = ['발화요인대분류', '화재건수']
    cause_df = cause_df.set_index('발화요인대분류')
    
    # Streamlit 내장 막대그래프 시각화
    st.subheader("💡 발화 요인 대분류별 건수 (막대 그래프)")
    st.bar_chart(cause_df)
    
    # 세부 데이터 테이블 표시
    with st.expander("🔍 상세 원인별(소분류) 데이터 보기"):
        detailed_cause = data.groupby(['발화요인대분류', '발화요인소분류']).size().reset_index(name='건수')
        st.dataframe(detailed_cause, use_container_width=True)

# --- [탭2: 지역별 건수] ---
with tab2:
    st.header("2. 지역별 화재 발생 현황")
    
    # ① 대한민국 지도를 통한 지역별 산점도
    st.subheader("🗺️ ① 대한민국 지도 내 지역별 발생 위치 (산점도)")
    st.markdown("※ 각 화재 발생 건이 해당 시도의 중심 좌표에 점으로 표시됩니다.")
    
    # st.map은 latitude, longitude 컬럼을 자동으로 인식해 지도를 그려줍니다.
    st.map(data[['latitude', 'longitude']])
    
    st.markdown("---")
    
    # ② 지역별 발생건수 (막대그래프)
    st.subheader("📊 ② 지역별 발생 건수 (막대 그래프)")
    
    # 시도별 건수 집계 및 정렬
    region_df = data['시도'].value_counts().reset_index()
    region_df.columns = ['시도', '화재건수']
    region_df = region_df.set_index('시도')
    
    # Streamlit 내장 막대그래프 시각화
    st.bar_chart(region_df)
    
    # 세부 데이터 테이블 표시
    with st.expander("🔍 지역별(시도/시군구) 상세 데이터 보기"):
        detailed_region = data.groupby(['시도', '시군구']).size().reset_index(name='건수')
        st.dataframe(detailed_region, use_container_width=True)
