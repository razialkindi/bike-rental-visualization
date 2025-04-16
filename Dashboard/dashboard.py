import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Bike Sharing Analysis Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Function to load and process data
@st.cache_data
def load_data():
    # Load dataset
    day_df = pd.read_csv('day.csv')
    hour_df = pd.read_csv('hour.csv')
    
    # Convert 'dteday' to datetime
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    # Create mapping for categorical columns
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    year_mapping = {0: '2011', 1: '2012'}
    weekday_mapping = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6: 'Saturday'}
    weather_mapping = {
        1: 'Clear',
        2: 'Mist',
        3: 'Light Snow/Rain',
        4: 'Heavy Rain/Snow'
    }

    # Apply mappings to both dataframes
    for df in [day_df, hour_df]:
        df['season_label'] = df['season'].map(season_mapping)
        df['yr_label'] = df['yr'].map(year_mapping)
        df['weekday_label'] = df['weekday'].map(weekday_mapping)
        df['weathersit_label'] = df['weathersit'].map(weather_mapping)

    # Add month name
    month_mapping = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 
                    7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    for df in [day_df, hour_df]:
        df['mnth_label'] = df['mnth'].map(month_mapping)

    # Convert normalized values to actual values
    for df in [day_df, hour_df]:
        df['temp_actual'] = df['temp'] * 41  # Celsius
        df['atemp_actual'] = df['atemp'] * 50  # Celsius
        df['hum_actual'] = df['hum'] * 100  # %
        df['windspeed_actual'] = df['windspeed'] * 67  # km/h
        
    # Add rush hour classification
    hour_df['rush_hour'] = hour_df['hr'].apply(lambda x: 'Rush Hour' if x in [7, 8, 9, 17, 18, 19] else 'Non-Rush Hour')
    
    # Add day type
    for df in [day_df, hour_df]:
        df['day_type'] = df['workingday'].map({0: 'Weekend/Holiday', 1: 'Working Day'})
    
    return day_df, hour_df

# Load data
day_df, hour_df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# Year filter
year_filter = st.sidebar.multiselect(
    "Select Year",
    options=day_df['yr_label'].unique(),
    default=day_df['yr_label'].unique()
)

# Season filter
season_filter = st.sidebar.multiselect(
    "Select Season",
    options=day_df['season_label'].unique(),
    default=day_df['season_label'].unique()
)

# Weather filter
weather_filter = st.sidebar.multiselect(
    "Select Weather Condition",
    options=day_df['weathersit_label'].unique(),
    default=day_df['weathersit_label'].unique()
)

# Day type filter
day_type_filter = st.sidebar.multiselect(
    "Select Day Type",
    options=day_df['day_type'].unique(),
    default=day_df['day_type'].unique()
)

# Apply filters to dataframes
filtered_day_df = day_df[
    (day_df['yr_label'].isin(year_filter)) &
    (day_df['season_label'].isin(season_filter)) &
    (day_df['weathersit_label'].isin(weather_filter)) &
    (day_df['day_type'].isin(day_type_filter))
]

filtered_hour_df = hour_df[
    (hour_df['yr_label'].isin(year_filter)) &
    (hour_df['season_label'].isin(season_filter)) &
    (hour_df['weathersit_label'].isin(weather_filter)) &
    (hour_df['day_type'].isin(day_type_filter))
]

# Dashboard title
st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown("This dashboard analyzes bike sharing patterns based on various factors including weather, time, and user types.")

