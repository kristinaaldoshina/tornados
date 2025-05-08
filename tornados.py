import streamlit as st
import base64
import duckdb
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import joblib
import math
import datetime as dt


# <>>>--- FUNCTIONS ---<<<>

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def convert_damage(x):
    if not isinstance(x, str) or x.strip() == '':
        return pd.NA
    try:
        if 'K' in x:
            return int(float(x.replace('K', '')) * 1_000)
        elif 'M' in x:
            return int(float(x.replace('M', '')) * 1_000_000)
        elif 'B' in x:
            return int(float(x.replace('M', '')) * 1_000_000_000)
        else:
            return pd.NA
    except ValueError:
        return pd.NA


@st.cache_data
def load_tornados_data():
    file_path = "usa_tornados_xxi.csv"
    df = duckdb.sql(f"SELECT * FROM '{file_path}'").df()
    columns_to_keep = ['begin_yearmonth', 'begin_day', 'begin_time', 'end_yearmonth', 'end_day', 'end_time', 
                       'episode_id', 'event_id', 'state', 'year', 'month_name', 'begin_date_time', 
                       'cz_timezone', 'end_date_time', 'injuries_direct', 'injuries_indirect', 'deaths_direct', 'deaths_indirect',
                       'damage_property', 'damage_crops', 'magnitude', 'magnitude_type', 'tor_f_scale', 'tor_length',
                       'tor_width', 'begin_range', 'begin_azimuth', 'begin_location', 'end_range', 'end_azimuth',
                       'end_location', 'begin_lat', 'begin_lon', 'end_lat', 'end_lon', 'episode_narrative',
                       'event_narrative', 'fat_yearmonth', 'fat_day', 'fat_time', 'fatality_id', 'fatality_type',
                       'fatality_date', 'fatality_age', 'fatality_sex', 'fatality_location', 'event_yearmonth']
    df.columns = df.columns.map(lambda x: x.lower())
    df = df[columns_to_keep]
    date_columns = ['begin_date_time', 'end_date_time', 'fatality_date']
    df[date_columns[:2]] = df[date_columns[:2]].apply(lambda column: pd.to_datetime(column, format='%d-%b-%y %H:%M:%S', errors='coerce'))
    df[date_columns[2]] = df[date_columns[2]].apply(lambda column: pd.to_datetime(column, format='%m/%d/%Y %H:%M:%S', errors='coerce'))
    damage_columns = ['damage_property', 'damage_crops']
    df[damage_columns] =df[damage_columns].fillna('')
    df[damage_columns] = df[damage_columns].map(convert_damage).astype('Int64')
    fat_columns = ['fat_yearmonth', 'fat_day', 'fat_time', 'fatality_id']
    df[fat_columns] =df[fat_columns].astype('Int32')
    df['tor_f_scale'] = df['tor_f_scale'].map(lambda x: x.replace('E', '').replace('FU', 'unknown'))
    df['tor_length'] = round(df['tor_length'] * 1.60934, 2)
    df['tor_width'] = round(df['tor_width'] * 0.9144, 2)
    df['state'] = df['state'].map(lambda x: x.title())
    df['tor_duration_minutes'] = (df['end_date_time'] - df['begin_date_time']).map(lambda x: round(x.total_seconds() /60, 2))
    return df


@st.cache_data
def load_states_geojson():
    url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def draw_map(df, column):
    states_geojson = load_states_geojson()
    fig = px.choropleth(
        df,
        geojson=states_geojson,
        locations="state",
        featureidkey="properties.name",
        color=column,
        color_continuous_scale='RdYlGn_r',
        projection="mercator",)
    fig.update_geos(
        center={"lat": 43, "lon": -120},
        projection_scale=3.3,
        visible=False,
        showland=True,
        landcolor="#BEBDBD",
        showocean=False,
        bgcolor="rgba(0,0,0,0)",)
    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0},
        autosize=True,
        height=300,
        coloraxis_colorbar=dict(title='', len=1.0, thickness=20, y=0.5, yanchor="middle"),
        paper_bgcolor="rgba(0,0,0,0)",)
    return fig


def day_part(x):
    if x in range(6, 13):
        return 'Morning'
    elif x in range(12, 19):
        return 'Day'
    elif x in range(18, 25):
        return 'Evening'
    else:
        return 'Night'
    

def apply_custom_sort(df, column, sort_list):
    df[column] = pd.Categorical(df[column], categories=sort_list, ordered=True)
    return df.sort_values(column)


def init_session_state():
    defaults = {"year_filter_tab3": [],
                "month_filter_tab3": [],
                "day_filter_tab3": [],
                "weekday_filter_tab3": [],
                "hour_filter_tab3": [],
                "fscale_filter_tab3": [],
                "year_filter_tab5": [],
                "month_filter_tab5": [],
                "day_filter_tab5": [],
                "weekday_filter_tab5": [],
                "hour_filter_tab5": [],
                'fscale_filter_tab5': [],
                "year_filter_tab6": [],
                "month_filter_tab6": [],
                "day_filter_tab6": [],
                "weekday_filter_tab6": [],
                "hour_filter_tab6": [],
                'fscale_filter_tab6': [],
                "year_filter_tab7": [],
                "month_filter_tab7": [],
                "day_filter_tab7": [],
                "weekday_filter_tab7": [],
                "hour_filter_tab7": [],
                'fscale_filter_tab7': [],
                "input_1_tab4": "",
                "input_2_tab4": "",
                "input_3_tab4": "F0",
                "clear_inputs_tab4": False,
                "input_1_tab5": "",
                "input_2_tab5": "",
                "input_3_tab5": "",
                "input_4_tab5": "",
                "input_5_tab5": "Alabama",
                "input_6_tab5": "F0",
                "clear_inputs_tab5": False,
                "input_1_tab6": "",
                "input_2_tab6": "",
                "input_3_tab6": "",
                "input_4_tab6": "",
                "input_5_tab6": "January",
                "input_6_tab6": "F0",
                "input_7_tab6": "Alabama",
                "input_8_tab6": "",
                "clear_inputs_tab6": False,
                "input_1_tab7": "",
                "input_2_tab7": "",
                "input_3_tab7": "",
                "input_4_tab7": "January",
                "clear_inputs_tab7": False,
                "damage_type": "damages",
                "injury_type": "injuries",
                "death_type": "deaths",
                "prediction_tab4": "",}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# <>>>--- SESSION SETTINGS ---<<<>

