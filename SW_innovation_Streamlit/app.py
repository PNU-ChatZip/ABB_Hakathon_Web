from folium.map import Marker
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import geopandas as gpd

import streamlit as st
import folium
from datetime import datetime
from folium import IFrame

import pandas as pd
import random
from io import BytesIO
from geopy.geocoders import Nominatim

import requests
import threading
import time

# 경고 메시지 숨기기
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(layout="wide")

# 부산의 구 리스트
busan_districts = [
    '중구', '서구', '동구', '영도구', '부산진구', '동래구', '남구', '북구',
    '해운대구', '사하구', '금정구', '강서구', '연제구', '수영구', '사상구'
]
districts_centers = {
    '중구': (35.10321667, 129.0345083),
    '서구': (35.09483611, 129.022010),
    '동구': (35.13589444, 129.059175),
    '영도구': (35.08811667, 129.0701861),
    '부산진구': (35.15995278, 129.0553194),
    '동래구': (35.20187222, 129.0858556),
    '남구': (35.13340833, 129.0865),
    '북구': (35.19418056, 128.992475),
    '해운대구': (35.16001944, 129.1658083),
    '사하구': (35.10142778, 128.9770417),
    '금정구': (35.24007778, 129.0943194),
    '강서구': (35.20916389, 128.9829083),
    '연제구': (35.17318611, 129.082075),
    '수영구': (35.14246667, 129.115375),
    '사상구': (35.14946667, 128.9933333)
}

ACCIDENT_DATA_URL = "http://waterboom.iptime.org:1101/receive-accident-location"
FORTHOLE_DATA_URL = "http://waterboom.iptime.org:1101/receive-forthole-location"


def fetch_and_format_accident_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        # 실제 데이터를 JSON 형태로 변환
        data = response.json()
        # JSON 데이터를 DataFrame으로 변환
        accidents_df = pd.DataFrame(data)
        
        # 샘플 데이터 형식에 맞추어 컬럼 변환
        formatted_df = pd.DataFrame({
            'id' : accidents_df['id'],
            'type': accidents_df['progress'],
            'category': accidents_df['type'],  
            'date': pd.to_datetime(accidents_df['time']),  # 'time'을 datetime 형식으로 변환
            'district': accidents_df['area2'],  # 'district'는 'area2' 값 사용
            'description': accidents_df['type'],  # 'description'은 'type' 값 사용
            'detail_location': accidents_df['road'],
            'location': list(zip(accidents_df['latitude'], accidents_df['longitude']))  # 'location'은 'latitude'와 'longitude'를 튜플로 묶음
        })
        return formatted_df
    else:
        st.error("Failed to fetch data")
        return pd.DataFrame()


# 샘플 데이터 생성
sample_data = {
    'id':[1,2,3],
    'type':['discoverd', 'checked', 'finished'],
    'category': ['차량 사고', '도로 막힘', '포트홀'],
    'date': pd.date_range(start="2023-01-01", periods=100, freq='D').to_pydatetime().tolist(),
    'district': random.choices(busan_districts, k=100),
    'description': ['사고 발생', '체증 심함', '포트홀 발생'],
    'detail_location': ['부산광역시 중구 대청동 1-1', '부산광역시 중구 대청동 1-2', '부산광역시 중구 대청동 1-3'],
    'location': [(random.uniform(35.05, 35.20), random.uniform(128.97, 129.15)) for _ in range(100)]
}
def init_district_data():
    if 'page' not in st.session_state:
        st.session_state.page = 0
    
    if 'init_data_loaded' not in st.session_state:
        # DataFrame 생성
        accidents_df = fetch_and_format_accident_data(ACCIDENT_DATA_URL)
        forthole_df = fetch_and_format_accident_data(FORTHOLE_DATA_URL)
        accidents_df = pd.concat([accidents_df, forthole_df])
        st.session_state['districts_data'] = {
        '중구': ['26110'],
        '서구': ['26140'],
        '동구': ['26170'],
        '영도구': ['26200'],
        '부산진구': ['26230'],
        '동래구': ['26260'],
        '남구': ['26290'],
        '북구': ['26320'],
        '해운대구': ['26350'],
        '사하구': ['26380'],
        '금정구': ['26410'],
        '강서구': ['26440'],
        '연제구': ['26470'],
        '수영구': ['26500']
        }
        EMD = gpd.read_file('LSMD_ADM_SECT_UMD_26_202309.shp', encoding='cp949')
        st.session_state.yi4326 = EMD.to_crs(epsg=4326)

        # 세션 상태에 데이터 저장
        st.session_state['accidents_df'] = accidents_df
        st.session_state['init_data_loaded'] = True
    else:
        # 세션 상태에서 데이터 로드
        accidents_df = st.session_state['accidents_df']
        district_data = st.session_state['districts_data']
        yi4326 = st.session_state['yi4326']