# Summary metrics
st.header("Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rentals = filtered_day_df['cnt'].sum()
    st.metric("Total Rentals", f"{total_rentals:,}")

with col2:
    avg_daily_rentals = filtered_day_df['cnt'].mean()
    st.metric("Avg. Daily Rentals", f"{avg_daily_rentals:.0f}")

with col3:
    casual_percentage = (filtered_day_df['casual'].sum() / total_rentals) * 100
    st.metric("Casual Users", f"{casual_percentage:.1f}%")

with col4:
    registered_percentage = (filtered_day_df['registered'].sum() / total_rentals) * 100
    st.metric("Registered Users", f"{registered_percentage:.1f}%")

# Create tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs(["Weather Impact", "Time Patterns", "Temperature & Humidity", "User Types"])

# Tab 1: Weather Impact
with tab1:
    st.header("How Weather Affects Bike Rentals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Average rentals by weather condition
        weather_avg = filtered_day_df.groupby('weathersit_label')['cnt'].mean().reset_index()
        fig_weather = px.bar(
            weather_avg,
            x='weathersit_label',
            y='cnt',
            color='weathersit_label',
            title='Average Daily Rentals by Weather Condition',
            labels={'cnt': 'Average Rentals', 'weathersit_label': 'Weather Condition'}
        )
        fig_weather.update_layout(xaxis_title="Weather Condition", yaxis_title="Average Rentals")
        st.plotly_chart(fig_weather, use_container_width=True)
    
    with col2:
        # Weather impact by season
        weather_season = filtered_day_df.groupby(['season_label', 'weathersit_label'])['cnt'].mean().reset_index()
        fig_weather_season = px.bar(
            weather_season,
            x='weathersit_label',
            y='cnt',
            color='season_label',
            barmode='group',
            title='Weather Impact by Season',
            labels={'cnt': 'Average Rentals', 'weathersit_label': 'Weather Condition', 'season_label': 'Season'}
        )
        fig_weather_season.update_layout(xaxis_title="Weather Condition", yaxis_title="Average Rentals")
        st.plotly_chart(fig_weather_season, use_container_width=True)
    
    # Calculate percentage change compared to clear weather
    if 'Clear' in filtered_day_df['weathersit_label'].unique():
        st.subheader("Percentage Change in Rentals Compared to Clear Weather")
        
        weather_impact = filtered_day_df.groupby('weathersit_label')['cnt'].mean()
        clear_weather_avg = weather_impact.get('Clear', 0)
        
        if clear_weather_avg > 0:
            weather_impact_pct = ((weather_impact - clear_weather_avg) / clear_weather_avg) * 100
            weather_impact_df = pd.DataFrame({
                'Weather': weather_impact_pct.index,
                'Change (%)': weather_impact_pct.values
            })
            
            # Filter out 'Clear' weather
            weather_impact_df = weather_impact_df[weather_impact_df['Weather'] != 'Clear']
            
            fig_impact = px.bar(
                weather_impact_df,
                x='Weather',
                y='Change (%)',
                color='Weather',
                title='Percentage Change in Rentals Compared to Clear Weather',
                text='Change (%)'
            )
            fig_impact.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_impact.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
            st.plotly_chart(fig_impact, use_container_width=True)

# Tab 2: Time Patterns
with tab2:
    st.header("Best Times for Bike Rentals")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly patterns
        hourly_rentals = filtered_hour_df.groupby('hr')['cnt'].mean().reset_index()
        fig_hourly = px.line(
            hourly_rentals,
            x='hr',
            y='cnt',
            title='Average Bike Rentals by Hour of Day',
            labels={'cnt': 'Average Rentals', 'hr': 'Hour of Day'}
        )
        fig_hourly.update_traces(mode='lines+markers')
        fig_hourly.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1), xaxis_title="Hour of Day", yaxis_title="Average Rentals")
        
        # Highlight peak hours
        peak_hours = hourly_rentals.nlargest(3, 'cnt')
        for _, row in peak_hours.iterrows():
            fig_hourly.add_annotation(
                x=row['hr'],
                y=row['cnt'],
                text=f"Peak: {row['cnt']:.1f}",
                showarrow=True,
                arrowhead=1
            )
        
        st.plotly_chart(fig_hourly, use_container_width=True)
    
    with col2:
        # Weekday vs Weekend patterns
        hour_df_filtered = filtered_hour_df.copy()
        hour_df_filtered['is_weekend'] = hour_df_filtered['weekday'].isin([0, 6])  # 0=Sunday, 6=Saturday
        
        weekday_hourly = hour_df_filtered[~hour_df_filtered['is_weekend']].groupby('hr')['cnt'].mean().reset_index()
        weekend_hourly = hour_df_filtered[hour_df_filtered['is_weekend']].groupby('hr')['cnt'].mean().reset_index()
        
        fig_week_pattern = go.Figure()
        fig_week_pattern.add_trace(go.Scatter(
            x=weekday_hourly['hr'],
            y=weekday_hourly['cnt'],
            mode='lines+markers',
            name='Weekday'
        ))
        fig_week_pattern.add_trace(go.Scatter(
            x=weekend_hourly['hr'],
            y=weekend_hourly['cnt'],
            mode='lines+markers',
            name='Weekend'
        ))
        fig_week_pattern.update_layout(
            title='Average Bike Rentals: Weekday vs Weekend',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            xaxis_title="Hour of Day",
            yaxis_title="Average Rentals"
        )
        st.plotly_chart(fig_week_pattern, use_container_width=True)
    
    # Weekly patterns
    weekly_rentals = filtered_day_df.groupby('weekday_label')['cnt'].mean().reset_index()
    
    # Ensure correct order of days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_rentals['weekday_label'] = pd.Categorical(weekly_rentals['weekday_label'], categories=day_order)
    weekly_rentals = weekly_rentals.sort_values('weekday_label')
    
    fig_weekly = px.bar(
        weekly_rentals,
        x='weekday_label',
        y='cnt',
        color='weekday_label',
        title='Average Bike Rentals by Day of Week',
        labels={'cnt': 'Average Rentals', 'weekday_label': 'Day of Week'}
    )
    fig_weekly.update_layout(xaxis_title="Day of Week", yaxis_title="Average Rentals")
    st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Monthly patterns
    monthly_rentals = filtered_day_df.groupby(['yr_label', 'mnth_label'])['cnt'].mean().reset_index()
    
    # Ensure correct order of months
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_rentals['mnth_label'] = pd.Categorical(monthly_rentals['mnth_label'], categories=month_order)
    monthly_rentals = monthly_rentals.sort_values(['yr_label', 'mnth_label'])
    
    fig_monthly = px.line(
        monthly_rentals,
        x='mnth_label',
        y='cnt',
        color='yr_label',
        markers=True,
        title='Average Bike Rentals by Month and Year',
        labels={'cnt': 'Average Rentals', 'mnth_label': 'Month', 'yr_label': 'Year'}
    )
    fig_monthly.update_layout(xaxis_title="Month", yaxis_title="Average Rentals")
    st.plotly_chart(fig_monthly, use_container_width=True)