init_session_state()

year_selected_tab3 = st.session_state.get("year_filter_tab3", [])
month_selected_tab3 = st.session_state.get("month_filter_tab3", [])
day_selected_tab3 = st.session_state.get("day_filter_tab3", [])
weekday_selected_tab3 = st.session_state.get("weekday_filter_tab3", [])
hour_selected_tab3 = st.session_state.get("hour_filter_tab3", [])
fscale_selected_tab3 = st.session_state.get('fscale_filter_tab3', [])

year_selected_tab5 = st.session_state.get("year_filter_tab5", [])
month_selected_tab5 = st.session_state.get("month_filter_tab5", [])
day_selected_tab5 = st.session_state.get("day_filter_tab5", [])
weekday_selected_tab5 = st.session_state.get("weekday_filter_tab5", [])
hour_selected_tab5 = st.session_state.get("hour_filter_tab5", [])
fscale_selected_tab5 = st.session_state.get('fscale_filter_tab5', [])
damage_type_selected = st.session_state.get("damage_type", "damages")
damage_column = damage_type_selected

year_selected_tab6 = st.session_state.get("year_filter_tab6", [])
month_selected_tab6 = st.session_state.get("month_filter_tab6", [])
day_selected_tab6 = st.session_state.get("day_filter_tab6", [])
weekday_selected_tab6 = st.session_state.get("weekday_filter_tab6", [])
hour_selected_tab6 = st.session_state.get("hour_filter_tab6", [])
fscale_selected_tab6 = st.session_state.get('fscale_filter_tab6', [])
injury_type_selected = st.session_state.get("injury_type", "injuries")
injury_column = injury_type_selected

year_selected_tab7 = st.session_state.get("year_filter_tab7", [])
month_selected_tab7 = st.session_state.get("month_filter_tab7", [])
day_selected_tab7 = st.session_state.get("day_filter_tab7", [])
weekday_selected_tab7 = st.session_state.get("weekday_filter_tab7", [])
hour_selected_tab7 = st.session_state.get("hour_filter_tab7", [])
fscale_selected_tab7 = st.session_state.get('fscale_filter_tab7', [])
death_type_selected = st.session_state.get("death_type", "deaths")
death_column = death_type_selected

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Home"

# <>>>--- PAGE SETTINGS ---<<<>

st.set_page_config(layout="wide", page_title="Tornados", page_icon="🌪️")
local_image_path ="tornados_background_light.png"
encoded_image = get_base64_of_bin_file(local_image_path)