def get_average_center(district_names):
    latitudes = [districts_centers[district][0] for district in district_names]
    longitudes = [districts_centers[district][1] for district in district_names]
    avg_lat = sum(latitudes) / len(latitudes)
    avg_lng = sum(longitudes) / len(longitudes)
    return (avg_lat, avg_lng)

# 지도 생성 함수
def create_map(data, district_name=None, marker=False):
    category_color_map = {
        '차량 사고': 'red',
        '도로 막힘': 'orange',
        '포트홀': 'blue'
    }
    with st.spinner('Wait for it...'):
        # 만약 특정 지역구가 선택되면 해당 지역구의 중심으로 지도 중심 설정
        if district_name and all(name in districts_centers for name in district_name):
            center_location = get_average_center(district_name)
            m = folium.Map(location=center_location, zoom_start=13.5)  # zoom level은 적절히 조정
        else:
            m = folium.Map(location=[35.15, 129.05], zoom_start=11)
        
        if marker==1:    
            category_clusters = {category: MarkerCluster(name=category) for category in category_color_map}

        if district_name:
            # 각 지역구에 속하는 행정동 리스트 추출
            dong_list = []
            for district in district_name:
                dong_list.extend(st.session_state['districts_data'].get(district, []))
            dong_geo = st.session_state['yi4326'][st.session_state['yi4326']['COL_ADM_SE'].isin(dong_list)]
            for _, row in dong_geo.iterrows():
                geojson = folium.GeoJson(
                    row['geometry'],
                    name=row['EMD_NM'],
                    style_function=lambda x: {'fillColor': 'green', 'color': 'green', 'weight': 2, 'fillOpacity': 0.1}
                )
                geojson.add_child(folium.Tooltip(row['EMD_NM']))
                geojson.add_to(m)

        
        acc_dict = {'차량 사고':'accident', '도로 막힘':'traffic_jam', '포트홀':'forthole'}
        status_description = {'finished':'완료', 'checked':'확인', 'discovered':'발견'}
        for _, accident in data.iterrows():
            icon_color = category_color_map[accident['category']]  # 카테고리별 색상을 얻음, 기본은 회색
            icon = folium.Icon(color=icon_color)
            status_class = {
            'finished': 'status-complete',
            'checked': 'status-hold',
            'discovered': 'status-pending'
            }[accident['type']]
            iframe = folium.IFrame(html=f"""
            <div>
                <style>
                    .status-indicator {{
                        height: 10px;
                        width: 10px;
                        background-color: #bbb;
                        border-radius: 50%;
                        display: inline-block;
                    }}
                    .status-complete {{ background-color: #4CAF50; }} /* Green */
                    .status-hold {{ background-color: #FFEB3B; }} /* Yellow */
                    .status-pending {{ background-color: #F44336; }} /* Red */
                </style>
            </div>
                <span class="status-indicator {status_class}"></span>
                <span class="status-description">{status_description[accident['type']]}</span>
            <div style="font-family: Arial; text-align: center;">
                <h4>{accident['category']} 사고</h4>
                <hr style="margin: 1px;">
                <p><strong>날짜:</strong> {accident['date'].strftime('%Y-%m-%d')}</p>
                <p><strong>시군구:</strong> {accident['district']}</p>
                <p><strong>설명:</strong> {accident['description']}</p>
                <div>
                    <style>
                        .complete-button {{
                            padding: 10px 15px;
                            background-color: #4CAF50; /* Green */
                            color: white;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            font-family: Arial;
                            margin-right: 5px; /* Add some space between the buttons */
                        }}

                        .hold-button {{
                            padding: 10px 15px;
                            background-color: #FF9800; /* Orange */
                            color: white;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            font-family: Arial;
                        }}
                        
                        .complete-button:hover, .hold-button:hover {{
                            opacity: 0.8;
                        }}
                        
                        .complete-button:active, .hold-button:active {{
                            opacity: 0.6;
                        }}
                        
                        .button-icon {{
                            padding-right: 5px;
                        }}
                    </style>

                    <button class="complete-button" onclick="sendGetRequest({accident['id']},'{acc_dict[accident['category']]}','finished'); alert('완료처리되었습니다.');">
                        <span class="button-icon">&#10004;</span> 완료
                    </button>
                    
                    <button class="hold-button" onclick="sendGetRequest({accident['id']},'{acc_dict[accident['category']]}','checked');  alert('확인 처리되었습니다.');">
                        <span class="button-icon">&#9888;</span> 확인
                    </button>
                    
                    <script>
                    function sendGetRequest(id, type, progress) {{
                        const url = `http://waterboom.iptime.org:1101/update-location-progress?id=${{id}}&type=${{type}}&progress=${{progress}}`;

                        fetch(url)
                        .then(response => {{
                            if (!response.ok) {{
                                throw new Error('Network response was not ok ' + response.statusText);
                            }}
                            return response.json();
                        }})
                        .then(data => {{
                            console.log('Success:', data);
                            // Handle success here
                        }})
                        .catch((error) => {{
                            console.error('Error:', error);
                            // Handle errors here
                        }});
                    }}
                    </script>
                </div>
            """, width=200, height=200)
            popup = folium.Popup(iframe, max_width=2650)
            
            if marker==0:
                folium.CircleMarker(
                location=accident['location'],
                radius=4,  # Smaller size
                color=icon_color,
                fill=True,
                fill_color=icon_color,
                fill_opacity=0.8,
                popup=popup,
                icon=icon,
                tooltip=f"{accident['category']} - {accident['date'].strftime('%Y-%m-%d')}"
            ).add_to(m)
            else:
                folium.CircleMarker(
                    location=accident['location'],
                    radius=4,  # Smaller size
                    color=icon_color,
                    fill=True,
                    fill_color=icon_color,
                    fill_opacity=0.8,
                    popup=popup,
                    icon=icon,
                    tooltip=f"{accident['category']} - {accident['date'].strftime('%Y-%m-%d')}"
                ).add_to(category_clusters[accident['category']])
                for cluster in category_clusters.values():
                    cluster.add_to(m)

        folium.LayerControl().add_to(m)
    return m