# Tab 3: Temperature & Humidity
with tab3:
    st.header("Temperature and Humidity Effects")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature impact
        fig_temp = px.scatter(
            filtered_day_df,
            x='temp_actual',
            y='cnt',
            title='Relationship Between Temperature and Bike Rentals',
            trendline='ols',
            labels={'temp_actual': 'Temperature (°C)', 'cnt': 'Number of Rentals'}
        )
        
        # Calculate correlation
        temp_corr = filtered_day_df['temp_actual'].corr(filtered_day_df['cnt'])
        fig_temp.add_annotation(
            x=0.05,
            y=0.95,
            xref="paper",
            yref="paper",
            text=f"Correlation: {temp_corr:.2f}",
            showarrow=False,
            font=dict(size=14),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Humidity impact
        fig_hum = px.scatter(
            filtered_day_df,
            x='hum_actual',
            y='cnt',
            title='Relationship Between Humidity and Bike Rentals',
            trendline='ols',
            labels={'hum_actual': 'Humidity (%)', 'cnt': 'Number of Rentals'}
        )
        
        # Calculate correlation
        hum_corr = filtered_day_df['hum_actual'].corr(filtered_day_df['cnt'])
        fig_hum.add_annotation(
            x=0.05,
            y=0.95,
            xref="paper",
            yref="paper",
            text=f"Correlation: {hum_corr:.2f}",
            showarrow=False,
            font=dict(size=14),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        
        st.plotly_chart(fig_hum, use_container_width=True)
    
    # Temperature and humidity heatmap
    st.subheader("Combined Effect of Temperature and Humidity")
    
    # Create bins for temperature and humidity
    temp_bins = pd.cut(filtered_day_df['temp_actual'], bins=10)
    hum_bins = pd.cut(filtered_day_df['hum_actual'], bins=10)
    
    # Group by temperature and humidity bins
    heatmap_data = filtered_day_df.groupby([temp_bins, hum_bins])['cnt'].mean().reset_index()
    
    # Pivot data for heatmap
    heatmap_pivot = heatmap_data.pivot(index='temp_actual', columns='hum_actual', values='cnt')
    
    # Create heatmap
    fig_heatmap = px.imshow(
        heatmap_pivot,
        labels=dict(x="Humidity Range (%)", y="Temperature Range (°C)", color="Average Rentals"),
        x=[str(col) for col in heatmap_pivot.columns],
        y=[str(idx) for idx in heatmap_pivot.index],
        title="Average Bike Rentals by Temperature and Humidity",
        color_continuous_scale='YlOrRd'
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Tab 4: User Types
with tab4:
    st.header("Casual vs. Registered Users Analysis")
    
    # Filter data for selected year
    if '2011' in year_filter:
        data_2011 = filtered_day_df[filtered_day_df['yr'] == 0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # User type by weekday
            weekday_data = data_2011.groupby('weekday_label')[['casual', 'registered']].mean().reset_index()
            
            # Melt data for grouped bar chart
            weekday_data_melted = weekday_data.melt(
                id_vars='weekday_label',
                value_vars=['casual', 'registered'],
                var_name='User Type',
                value_name='Average Rentals'
            )
            
            # Ensure correct order of days
            weekday_data_melted['weekday_label'] = pd.Categorical(
                weekday_data_melted['weekday_label'],
                categories=day_order
            )
            weekday_data_melted = weekday_data_melted.sort_values('weekday_label')
            
            # Create grouped bar chart
            fig_user_weekday = px.bar(
                weekday_data_melted,
                x='weekday_label',
                y='Average Rentals',
                color='User Type',
                barmode='group',
                title='Average Bike Rentals by User Type and Weekday (2011)',
                labels={'weekday_label': 'Day of Week'}
            )
            fig_user_weekday.update_layout(xaxis_title="Day of Week", yaxis_title="Average Rentals")
            
            st.plotly_chart(fig_user_weekday, use_container_width=True)
        
        with col2:
            # Percentage distribution by weekday
            weekday_totals = data_2011.groupby('weekday_label')[['casual', 'registered', 'cnt']].sum().reset_index()
            weekday_totals['casual_pct'] = (weekday_totals['casual'] / weekday_totals['cnt']) * 100
            weekday_totals['registered_pct'] = (weekday_totals['registered'] / weekday_totals['cnt']) * 100
            
            # Ensure correct order of days
            weekday_totals['weekday_label'] = pd.Categorical(
                weekday_totals['weekday_label'],
                categories=day_order
            )
            weekday_totals = weekday_totals.sort_values('weekday_label')
            
            # Create stacked bar chart
            fig_user_pct = go.Figure()
            fig_user_pct.add_trace(go.Bar(
                x=weekday_totals['weekday_label'],
                y=weekday_totals['casual_pct'],
                name='Casual Users',
                marker_color='#1f77b4'
            ))
            fig_user_pct.add_trace(go.Bar(
                x=weekday_totals['weekday_label'],
                y=weekday_totals['registered_pct'],
                name='Registered Users',
                marker_color='#ff7f0e'
            ))
            
            fig_user_pct.update_layout(
                title='Percentage Distribution of User Types by Weekday (2011)',
                xaxis_title='Day of Week',
                yaxis_title='Percentage (%)',
                barmode='stack'
            )
            
            st.plotly_chart(fig_user_pct, use_container_width=True)
    
    # Monthly trend of user types
    monthly_users = filtered_day_df.groupby(['yr_label', 'mnth_label'])[['casual', 'registered']].mean().reset_index()
    
    # Ensure correct order of months
    monthly_users['mnth_label'] = pd.Categorical(monthly_users['mnth_label'], categories=month_order)
    monthly_users = monthly_users.sort_values(['yr_label', 'mnth_label'])
    
    # Melt data for line chart
    monthly_users_melted = pd.melt(
        monthly_users,
        id_vars=['yr_label', 'mnth_label'],
        value_vars=['casual', 'registered'],
        var_name='User Type',
        value_name='Average Rentals'
    )
    
    # Create line chart
    fig_monthly_users = px.line(
        monthly_users_melted,
        x='mnth_label',
        y='Average Rentals',
        color='User Type',
        facet_col='yr_label',
        markers=True,
        title='Monthly Trend of Casual vs. Registered Users',
        labels={'mnth_label': 'Month', 'yr_label': 'Year'}
    )
    fig_monthly_users.update_layout(xaxis_title="Month", yaxis_title="Average Rentals")
    
    st.plotly_chart(fig_monthly_users, use_container_width=True)
    
    # Hourly pattern by user type
    hourly_users = filtered_hour_df.groupby('hr')[['casual', 'registered']].mean().reset_index()
    
    # Melt data for line chart
    hourly_users_melted = pd.melt(
        hourly_users,
        id_vars=['hr'],
        value_vars=['casual', 'registered'],
        var_name='User Type',
        value_name='Average Rentals'
    )
    
    # Create line chart
    fig_hourly_users = px.line(
        hourly_users_melted,
        x='hr',
        y='Average Rentals',
        color='User Type',
        markers=True,
        title='Hourly Pattern of Casual vs. Registered Users',
        labels={'hr': 'Hour of Day'}
    )
    fig_hourly_users.update_layout(
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),
        xaxis_title="Hour of Day",
        yaxis_title="Average Rentals"
    )
    
    st.plotly_chart(fig_hourly_users, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Bike Sharing Dataset Analysis Dashboard | Created with Streamlit")
