import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="전기차 화재 발생 현황 대시보드", layout="wide")
st.title("🚗 전기차 화재 발생 현황 분석 웹앱")
st.markdown("소방청 데이터를 기반으로 한 전기차 화재 발생 현황 대시보드입니다.")

# 2. 사이드바 설정 (점 크기 조절 및 수동 파일 업로더)
st.sidebar.header("⚙️ 시각화 설정")

# 지도 크기 배율 조절 슬라이더
size_multiplier = st.sidebar.slider(
    "📍 지도 상 점 크기 비율 조절", 
    min_value=1000, 
    max_value=10000, 
    value=3000, 
    step=500,
    help="건수 대비 지도에 표시되는 점의 반지름 크기(미터 단위)를 조절합니다."
)

st.sidebar.markdown("---")
st.sidebar.subheader("📂 데이터 수동 업로드 패널")
uploaded_file = st.sidebar.file_uploader(
    "GitHub에 CSV 파일이 없어서 에러가 난다면, 여기에 CSV 파일을 직접 끌어다 놓으세요.", 
    type=["csv"]
)

# 3. 데이터 로드 함수 (인코딩 문제 방지용 안전 장치 포함)
@st.cache_data
def load_data(file_source):
    try:
        # 한글 깨짐 방지를 위해 cp949 인코딩 먼저 시도
        df = pd.read_csv(file_source, encoding="cp949")
    except UnicodeDecodeError:
        # 실패할 경우 일반 utf-8로 인코딩 시도
        df = pd.read_csv(file_source, encoding="utf-8")
    return df

# 데이터 소스 연결 자동 전환 프로세스
data_loaded = False
if uploaded_file is not None:
    try:
        data = load_data(uploaded_file)
        data_loaded = True
        st.sidebar.success("성공적으로 업로드된 파일을 읽었습니다!")
    except Exception as e:
        st.sidebar.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
else:
    # 기본 경로에서 파일 탐색 시도
    default_filename = "소방청_전기차 화재 발생 현황_20241231.csv"
    try:
        data = load_data(default_filename)
        data_loaded = True
    except FileNotFoundError:
        st.error("⚠️ 서버(GitHub) 공간에서 '소방청_전기차 화재 발생 현황_20241231.csv' 파일을 찾지 못했습니다.")
        st.warning(
            "💡 **즉시 해결 방법:**\n"
            "왼쪽 사이드바에 있는 **'데이터 수동 업로드 패널'**에 컴퓨터 속 CSV 파일을 직접 마우스로 끌어다 놓으시면(Drag & Drop) 깃허브 업로드 상태와 관계없이 대시보드가 즉시 화면에 나타납니다."
        )
        st.stop()

# 4. 지도 매핑을 위한 주요 시도별 중심 위도/경도 데이터 사전 정의
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

# 5. 탭 구성 (발생 원인, 지역별 건수)
tab1, tab2 = st.tabs(["🔥 발생 원인 분석", "📍 지역별 건수 분석"])

# --- [탭1: 발생 원인] ---
with tab1:
    st.header("1. 화재 발생 요인별 현황")
    
    # 대분류별 건수 카운트 후 정렬
    cause_df = data['발화요인대분류'].value_counts().reset_index()
    cause_df.columns = ['발화요인대분류', '화재건수']
    cause_df = cause_df.set_index('발화요인대분류')
    
    # 순수 Streamlit 내장 차트로만 시각화 구현
    st.subheader("💡 발화 요인 대분류별 건수 (막대 그래프)")
    st.bar_chart(cause_df)
    
    with st.expander("🔍 상세 원인별(소분류) 데이터 테이블 보기"):
        detailed_cause = data.groupby(['발화요인대분류', '발화요인소분류']).size().reset_index(name='건수')
        st.dataframe(detailed_cause, use_container_width=True)


# --- [탭2: 지역별 건수] ---
with tab2:
    st.header("2. 지역별 화재 발생 현황")
    
    # ① 대한민국 지도를 통한 지역별 산점도 (건수별 크기 제어)
    st.subheader("🗺️ ① 지역별 화재 발생 건수 시각화 (건수 반영 지도)")
    st.markdown(
        "각 시도별 중심지에 **화재 발생 빈도에 비례하는 크기의 원**이 표시됩니다. "
        "화재 건수가 집중된 지역일수록 점의 크기가 커집니다."
    )
    
    # 데이터 가공 단계
    map_data = data['시도'].value_counts().reset_index()
    map_data.columns = ['시도', '화재건수']
    
    # 미리 준비한 위경도 컬럼 매핑
    map_data['latitude'] = map_data['시도'].map(lambda x: geo_coords.get(x, [None, None])[0])
    map_data['longitude'] = map_data['시도'].map(lambda x: geo_coords.get(x, [None, None])[1])
    map_data = map_data.dropna(subset=['latitude', 'longitude'])
    
    # [건수 반영 핵심] 화재 발생 수치에 슬라이더 배율을 곱해 점 크기 설정
    map_data['size'] = map_data['화재건수'] * size_multiplier
    
    # 화재 지점 구분을 위한 반투명 레드 컬러 코드 정의
    map_data['color'] = "#FF4B4BA0"
    
    # Streamlit 내장 지도로 렌더링
    st.map(
        map_data, 
        latitude='latitude', 
        longitude='longitude', 
        size='size', 
        color='color',
        use_container_width=True
    )
    
    st.markdown("---")
    
    # ② 지역별 발생건수 (막대그래프)
    st.subheader("📊 ② 지역별 발생 건수 (막대 그래프)")
    
    # 시도 명칭을 축으로 세팅하여 차트 연결
    region_chart_df = map_data.set_index('시도')[['화재건수']]
    st.bar_chart(region_chart_df)
    
    with st.expander("🔍 시도 및 시군구 단위 세부 화재 데이터 보기"):
        detailed_region = data.groupby(['시도', '시군구']).size().reset_index(name='건수')
        st.dataframe(detailed_region, use_container_width=True)