layout_css = f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{encoded_image}");
    background-size: 100% 100%;
    background-position: top center;
    background-attachment: fixed;
    background-repeat: no-repeat;}}</style>"""
st.markdown(layout_css, unsafe_allow_html=True)

# <>>>--- DATA TO USE ---<<<>

tornados = load_tornados_data()

# <>>>--- TABS ---<<<>

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["Home", "About", "Summary", "Dynamics", "Damages", "Injuries", "Deaths"])

# <>>>--- TAB 1 ---<<<> HOME

with tab1:

    st.markdown("""<h1 style= 'text-align: center; margin-top: 14rem;'>Tornados in the USA in the 21st century</h1>""", 
                unsafe_allow_html=True)
    st.markdown("""<p style= 'text-align: center;'>Aldošina K., Belanova K., Korostelyova A., Urmonaitė M., Vosylius P.</p>""",
                unsafe_allow_html=True)

# <>>>--- TAB 2 ---<<<> ABOUT

with tab2:
    if st.session_state["active_tab"] != "About":
        st.session_state["active_tab"] = "About"

    st.markdown("""  
        <p>This webpage contains an interactive analysis of tornados in the USA in the 21st century.
        <br>You can find more information about the dataset 
            <a href="https://www.ncdc.noaa.gov/stormevents/ftp.jsp" target="_blank" style="color: black;">here.</a>
        <br>Here is a sample of the preprocessed dataset used in this analysis. One row is one unique tornado.</p>
        """, unsafe_allow_html=True)
    
    st.dataframe(tornados.sample(6))

    with open("tornados_docs.md", "r") as f:
        st.expander("See dataset documentation").markdown(f.read())

# <>>>--- TAB 3 ---<<<> SUMMARY

year_list = list(range(2000, 2025))
month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
day_list = list(range(1, 32))
weekday_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hour_list = list(range(0, 25))
fscale_list = ['F0', 'F1', 'F2', 'F3', 'F4', 'F5', 'unknown']
state_list = sorted(tornados['state'].unique())

with tab3:

    if st.session_state["active_tab"] != "Summary":
        st.session_state["active_tab"] = "Summary"

    tornados_filtered = tornados.copy()

    tornados_filtered = tornados_filtered[tornados_filtered['year'].isin(year_selected_tab3)] if year_selected_tab3 else tornados_filtered
    tornados_filtered = tornados_filtered[tornados_filtered['month_name'].isin(month_selected_tab3)] if month_selected_tab3 else tornados_filtered
    tornados_filtered = tornados_filtered[tornados_filtered['begin_day'].isin(day_selected_tab3)] if day_selected_tab3 else tornados_filtered
    tornados_filtered = tornados_filtered[tornados_filtered['begin_date_time'].dt.day_name().isin(weekday_selected_tab3)] if weekday_selected_tab3 else tornados_filtered
    tornados_filtered = tornados_filtered[tornados_filtered["begin_time"].astype(str).str.zfill(4).str[:2].isin(str(h) for h in hour_selected_tab3)] if hour_selected_tab3 else tornados_filtered
    tornados_filtered = tornados_filtered[tornados_filtered['tor_f_scale'].isin(fscale_selected_tab3)] if fscale_selected_tab3 else tornados_filtered

    cols = st.columns([0.14, 0.14, 0.14, 0.14, 0.14, 0.3])

    with cols[0]:
        total_amount = tornados_filtered['event_id'].nunique()
        st.metric("Total amount", 
                  total_amount, 
                  help="Total amount of tornados")
    
    with cols[1]:
        weekday_mode = tornados_filtered['begin_date_time'].dt.day_name().mode()
        most_weekday = weekday_mode[0][:3] if not weekday_mode.empty else '-'
        st.metric("Usually starts on", 
                  most_weekday, 
                  help="Day of the week when tornado appears")
    
    with cols[2]:
        daypart_mode = tornados_filtered['begin_date_time'].dropna().dt.hour.apply(day_part).mode()
        most_daypart = daypart_mode[0] if not daypart_mode.empty else "-"
        st.metric("Usually starts in", 
                  most_daypart, 
                  help="Time of the day when tornado appears, 6-12: morning, 12-18: day, 18-24: evening, 24-6: night")
    
    with cols[3]:
        avg_duration = round(tornados_filtered['tor_duration_minutes'].mean())
        average_duration = str(avg_duration) + ' min' if not math.isnan(avg_duration) else "-"
        st.metric("Average duration", 
                  average_duration, 
                  help="Average duration of a tornado in minutes")
    
    with cols[4]:
        st.metric("Total fatalities", 
                  tornados_filtered['fatality_id'].count() if total_amount > 0 else '-',
                  help="Total amount of direct or indirect injuries or deaths")
    
    with cols[5]:
        fatality_mode = tornados_filtered['fatality_location'].dropna().mode()
        most_fatality = fatality_mode[0] if not fatality_mode.empty else "-"
        st.metric("Usual fatality",
                  most_fatality, 
                  help="Place of the most often fatality - injury or death")
    
    st.divider()
           
    col1, col2 = st.columns(2)

    with col1:
        filter_keys = ['year_filter_tab3', 'month_filter_tab3', 'day_filter_tab3', 
                       'weekday_filter_tab3', 'hour_filter_tab3', 'fscale_filter_tab3']
        if st.button("Clear all filters", key="clear_filters_tab3", use_container_width=True):
            st.session_state["active_tab"] = "Summary"
            for key in filter_keys:
                st.session_state[key] = []
            st.rerun()
        
        col11, col12 = st.columns(2)

        with col11:
            year_selected_tab3 = st.multiselect('Year', year_list, key='year_filter_tab3')
            month_selected_tab3 = st.multiselect('Month', month_list, key='month_filter_tab3')
            day_selected_tab3 = st.multiselect('Day', day_list, key='day_filter_tab3')
        
        with col12:
            weekday_selected_tab3 = st.multiselect('Week day', weekday_list, key='weekday_filter_tab3')
            hour_selected_tab3 = st.multiselect('Hour', hour_list, key='hour_filter_tab3')
            fscale_selected_tab3 = st.multiselect('F-scale', fscale_list, key='fscale_filter_tab3')

    with col2:
        tornados_locations = tornados_filtered.groupby('state').agg(tor_num=('event_id', 'nunique')).reset_index()
        fig_tab3 = draw_map(tornados_locations, 'tor_num')
        st.plotly_chart(fig_tab3, key='map_tab3')

    st.divider()

    st.dataframe(tornados_filtered)

# <>>>--- TAB 4 ---<<<> DYNAMICS

with tab4:

    if st.session_state["active_tab"] != "Dynamics":
        st.session_state["active_tab"] = "Dynamics"

    tornados_dynamics = tornados.copy()
    tornados_dynamics['week_day'] = tornados_dynamics['begin_date_time'].dt.day_name()

    col1, col2 = st.columns(2)

    with col1:
        group_label_map = {"Year": "year", 
                           "Month": "month_name", 
                           "Day of month": "begin_day",
                           "Day of week": "week_day", 
                           "F-scale": "tor_f_scale", 
                           "State": "state"}    
        group_label = st.selectbox("Group by", list(group_label_map.keys()), index=0)
        group_by_col = group_label_map[group_label]

    with col2:
        measurement_label_map = {'Duration in minutes': 'tor_duration_minutes',
                                'Path length in kilometers': 'tor_length',
                                'Width in meters': 'tor_width'}
        measurement_label = st.selectbox("Measurement", list(measurement_label_map.keys()), index=0)
        agg_wrt_col = measurement_label_map[measurement_label]

    tornados_dynamics_grouped = tornados_dynamics.groupby(group_by_col)[agg_wrt_col].mean().reset_index()
    sorting_order = {"year": year_list, 
                     "month_name": month_list, 
                     "begin_day": day_list,
                     "week_day": weekday_list, 
                     "tor_f_scale": fscale_list, 
                     "state": state_list}
    tornados_dynamics_grouped = apply_custom_sort(tornados_dynamics_grouped, group_by_col, sorting_order[group_by_col])
    
    fig_tab41 = px.line(tornados_dynamics_grouped,
                        x=group_by_col,
                        y=agg_wrt_col,
                        markers=True)
    fig_tab41.update_layout(xaxis_title=group_label.capitalize(),
                            yaxis_title=measurement_label.capitalize(),
                            template="plotly_white",
                            title={'text': f"Average {measurement_label.lower()} per {group_label.lower()}",
                                   'x': 0.04,  
                                   'xanchor': 'left'})
    fig_tab41.update_traces(line=dict(width=1, dash='dot', color='#D6D5D5'),
                            marker=dict(color='#8D8D8D', size=8))
    st.plotly_chart(fig_tab41, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    
    with col1:
        centroids_by_decade = tornados.groupby(tornados['year'] // 10 * 10)[['begin_lon', 'begin_lat']].mean().reset_index().rename(columns={'year': 'decade'})
        fig_tab42 = go.Figure()
        fig_tab42.add_trace(go.Scattergeo(
            lon=centroids_by_decade["begin_lon"],
            lat=centroids_by_decade["begin_lat"],
            mode="markers+text",
            marker=dict(size=10,
                        color=centroids_by_decade["decade"],
                        colorscale='RdYlGn_r',
                        colorbar_title=""),
                        name="Decade Centroids"))
        fig_tab42.update_geos(
            center={"lat": 39, "lon": -98},
            projection_scale=7,
            visible=False,
            showland=True,
            landcolor="#BEBDBD",
            showocean=False,
            bgcolor="rgba(0,0,0,0)",
            projection_type="mercator",
            showcountries=True)
        fig_tab42.update_layout(
            title={'text': "Migration of tornados activity centroid by decade", 'x': 0.04,  'xanchor': 'left'},
            margin={"r":0,"t":40,"l":0,"b":0},
            height=450,
            paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_tab42, use_container_width=True)

    with col2:   
        fig_tab43 = go.Figure()
        sample = tornados_dynamics.sample(n=100, random_state=42)
        for _, row in sample.iterrows():
            fig_tab43.add_trace(go.Scattergeo(
                lon=[row["begin_lon"], row["end_lon"]],
                lat=[row["begin_lat"], row["end_lat"]],
                mode="lines",
                line=dict(width=2, color="crimson"),
                showlegend=False,
                opacity=0.6))
            fig_tab43.add_trace(go.Scattergeo(
                lon=[row["end_lon"]],
                lat=[row["end_lat"]],
                mode="markers",
                marker=dict(
                    symbol="triangle-up",
                    size=10,
                    color="#9B202B",
                    angle=np.rad2deg(np.arctan2(
                        row["end_lat"] - row["begin_lat"],
                        row["end_lon"] - row["begin_lon"]))),
                showlegend=False,
                opacity=0.7))
        fig_tab43.update_geos(
            center={"lat": 39, "lon": -98},
            projection_scale=7,
            visible=False,
            showland=True,
            landcolor="#BEBDBD",
            showocean=False,
            bgcolor="rgba(0,0,0,0)",
            projection_type="mercator",
            showcountries=True)
        fig_tab43.update_layout(
            title={'text': "Tornados paths directions", 'x': 0.12,  'xanchor': 'left'},
            margin={"r":0,"t":40,"l":0,"b":0},
            height=450,
            paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_tab43, use_container_width=True)

    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_1_tab4 = st.text_input("Width in meters", key="input_1_tab4")
    
    with col2:
        input_2_tab4 = st.text_input("Trajectory length in kilometers", key="input_2_tab4")
    
    with col3:
        input_3_tab4 = st.selectbox('F-scale value', options=fscale_list, key="input_3_tab4")

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("Clear all fields",  use_container_width=True, key='clear_all_tab4'):
            st.session_state["active_tab"] = "Dynamics"
            st.session_state["clear_inputs_tab4"] = True
            st.rerun()
    
    with col5:
        if st.button("Predict next tornado date", use_container_width=True):
            try:
                width_tab4 = 0 if input_1_tab4 == '' else float(input_1_tab4.replace(',', '.'))
                distance_tab4 = 0 if input_2_tab4 == '' else float(input_2_tab4.replace(',', '.'))
                scale_tab4 = int(input_3_tab4[1]) if input_3_tab4 != 'unknown' else 0
                features_tab4 = ['TOR_F_SCALE', 'TOR_LENGTH', 'TOR_WIDTH']
                X_pred_tab4 = pd.DataFrame({'TOR_F_SCALE': scale_tab4,
                                            'TOR_LENGTH': distance_tab4,
                                            'TOR_WIDTH': width_tab4}, 
                                            columns=features_tab4, 
                                            index=[0])
                days_left_model = joblib.load("tornado_evolution_model.pkl")
                days_left_prediction = round(days_left_model.predict(X_pred_tab4)[0])
                today = dt.datetime.today().date()
                next_tornado_date = str(today + dt.timedelta(days=days_left_prediction))
                st.session_state["prediction_tab4"] = next_tornado_date
                
                with col6:
                    st.markdown(f"""
                    <div style='
                        font-family: "Source Sans Pro", sans-serif;
                        font-weight: 600;
                        font-size: 32px;
                        color: #262730;
                        text-align: left;
                        margin-top: -0.4rem;'>{st.session_state.get("prediction_tab4", "")}
                    </div>""", unsafe_allow_html=True)
                    # st.metric("", next_tornado_date)
            except Exception as e:
                st.error(f'Prediction failed: {e}')
    
# <>>>--- TAB 5 ---<<<> DAMAGES

with tab5:

    if st.session_state["active_tab"] != "Damages":
        st.session_state["active_tab"] = "Damages"
    
    tornados_damage_filtered = tornados.copy()
    tornados_damage_filtered['damages'] = tornados_damage_filtered['damage_property'] + tornados_damage_filtered['damage_crops']

    tornados_damage_filtered = tornados_damage_filtered[tornados_damage_filtered['year'].isin(year_selected_tab5)] if year_selected_tab5 else tornados_damage_filtered
    tornados_damage_filtered = tornados_damage_filtered[tornados_damage_filtered['month_name'].isin(month_selected_tab5)] if month_selected_tab5 else tornados_damage_filtered
    tornados_damage_filtered = tornados_damage_filtered[tornados_damage_filtered['begin_day'].isin(day_selected_tab5)] if day_selected_tab5 else tornados_damage_filtered
    tornados_damage_filtered = tornados_damage_filtered[tornados_damage_filtered['begin_date_time'].dt.day_name().isin(weekday_selected_tab5)] if weekday_selected_tab5 else tornados_damage_filtered
    tornados_damage_filtered = tornados_damage_filtered[tornados_damage_filtered["begin_time"].astype(str).str.zfill(4).str[:2].isin(str(h) for h in hour_selected_tab5)] if hour_selected_tab5 else tornados_damage_filtered
    tornados_damage_filtered = tornados_damage_filtered[tornados_damage_filtered['tor_f_scale'].isin(fscale_selected_tab5)] if fscale_selected_tab5 else tornados_damage_filtered
    
    cols = st.columns([0.14, 0.14, 0.14, 0.14, 0.14, 0.3])

    with cols[0]:
        total_damage = tornados_damage_filtered[damage_column].sum() / 1_000_000
        st.metric("Total",
                  round(total_damage) if (damage_column == 'damages' and pd.notna(total_damage)) else '-',
                  help="Total damage, millions of dollars")
    
    with cols[1]:
        property_damage = tornados_damage_filtered['damage_property'].sum() / 1_000_000
        st.metric("Property",
                  round(property_damage) if (damage_column != 'damage_crops' and pd.notna(property_damage)) else '-',
                  help="Property damage, millions of dollars")
    
    with cols[2]:
        crops_damage = tornados_damage_filtered['damage_crops'].sum() / 1_000_000
        st.metric("Crops",
                  round(crops_damage) if (damage_column != 'damage_property'and pd.notna(crops_damage)) else '-',
                  help="Crops damage, millions of dollars")
    
    with cols[3]:
        average_damage = tornados_damage_filtered[damage_column].mean() / 1_000_000
        st.metric("Average",
                  round(average_damage) if pd.notna(average_damage) else '-',
                  help="Average damage, millions of dollars")
    
    with cols[4]:
        max_damage = tornados_damage_filtered[damage_column].max() / 1_000_000
        st.metric("Maximum",
                  round(max_damage) if pd.notna(max_damage) else '-',
                  help="The largest damage, millions of dollars")
    
    with cols[5]:
        fatality_mode = tornados_damage_filtered['fatality_location'].dropna().mode()
        most_fatality = fatality_mode[0] if (tornados_damage_filtered[damage_column].sum() > 0 and not fatality_mode.empty) else '-'
        st.metric("Usual place",
                  most_fatality,
                  help="Place of the most often damage")
    
    st.divider()
           
    col1, col2 = st.columns(2)

    with col1:
        col11, col12, col13 = st.columns(3)

        with col11:
            filter_keys = ['year_filter_tab5', 'month_filter_tab5', 'day_filter_tab5', 
                           'weekday_filter_tab5', 'hour_filter_tab5', 'fscale_filter_tab5']
            if st.button("Clear all filters", key="clear_filters_tab5", use_container_width=True):
                st.session_state["active_tab"] = "Damages"
                for key in filter_keys:
                    st.session_state[key] = []
                    st.session_state["damage_type"] = 'damages'
                st.rerun()
        
        with col12:
            if st.button("Property", use_container_width=True):
                st.session_state["active_tab"] = "Damages"
                st.session_state["damage_type"] = 'damage_property'
                st.rerun()
        
        with col13:
            if st.button("Crop", use_container_width=True):
                st.session_state["active_tab"] = "Damages"
                st.session_state["damage_type"] = 'damage_crops'
                st.rerun()

        col21, col22 = st.columns(2)

        with col21:
            year_selected_tab5 = st.multiselect('Year', year_list, key='year_filter_tab5')
            month_selected_tab5 = st.multiselect('Month', month_list, key='month_filter_tab5')
            day_selected_tab5 = st.multiselect('Day', day_list, key='day_filter_tab5')
        
        with col22:
            weekday_selected_tab5 = st.multiselect('Week day', weekday_list, key='weekday_filter_tab5')
            hour_selected_tab5 = st.multiselect('Hour', hour_list, key='hour_filter_tab5')
            fscale_selected_tab5 = st.multiselect('F-scale', fscale_list, key='fscale_filter_tab5')

    with col2:
        tornados_damages = tornados_damage_filtered.groupby('state').agg(damages_sum=(damage_column, 'sum')).reset_index()
        fig_tab5 = draw_map(tornados_damages, 'damages_sum')
        st.plotly_chart(fig_tab5, key='map_tab5')

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        input_1_tab5 = st.text_input("Width in meters", key="input_1_tab5")
        input_2_tab5 = st.text_input("Trajectory length in kilometers", key="input_2_tab5")
        input_3_tab5 = st.text_input("Duration in minutes", key="input_3_tab5")
        
        if st.button("Clear all fields",  use_container_width=True, key='clear_all_tab5'):
            st.session_state["active_tab"] = "Damages"
            st.session_state["clear_inputs_tab5"] = True
            st.session_state["show_metrics_tab5"] = False 
            st.session_state["input_5_tab5"] = "Alabama"
            st.session_state["input_6_tab5"] = "F0"
            st.rerun()
    
    with col2:
        input_4_tab5 = st.text_input("Year and month as integer YYYYMM", key="input_4_tab5")
        input_5_tab5 = st.selectbox("State", options=state_list, key='input_5_tab5')
        input_6_tab5 = st.selectbox("F-scale value", options=fscale_list, key='input_6_tab5')
        
        if st.button("Predict damage size", use_container_width=True):
            st.session_state["active_tab"] = "Damages"
            try:
                width_tab5 = 0 if input_1_tab5 == '' else float(input_1_tab5.replace(',', '.'))
                length_tab5 = 0 if input_2_tab5 == '' else float(input_2_tab5.replace(',', '.'))
                duration_tab5 = 0 if input_3_tab5 == '' else float(input_3_tab5.replace(',', '.'))
                yearmonth_tab5 = 20260101 if input_4_tab5 == '' else input_4_tab5
                    
                features_property_tab5 = ['tor_duration_minutes', 'state', 'event_yearmonth', 'tor_length', 'tor_width']
                X_pred_property_tab5 = pd.DataFrame({'tor_duration_minutes': duration_tab5,
                                                    'state': input_5_tab5,
                                                    'event_yearmonth': yearmonth_tab5,
                                                    'tor_length': length_tab5,
                                                    'tor_width': width_tab5}, 
                                                    columns=features_property_tab5, 
                                                    index=[0])
                features_crops_tab5 = ['tor_f_scale', 'tor_length', 'tor_width']
                X_pred_crops_tab5 = pd.DataFrame({'tor_f_scale': input_6_tab5,
                                                  'tor_length': length_tab5,
                                                  'tor_width': width_tab5}, 
                                                  columns=features_crops_tab5, 
                                                  index=[0])
                
                property_damage_model = joblib.load("tornado_property_model.pkl")
                property_damage_prediction = property_damage_model.predict(X_pred_property_tab5)

                crops_damage_model = joblib.load("tornado_crops_model.pkl")
                crops_damage_prediction = crops_damage_model.predict(X_pred_crops_tab5)
                
                with col3:
                    st.metric("Property damage",
                              round(property_damage_prediction[0]),
                              help="Size of property damage, in dollars, caused by a tornado with provided specifications")
                    st.metric("Crops damage",
                              round(crops_damage_prediction[0]),
                              help="Size of crops damage, in dollars, caused by a tornado with provided specifications")
            except Exception as e:
                st.error(f'Prediction failed: {e}')

# <>>>--- TAB 6 ---<<<> INJURIES

with tab6:

    if st.session_state["active_tab"] != "Injuries":
        st.session_state["active_tab"] = "Injuries"
    
    tornados_injury_filtered = tornados.copy()
    tornados_injury_filtered['injuries'] = tornados_injury_filtered['injuries_direct'] + tornados_injury_filtered['injuries_indirect']

    tornados_injury_filtered = tornados_injury_filtered[tornados_injury_filtered['year'].isin(year_selected_tab6)] if year_selected_tab6 else tornados_injury_filtered
    tornados_injury_filtered = tornados_injury_filtered[tornados_injury_filtered['month_name'].isin(month_selected_tab6)] if month_selected_tab6 else tornados_injury_filtered
    tornados_injury_filtered = tornados_injury_filtered[tornados_injury_filtered['begin_day'].isin(day_selected_tab6)] if day_selected_tab6 else tornados_injury_filtered
    tornados_injury_filtered = tornados_injury_filtered[tornados_injury_filtered['begin_date_time'].dt.day_name().isin(weekday_selected_tab6)] if weekday_selected_tab6 else tornados_injury_filtered
    tornados_injury_filtered = tornados_injury_filtered[tornados_injury_filtered["begin_time"].astype(str).str.zfill(4).str[:2].isin(str(h) for h in hour_selected_tab6)] if hour_selected_tab6 else tornados_injury_filtered
    tornados_injury_filtered = tornados_injury_filtered[tornados_injury_filtered['tor_f_scale'].isin(fscale_selected_tab6)] if fscale_selected_tab6 else tornados_injury_filtered
    
    cols = st.columns([0.14, 0.14, 0.14, 0.14, 0.14, 0.3])

    with cols[0]:
        total_injuries = tornados_injury_filtered[injury_column].sum()
        st.metric("Total",
                  total_injuries if (injury_column == 'injuries' and pd.notna(total_injuries)) else '-',
                  help="Total amount of injuries")
    
    with cols[1]:
        direct_injuries = tornados_injury_filtered['injuries_direct'].sum()
        st.metric("Direct",
                   direct_injuries if (injury_column != 'injuries_indirect' and pd.notna(direct_injuries)) else '-',
                  help="Total amount of direct injuries")
    
    with cols[2]:
        indirect_injuries = tornados_injury_filtered['injuries_indirect'].sum()
        st.metric("Indirect",
                   indirect_injuries if (injury_column != 'injuries_direct' and pd.notna(indirect_injuries)) else '-',
                  help="Total amount of indirect injuries")
    
    with cols[3]:
        average_injury_age = tornados_injury_filtered['fatality_age'].mean()
        st.metric("Average age",
                  round(average_injury_age) if (tornados_injury_filtered[injury_column].sum() and pd.notna(average_injury_age)) > 0 else '-',
                  help="Average age of injury")
    
    with cols[4]:
        gender_mode = tornados_injury_filtered['fatality_sex'].mode()
        most_gender = gender_mode[0] if (tornados_injury_filtered['injuries'].sum() > 0 and not gender_mode.empty) else '-'
        st.metric("Usual gender",
                  most_gender,
                  help="Most frequent gender of injury")
    
    with cols[5]:
        fatality_mode = tornados_injury_filtered['fatality_location'].dropna().mode()
        most_fatality = fatality_mode[0] if (tornados_injury_filtered[injury_column].sum() > 0 and not fatality_mode.empty) else '-'
        st.metric("Usual place",
                  most_fatality if injury_column != 'injuries_indirect' else '-',
                  help="Place of the most often injury")
    
    st.divider()
           
    col1, col2 = st.columns(2)

    with col1:
        col11, col12, col13 = st.columns(3)

        with col11:
            filter_keys = ['year_filter_tab6', 'month_filter_tab6', 'day_filter_tab6', 
                           'weekday_filter_tab6', 'hour_filter_tab6', 'fscale_filter_tab6']
            
            if st.button("Clear all filters", key="clear_filters_tab6", use_container_width=True):
                st.session_state["active_tab"] = "Injuries"
                for key in filter_keys:
                    st.session_state[key] = []
                    st.session_state["injury_type"] = 'injuries'
                st.rerun()
        
        with col12:
            if st.button("Direct", use_container_width=True, key='direct_tab6'):
                st.session_state["active_tab"] = "Injuries"
                st.session_state["injury_type"] = 'injuries_direct'
                st.rerun()
        
        with col13:
            if st.button("Indirect", use_container_width=True, key='indirect_tab6'):
                st.session_state["active_tab"] = "Injuries"
                st.session_state["injury_type"] = 'injuries_indirect'
                st.rerun()

        col21, col22 = st.columns(2)
        
        with col21:
            year_selected_tab6 = st.multiselect('Year', year_list, key='year_filter_tab6')
            month_selected_tab6 = st.multiselect('Month', month_list, key='month_filter_tab6')
            day_selected_tab6 = st.multiselect('Day', day_list, key='day_filter_tab6')
        
        with col22:
            weekday_selected_tab6 = st.multiselect('Week day', weekday_list, key='weekday_filter_tab6')
            hour_selected_tab6 = st.multiselect('Hour', hour_list, key='hour_filter_tab6')
            fscale_selected_tab6 = st.multiselect('F-scale', fscale_list, key='fscale_filter_tab6')

    with col2:
        tornados_injuries = tornados_injury_filtered.groupby('state').agg(injuries_sum=(injury_column, 'sum')).reset_index()
        fig_tab6 = draw_map(tornados_injuries, 'injuries_sum')
        st.plotly_chart(fig_tab6, key='map_tab6')

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        input_1_tab6 = st.text_input("Width in meters", key="input_1_tab6")
        input_2_tab6 = st.text_input("Trajectory length in kilometers", key="input_2_tab6")
        input_3_tab6 = st.text_input("Duration in minutes", key="input_3_tab6")
        input_4_tab6 = st.text_input("Magnitude", key="input_4_tab6")
        
        if st.button("Clear all fields",  use_container_width=True, key='clear_all_tab6'):
            st.session_state["active_tab"] = "Injuries"
            st.session_state["clear_inputs_tab6"] = True
            st.session_state["show_metrics_tab6"] = False
            st.session_state["input_5_tab6"] = "January"
            st.session_state["input_6_tab6"] = "F0"
            st.session_state["input_7_tab6"] = "Alabama"
            st.rerun()
    
    with col2:
        input_5_tab6 = st.selectbox('Full month name', options=month_list, key="input_5_tab6")
        input_6_tab6 = st.selectbox('F-scale value', options=fscale_list, key="input_6_tab6")
        input_7_tab6 = st.selectbox('State', options=state_list, key="input_7_tab6")
        input_8_tab6 = st.text_input('Narrative', key="input_8_tab6")

        if st.button("Predict injury probability", use_container_width=True):
            try:
                width_tab6 = 0 if input_1_tab6 == '' else np.log1p(float(input_1_tab6.replace(',', '.')))
                distance_tab6 = 0 if input_2_tab6 == '' else np.log1p(float(input_2_tab6.replace(',', '.')))
                duration_tab6 = 0 if input_3_tab6 == '' else np.log1p(float(input_3_tab6.replace(',', '.')))
                magnitude_tab6 = 0 if input_4_tab6 == '' else float(input_4_tab6.replace(',', '.'))
                
                features_tab6 = ['event_narrative', 'log_tor_length', 'log_tor_width', 'log_tor_duration_minutes',
                                 'tor_f_scale', 'state', 'month_name']
                X_pred_tab6 = pd.DataFrame({'event_narrative': input_8_tab6,
                                            'log_tor_length': distance_tab6,
                                            'log_tor_width': width_tab6,
                                             'log_tor_duration_minutes': duration_tab6,
                                             'tor_f_scale': input_6_tab6,
                                             'state': input_7_tab6,
                                             'month_name': input_5_tab6}, 
                                            columns=features_tab6, 
                                            index=[0])
                
                injury_model = joblib.load("tornado_injuries_model_new.pkl")
                injury_probability = round(injury_model.predict_proba(X_pred_tab6)[0, 1], 3)

                with col3:
                    st.metric("Any injury",
                              injury_probability,
                              help="Probability to get injured by a tornado with provided specifications")
            except Exception as e:
                st.error(f'Prediction failed: {e}')

# <>>>--- TAB 7 ---<<<> DEATHS

with tab7:

    if st.session_state["active_tab"] != "Deaths":
        st.session_state["active_tab"] = "Deaths"

    tornados_death_filtered = tornados.copy()
    tornados_death_filtered['deaths'] = tornados_death_filtered['deaths_direct'] + tornados_death_filtered['deaths_indirect']
    
    tornados_death_filtered = tornados_death_filtered[tornados_death_filtered['year'].isin(year_selected_tab7)] if year_selected_tab7 else tornados_death_filtered
    tornados_death_filtered = tornados_death_filtered[tornados_death_filtered['month_name'].isin(month_selected_tab7)] if month_selected_tab7 else tornados_death_filtered
    tornados_death_filtered = tornados_death_filtered[tornados_death_filtered['begin_day'].isin(day_selected_tab7)] if day_selected_tab7 else tornados_death_filtered
    tornados_death_filtered = tornados_death_filtered[tornados_death_filtered['begin_date_time'].dt.day_name().isin(weekday_selected_tab7)] if weekday_selected_tab7 else tornados_death_filtered
    tornados_death_filtered = tornados_death_filtered[tornados_death_filtered["begin_time"].astype(str).str.zfill(4).str[:2].isin(str(h) for h in hour_selected_tab7)] if hour_selected_tab7 else tornados_death_filtered
    tornados_death_filtered = tornados_death_filtered[tornados_death_filtered['tor_f_scale'].isin(fscale_selected_tab7)] if fscale_selected_tab7 else tornados_death_filtered
    
    cols = st.columns([0.14, 0.14, 0.14, 0.14, 0.14, 0.3])

    with cols[0]:
        total_deaths = tornados_death_filtered[death_column].sum()
        st.metric("Total",
                   total_deaths if (death_column == 'deaths'and pd.notna(total_deaths)) else '-',
                  help="Total amount of deaths")
    
    with cols[1]:
        direct_deaths = tornados_death_filtered['deaths_direct'].sum()
        st.metric("Direct",
                   direct_deaths if (death_column != 'deaths_indirect' and pd.notna(direct_deaths)) else '-',
                  help="Total amount of direct deaths")
    with cols[2]:
        indirect_deaths = tornados_death_filtered['deaths_indirect'].sum()
        st.metric("Indirect",
                   indirect_deaths if (death_column != 'deaths_direct' and pd.notna(indirect_deaths)) else '-',
                  help="Total amount of indirect deaths")
    
    with cols[3]:
        average_death_age = tornados_death_filtered['fatality_age'].mean()
        st.metric("Average age",
                  round(average_death_age) if (tornados_death_filtered[death_column].sum() > 0 and pd.notna(average_death_age)) else '-',
                  help="Average age of death")
    
    with cols[4]:
        gender_mode = tornados_death_filtered['fatality_sex'].mode()
        most_gender = gender_mode[0] if (tornados_death_filtered['deaths'].sum() > 0 and not gender_mode.empty) else '-'
        st.metric("Usual gender",
                  most_gender,
                  help="Most frequent gender of death")
    
    with cols[5]:
        fatality_mode = tornados_death_filtered['fatality_location'].dropna().mode()
        most_fatality = fatality_mode[0] if (tornados_death_filtered[death_column].sum() > 0 and not fatality_mode.empty) else '-'
        st.metric("Usual place",
                  most_fatality if death_column != 'deaths_indirect' else '-',
                  help="Place of the most often death")
    
    st.divider()
           
    col1, col2 = st.columns(2)

    with col1:
        col11, col12, col13 = st.columns(3)
        
        with col11:
            filter_keys = ['year_filter_tab7', 'month_filter_tab7', 'day_filter_tab7', 
                           'weekday_filter_tab7', 'hour_filter_tab7', 'fscale_filter_tab7']
            
            if st.button("Clear all filters", key="clear_filters_tab7", use_container_width=True):
                st.session_state["active_tab"] = "Deaths"
                for key in filter_keys:
                    st.session_state[key] = []
                    st.session_state["death_type"] = 'deaths'
                st.rerun()
        
        with col12:
            if st.button("Direct", use_container_width=True, key='direct_tab7'):
                st.session_state["active_tab"] = "Deaths"
                st.session_state["death_type"] = 'deaths_direct'
                st.rerun()
        
        with col13:
            if st.button("Indirect", use_container_width=True, key='indirect_tab7'):
                st.session_state["active_tab"] = "Deaths"
                st.session_state["death_type"] = 'deaths_indirect'
                st.rerun()

        col21, col22 = st.columns(2)

        with col21:
            year_selected_tab7 = st.multiselect('Year', year_list, key='year_filter_tab7')
            month_selected_tab7 = st.multiselect('Month', month_list, key='month_filter_tab7')
            day_selected_tab7 = st.multiselect('Day', day_list, key='day_filter_tab7')
        
        with col22:
            weekday_selected_tab7 = st.multiselect('Week day', weekday_list, key='weekday_filter_tab7')
            hour_selected_tab7 = st.multiselect('Hour', hour_list, key='hour_filter_tab7')
            fscale_selected_tab7 = st.multiselect('F-scale', fscale_list, key='fscale_filter_tab7')

    with col2:
        tornados_deaths = tornados_death_filtered.groupby('state').agg(deaths_sum=(death_column, 'sum')).reset_index()
        fig_tab7 = draw_map(tornados_deaths, 'deaths_sum')
        st.plotly_chart(fig_tab7, key='map_tab7')

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        input_1_tab7 = st.text_input("Width in meters", key="input_1_tab7")
        input_2_tab7 = st.text_input("Trajectory length in kilometers", key="input_2_tab7")
        
        if st.button("Clear all fields",  use_container_width=True, key='clear_all_tab7'):
            st.session_state["active_tab"] = "Deaths"
            st.session_state["clear_inputs_tab7"] = True
            st.session_state["show_metrics_tab7"] = False
            st.session_state["input_4_tab7"] = "January"
            st.rerun()
    
    with col2:
        input_3_tab7 = st.text_input("Duration in minutes", key="input_3_tab7")
        input_4_tab7 = st.selectbox('Full month name', options=month_list, key="input_4_tab7")

        if st.button("Predict death probability", use_container_width=True):
            try:
                width_tab7 = 0 if input_1_tab7 == '' else float(input_1_tab7.replace(',', '.'))
                distance_tab7 = 0 if input_2_tab7 == '' else float(input_2_tab7.replace(',', '.'))
                duration_tab7 = 0 if input_3_tab7 == '' else float(input_3_tab7.replace(',', '.'))
                area_tab7 = distance_tab7 * width_tab7 * 0.001
                    
                features_tab7 = ['tor_area', 'tor_width', 'tor_length', 'path_distance_km', 'tor_duration_minutes', 'month_name']
                X_pred_tab7 = pd.DataFrame({'tor_area': area_tab7,
                                            'tor_width': width_tab7,
                                            'tor_length': distance_tab7,
                                            'path_distance_km': distance_tab7,
                                            'tor_duration_minutes': duration_tab7,
                                            'month_name': input_4_tab7}, 
                                            columns=features_tab7, 
                                            index=[0])

                total_death_model = joblib.load("tornado_all_death.pkl")
                total_death_probability = round(total_death_model.predict_proba(X_pred_tab7)[0, 1], 3)

                indirect_death_model = joblib.load("tornado_indirect_death.pkl")
                indirect_death_probability = round(indirect_death_model.predict_proba(X_pred_tab7)[0, 1], 3)
                
                with col3:
                    st.metric("Any death",
                              total_death_probability,
                              help="Probability to get killed by a tornado with provided specifications")
                    st.metric("Indirect death",
                              indirect_death_probability,
                              help="Probability to get killed by a tornado indirectly with provided specifications")
            except Exception as e:
                st.error(f'Prediction failed: {e}')