def filter_accidents():
    date_filter = [pd.to_datetime(date).to_pydatetime() for date in st.session_state['date_range']] if len(st.session_state['date_range']) == 2 else None
    current_category = st.session_state['category_select_key']
    current_districts = st.session_state['districts_select_key']
    
    category_condition = (st.session_state['accidents_df']['category'] == current_category) if current_category != '전체' else True
    district_condition = st.session_state['accidents_df']['district'].isin(current_districts)
    
    if current_category and current_districts:
        if date_filter:
            date_condition = (
                (st.session_state['accidents_df']['date'] >= date_filter[0]) &
                (st.session_state['accidents_df']['date'] <= date_filter[1])
            )
            return st.session_state['accidents_df'][category_condition & date_condition & district_condition]
        else:
            return st.session_state['accidents_df'][category_condition & district_condition]
    else:
        return pd.DataFrame()

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        # 변경된 부분: writer.save() 대신 writer.close() 사용
    processed_data = output.getvalue()

    return processed_data

def download_excel(df):
    excel_file = to_excel(df)
    st.download_button(
        label="Download Excel file",
        data=excel_file,
        file_name="data.xlsx",
        mime="application/vnd.ms-excel"
    )

def main():
    init_district_data()
    # 사이드바 설정
    st.sidebar.title("사고 검색 옵션")
    category = st.sidebar.selectbox(
        '사고 카테고리',
        options=['전체'] + sample_data['category'],
        key='category_select_key',
        on_change=filter_accidents
    )

    # 날짜 범위 선택
    if 'date_range' not in st.session_state:
        st.session_state['date_range'] = []

    st.session_state['date_range'] = st.sidebar.date_input(
        '날짜 범위 선택',
        [],
        key='date_range_key',
        on_change=filter_accidents
    )

    # 시군구 선택
    selected_districts = st.sidebar.multiselect(
        '시군구 선택',
        options=busan_districts,
        default=busan_districts,
        key='districts_select_key',
        on_change=filter_accidents
    )
    st.title(" 🌐 B - MAP")
    # 사이드바에 데이터프레임을 표시)

    filtered_data = filter_accidents()
    st.sidebar.write("Filtered Data", filtered_data)
    
    col1, col2, space, col3 = st.columns([1.2,1,2.2,2])

    # 첫 번째 열에 "전체 데이터 보기" 버튼 배치
    with col1:
        if st.button("전체 데이터 보기"):
            st.session_state.page = 0

    # 두 번째 열에 "클러스터 보기" 버튼 배치
    with col2:
        if st.button("클러스터 보기"):
            st.session_state.page = 1

    # 세 번째 열에 엑셀 다운로드 버튼 배치
    with col3:
        download_excel(filtered_data)

    map_fig = create_map(filtered_data, district_name=st.session_state['districts_select_key'],marker=st.session_state.page)

    st_folium(map_fig, width='100%')
if __name__ == '__main__':
    main()