import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Set page config
st.set_page_config(
    page_title="Bike Usage Analytics Center",
    page_icon="📊",
    layout="wide"
)

# Load data
def load_data():
    data = pd.read_csv('./submission/Dashboard/main_data.csv')
    # Convert date to datetime
    data['dteday'] = pd.to_datetime(data['dteday'])
    return data

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 20px;
    }
    .section-header {
        font-size: 1.8rem;
        color: #333;
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .metric-card {
        background-color: #f7f7f7;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .insight-text {
        background-color: #e8f4f8;
        border-left: 5px solid #1E88E5;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Load data
data = load_data()

# Header
st.markdown("<h1 class='main-header'>Bike Usage Analytics Center</h1>", unsafe_allow_html=True)

# Overview metrics
st.markdown("<h2 class='section-header'>Usage Overview</h2>", unsafe_allow_html=True)

# Create metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Total Rides", f"{data['cnt'].sum():,}")
    st.markdown("</div>", unsafe_allow_html=True)
    
with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Casual Riders", f"{data['casual'].sum():,}")
    st.markdown("</div>", unsafe_allow_html=True)
    
with col3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Registered Riders", f"{data['registered'].sum():,}")
    st.markdown("</div>", unsafe_allow_html=True)
    
with col4:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Average Rides per Hour", f"{data['cnt'].mean():.1f}")
    st.markdown("</div>", unsafe_allow_html=True)

# Date filter
st.sidebar.header("Filters")
min_date = data['dteday'].min().date()
max_date = data['dteday'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter data based on date
filtered_data = data[(data['dteday'].dt.date >= start_date) & (data['dteday'].dt.date <= end_date)]

# Weather filter
weather_options = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain/Snow"}
selected_weather = st.sidebar.multiselect(
    "Weather Condition",
    options=list(weather_options.keys()),
    default=list(weather_options.keys()),
    format_func=lambda x: weather_options[x]
)

# Further filter data based on weather
if selected_weather:
    filtered_data = filtered_data[filtered_data['weathersit'].isin(selected_weather)]

# Time analysis section
st.markdown("<h2 class='section-header'>Time-Based Analysis</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Hourly distribution
    hourly_data = filtered_data.groupby('hr')['cnt'].mean().reset_index()
    fig = px.line(
        hourly_data, 
        x='hr', 
        y='cnt',
        title='Average Hourly Bike Usage',
        labels={'hr': 'Hour of Day', 'cnt': 'Average Number of Bikes'},
        markers=True
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='insight-text'>Peak usage occurs during commuting hours (7-9 AM and 5-7 PM), indicating bikes are primarily used for work commutes.</div>", unsafe_allow_html=True)

with col2:
    # Weekday analysis
    weekday_data = filtered_data.groupby('weekday')['cnt'].mean().reset_index()
    weekday_data['weekday_name'] = weekday_data['weekday'].map({
        0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
        4: 'Thursday', 5: 'Friday', 6: 'Saturday'
    })
    fig = px.bar(
        weekday_data, 
        x='weekday_name', 
        y='cnt',
        title='Average Bike Usage by Day of Week',
        labels={'weekday_name': 'Day of Week', 'cnt': 'Average Number of Bikes'},
        color='cnt'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Environmental factors
st.markdown("<h2 class='section-header'>Environmental Impact Analysis</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Temperature vs usage
    fig = px.scatter(
        filtered_data, 
        x='temp', 
        y='cnt',
        title='Temperature vs. Bike Usage',
        labels={'temp': 'Normalized Temperature', 'cnt': 'Number of Bikes'},
        color='season',
        size='cnt',
        hover_data=['dteday', 'hr'],
        color_discrete_map={1: '#4575b4', 2: '#74add1', 3: '#f46d43', 4: '#d73027'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='insight-text'>Bike usage shows a positive correlation with temperature, with higher temperatures generally resulting in increased ridership.</div>", unsafe_allow_html=True)

with col2:
    # Humidity vs usage
    fig = px.scatter(
        filtered_data, 
        x='hum', 
        y='cnt',
        title='Humidity vs. Bike Usage',
        labels={'hum': 'Normalized Humidity', 'cnt': 'Number of Bikes'},
        color='season',
        size='windspeed',
        hover_data=['dteday', 'hr'],
        color_discrete_map={1: '#4575b4', 2: '#74add1', 3: '#f46d43', 4: '#d73027'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# User segmentation
st.markdown("<h2 class='section-header'>User Segmentation</h2>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Casual vs Registered by hour
    hourly_user_data = filtered_data.groupby('hr')[['casual', 'registered']].mean().reset_index()
    hourly_user_data_melted = pd.melt(
        hourly_user_data, 
        id_vars=['hr'], 
        value_vars=['casual', 'registered'],
        var_name='user_type', 
        value_name='count'
    )
    
    fig = px.line(
        hourly_user_data_melted, 
        x='hr', 
        y='count', 
        color='user_type',
        title='Casual vs. Registered Users by Hour',
        labels={'hr': 'Hour of Day', 'count': 'Average Number of Bikes', 'user_type': 'User Type'},
        markers=True
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Rush hour analysis
    rush_hour_data = filtered_data.groupby('rush_hour')[['casual', 'registered', 'cnt']].mean().reset_index()
    
    fig = px.bar(
        rush_hour_data, 
        x='rush_hour', 
        y=['casual', 'registered'],
        title='User Types During Rush vs. Non-Rush Hours',
        labels={'rush_hour': 'Rush Hour Status', 'value': 'Average Number of Bikes', 'variable': 'User Type'},
        barmode='group'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("<div class='insight-text'>Registered users dominate during rush hours, suggesting commuters rely on bike sharing for daily transportation to work.</div>", unsafe_allow_html=True)

# Weather impact
st.markdown("<h2 class='section-header'>Weather Impact</h2>", unsafe_allow_html=True)

weather_impact = filtered_data.groupby('weathersit')[['casual', 'registered', 'cnt']].mean().reset_index()
weather_impact['weathersit_name'] = weather_impact['weathersit'].map(weather_options)

fig = px.bar(
    weather_impact, 
    x='weathersit_name', 
    y=['casual', 'registered'],
    title='Weather Impact on Different User Types',
    labels={'weathersit_name': 'Weather Condition', 'value': 'Average Number of Bikes', 'variable': 'User Type'},
    barmode='group',
    color_discrete_map={'casual': '#1E88E5', 'registered': '#FFC107'}
)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div class='insight-text'>Both user types show decreased activity during adverse weather conditions, with casual riders showing more sensitivity to weather changes than registered users.</div>", unsafe_allow_html=True)

# Seasonal trends
st.markdown("<h2 class='section-header'>Seasonal Analysis</h2>", unsafe_allow_html=True)

season_map = {1: "Winter", 2: "Spring", 3: "Summer", 4: "Fall"}
seasonal_data = filtered_data.groupby('season')[['casual', 'registered', 'cnt']].mean().reset_index()
seasonal_data['season_name'] = seasonal_data['season'].map(season_map)

fig = px.line(
    seasonal_data, 
    x='season_name', 
    y=['casual', 'registered', 'cnt'],
    title='Seasonal Bike Usage Patterns',
    labels={'season_name': 'Season', 'value': 'Average Number of Bikes', 'variable': 'User Type'},
    markers=True
)
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

# Conclusion
st.markdown("<h2 class='section-header'>Key Insights</h2>", unsafe_allow_html=True)
st.markdown("""
<div class='insight-text'>
<ul>
    <li>Bike usage peaks during commuting hours (7-9 AM and 5-7 PM)</li>
    <li>Registered users form the majority of riders, especially during weekdays</li>
    <li>Weather significantly impacts ridership, with clear weather showing highest usage</li>
    <li>Temperature has a strong positive correlation with bike usage</li>
    <li>Seasonal trends show highest usage during summer months</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("Bike Usage Analytics Center | Data Analysis Project | 2023")
