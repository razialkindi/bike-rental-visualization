import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Bike Sharing Analysis Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Function to load data
@st.cache_data
def load_data():
    day_df = pd.read_csv('Data/day.csv')
    hour_df = pd.read_csv('Data/hour.csv')
    
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
    
    return day_df, hour_df

# Load data
day_df, hour_df = load_data()

# Dashboard title
st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown("Dashboard ini menampilkan analisis data penyewaan sepeda dari dataset Bike Sharing.")

# Sidebar
st.sidebar.title("Filter Data")

# Year filter
year_options = sorted(day_df['yr_label'].unique())
selected_year = st.sidebar.multiselect('Pilih Tahun:', year_options, default=year_options)

# Season filter
season_options = sorted(day_df['season_label'].unique())
selected_season = st.sidebar.multiselect('Pilih Musim:', season_options, default=season_options)

# Weather filter
weather_options = sorted(day_df['weathersit_label'].unique())
selected_weather = st.sidebar.multiselect('Pilih Kondisi Cuaca:', weather_options, default=weather_options)

# Filter data based on selections
filtered_day_df = day_df[
    day_df['yr_label'].isin(selected_year) &
    day_df['season_label'].isin(selected_season) &
    day_df['weathersit_label'].isin(selected_weather)
]

filtered_hour_df = hour_df[
    hour_df['yr_label'].isin(selected_year) &
    hour_df['season_label'].isin(selected_season) &
    hour_df['weathersit_label'].isin(selected_weather)
]

# Check if data is empty after filtering
if filtered_day_df.empty or filtered_hour_df.empty:
    st.warning("Tidak ada data yang tersedia dengan filter yang dipilih. Silakan ubah filter.")
    st.stop()

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Pengaruh Cuaca", "Pola Waktu", "Pengaruh Suhu & Kelembapan", "Pengguna Casual vs Registered"])

# Tab 1: Pengaruh Cuaca
with tab1:
    st.header("Pengaruh Cuaca Terhadap Jumlah Penyewaan Sepeda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Weather impact on rentals
        weather_avg = filtered_day_df.groupby('weathersit_label')['cnt'].mean().reset_index()
        
        fig = px.bar(
            weather_avg, 
            x='weathersit_label', 
            y='cnt',
            color='weathersit_label',
            labels={'cnt': 'Rata-rata Penyewaan', 'weathersit_label': 'Kondisi Cuaca'},
            title='Rata-rata Penyewaan Sepeda Berdasarkan Kondisi Cuaca'
        )
        fig.update_layout(xaxis_title='Kondisi Cuaca', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate percentage drop
        if 'Clear' in weather_avg['weathersit_label'].values:
            clear_weather_avg = weather_avg[weather_avg['weathersit_label'] == 'Clear']['cnt'].values[0]
            weather_avg['percentage_change'] = ((weather_avg['cnt'] - clear_weather_avg) / clear_weather_avg) * 100
            
            st.subheader("Perubahan Persentase Dibandingkan dengan Cuaca Cerah:")
            for idx, row in weather_avg.iterrows():
                if row['weathersit_label'] != 'Clear':
                    st.write(f"{row['weathersit_label']}: {row['percentage_change']:.2f}%")
    
    with col2:
        # Weather impact by season
        weather_season_avg = filtered_day_df.groupby(['weathersit_label', 'season_label'])['cnt'].mean().reset_index()
        
        fig = px.bar(
            weather_season_avg, 
            x='weathersit_label', 
            y='cnt',
            color='season_label',
            barmode='group',
            labels={'cnt': 'Rata-rata Penyewaan', 'weathersit_label': 'Kondisi Cuaca', 'season_label': 'Musim'},
            title='Rata-rata Penyewaan Sepeda Berdasarkan Cuaca dan Musim'
        )
        fig.update_layout(xaxis_title='Kondisi Cuaca', yaxis_title='Rata-rata Penyewaan')
        st.plotly_chart(fig, use_container_width=True)

# Tab 2: Pola Waktu
with tab2:
    st.header("Pola Waktu Penyewaan Sepeda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hourly pattern
        hourly_rentals = filtered_hour_df.groupby('hr')['cnt'].mean().reset_index()
        
        fig = px.line(
            hourly_rentals, 
            x='hr', 
            y='cnt',
            markers=True,
            labels={'cnt': 'Rata-rata Penyewaan', 'hr': 'Jam'},
            title='Rata-rata Penyewaan Sepeda Berdasarkan Jam'
        )
        fig.update_layout(
            xaxis=dict(tickmode='linear', tick0=0, dtick=1),
            xaxis_title='Jam',
            yaxis_title='Rata-rata Penyewaan'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Weekday vs weekend hourly pattern
        filtered_hour_df['is_weekend'] = filtered_hour_df['weekday'].isin([0, 6])  # 0=Sunday, 6=Saturday
        weekday_hourly = filtered_hour_df[~filtered_hour_df['is_weekend']].groupby('hr')['cnt'].mean().reset_index()
        weekend_hourly = filtered_hour_df[filtered_hour_df['is_weekend']].groupby('hr')['cnt'].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=weekday_hourly['hr'],
            y=weekday_hourly['cnt'],
            mode='lines+markers',
            name='Hari Kerja'
        ))
        fig.add_trace(go.Scatter(
            x=weekend_hourly['hr'],
            y=weekend_hourly['cnt'],
            mode='lines+markers',
            name='Akhir Pekan'
        ))
        fig.update_layout(
            title='Rata-rata Penyewaan: Hari Kerja vs Akhir Pekan',
            xaxis=dict(tickmode='linear', tick0=0, dtick=1, title='Jam'),
            yaxis_title='Rata-rata Penyewaan'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Monthly trends
    st.subheader("Tren Bulanan Penyewaan Sepeda")
    monthly_data = filtered_day_df.groupby(['yr_label', 'mnth_label'])['cnt'].mean().reset_index()
    
    # Ensure months are in correct order
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_data['mnth_label'] = pd.Categorical(monthly_data['mnth_label'], categories=month_order)
    monthly_data = monthly_data.sort_values(['yr_label', 'mnth_label'])
    
    fig = px.line(
        monthly_data, 
        x='mnth_label', 
        y='cnt',
        color='yr_label',
        markers=True,
        labels={'cnt': 'Rata-rata Penyewaan', 'mnth_label': 'Bulan', 'yr_label': 'Tahun'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Bulan dan Tahun'
    )
    fig.update_layout(
        xaxis_title='Bulan',
        yaxis_title='Rata-rata Penyewaan',
        xaxis={'categoryorder': 'array', 'categoryarray': month_order}
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Pengaruh Suhu & Kelembapan
with tab3:
    st.header("Pengaruh Suhu dan Kelembapan Terhadap Penggunaan Sepeda")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Temperature impact
        fig = px.scatter(
            filtered_day_df,
            x='temp_actual',
            y='cnt',
            trendline='ols',
            labels={'temp_actual': 'Suhu (°C)', 'cnt': 'Jumlah Penyewaan'},
            title='Hubungan Antara Suhu dan Jumlah Penyewaan'
        )
        fig.update_layout(xaxis_title='Suhu (°C)', yaxis_title='Jumlah Penyewaan')
        
        # Calculate correlation
        temp_corr = filtered_day_df['temp_actual'].corr(filtered_day_df['cnt'])
        fig.add_annotation(
            x=0.05,
            y=0.95,
            xref="paper",
            yref="paper",
            text=f"Korelasi: {temp_corr:.2f}",
            showarrow=False,
            font=dict(size=14),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Humidity impact
        fig = px.scatter(
            filtered_day_df,
            x='hum_actual',
            y='cnt',
            trendline='ols',
            labels={'hum_actual': 'Kelembapan (%)', 'cnt': 'Jumlah Penyewaan'},
            title='Hubungan Antara Kelembapan dan Jumlah Penyewaan'
        )
        fig.update_layout(xaxis_title='Kelembapan (%)', yaxis_title='Jumlah Penyewaan')
        
        # Calculate correlation
        hum_corr = filtered_day_df['hum_actual'].corr(filtered_day_df['cnt'])
        fig.add_annotation(
            x=0.05,
            y=0.95,
            xref="paper",
            yref="paper",
            text=f"Korelasi: {hum_corr:.2f}",
            showarrow=False,
            font=dict(size=14),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap of temperature and humidity combined effect
    st.subheader("Efek Kombinasi Suhu dan Kelembapan Terhadap Penyewaan Sepeda")
    
    # Create bins for temperature and humidity
    temp_bins = pd.cut(filtered_day_df['temp_actual'], bins=10)
    hum_bins = pd.cut(filtered_day_df['hum_actual'], bins=10)
    
    # Calculate average rentals for each bin combination
    heatmap_data = filtered_day_df.groupby([temp_bins, hum_bins])['cnt'].mean().reset_index()
    
    # Create pivot table for heatmap
    pivot_data = heatmap_data.pivot(index='temp_actual', columns='hum_actual', values='cnt')
    
    # Get bin labels
    temp_labels = [f"{round(interval.left, 1)}-{round(interval.right, 1)}" for interval in pivot_data.index]
    hum_labels = [f"{round(interval.left, 1)}-{round(interval.right, 1)}" for interval in pivot_data.columns]
    
    # Create heatmap
    fig = px.imshow(
        pivot_data.values,
        labels=dict(x="Kelembapan (%)", y="Suhu (°C)", color="Rata-rata Penyewaan"),
        x=hum_labels,
        y=temp_labels,
        color_continuous_scale="YlOrRd"
    )
    fig.update_layout(
        title='Rata-rata Penyewaan Sepeda Berdasarkan Suhu dan Kelembapan',
        xaxis_title='Kelembapan (%)',
        yaxis_title='Suhu (°C)'
    )
    st.plotly_chart(fig, use_container_width=True)

# Tab 4: Pengguna Casual vs Registered
with tab4:
    st.header("Perbedaan Pola Penggunaan Antara Pengguna Casual dan Registered")
    
    # Filter data for selected year(s)
    year_data = filtered_day_df.copy()
    
    # Analyze user type distribution by weekday
    weekday_data = year_data.groupby('weekday_label')[['casual', 'registered']].mean().reset_index()
    
    # Melt the data for easier plotting
    weekday_data_melted = weekday_data.melt(
        id_vars='weekday_label',
        value_vars=['casual', 'registered'],
        var_name='User Type',
        value_name='Average Rentals'
    )
    
    # Order weekdays correctly
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_data_melted['weekday_label'] = pd.Categorical(weekday_data_melted['weekday_label'], categories=weekday_order)
    weekday_data_melted = weekday_data_melted.sort_values('weekday_label')
    
    # Map user types to more descriptive names
    weekday_data_melted['User Type'] = weekday_data_melted['User Type'].map({'casual': 'Casual Users', 'registered': 'Registered Users'})
    
    # Create bar chart
    fig = px.bar(
        weekday_data_melted,
        x='weekday_label',
        y='Average Rentals',
        color='User Type',
        barmode='group',
        labels={'weekday_label': 'Hari', 'Average Rentals': 'Rata-rata Penyewaan', 'User Type': 'Tipe Pengguna'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Tipe Pengguna dan Hari'
    )
    fig.update_layout(
        xaxis_title='Hari',
        yaxis_title='Rata-rata Penyewaan',
        xaxis={'categoryorder': 'array', 'categoryarray': weekday_order}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Calculate percentage distribution
    weekday_totals = year_data.groupby('weekday_label')[['casual', 'registered', 'cnt']].sum().reset_index()
    weekday_totals['casual_pct'] = (weekday_totals['casual'] / weekday_totals['cnt']) * 100
    weekday_totals['registered_pct'] = (weekday_totals['registered'] / weekday_totals['cnt']) * 100
    
    # Order weekdays correctly
    weekday_totals['weekday_label'] = pd.Categorical(weekday_totals['weekday_label'], categories=weekday_order)
    weekday_totals = weekday_totals.sort_values('weekday_label')
    
    # Create stacked bar chart for percentages
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekday_totals['weekday_label'],
        y=weekday_totals['casual_pct'],
        name='Casual Users',
        marker_color='#1f77b4'
    ))
    fig.add_trace(go.Bar(
        x=weekday_totals['weekday_label'],
        y=weekday_totals['registered_pct'],
        name='Registered Users',
        marker_color='#ff7f0e'
    ))
    fig.update_layout(
        barmode='stack',
        title='Distribusi Persentase Tipe Pengguna Berdasarkan Hari',
        xaxis_title='Hari',
        yaxis_title='Persentase (%)',
        xaxis={'categoryorder': 'array', 'categoryarray': weekday_order}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly trends by user type
    st.subheader("Tren Bulanan Berdasarkan Tipe Pengguna")
    
    monthly_user_data = year_data.groupby(['mnth_label'])[['casual', 'registered']].mean().reset_index()
    
    # Melt the data for easier plotting
    monthly_user_data_melted = monthly_user_data.melt(
        id_vars='mnth_label',
        value_vars=['casual', 'registered'],
        var_name='User Type',
        value_name='Average Rentals'
    )
    
    # Ensure months are in correct order
    month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_user_data_melted['mnth_label'] = pd.Categorical(monthly_user_data_melted['mnth_label'], categories=month_order)
    monthly_user_data_melted = monthly_user_data_melted.sort_values('mnth_label')
    
    # Map user types to more descriptive names
    monthly_user_data_melted['User Type'] = monthly_user_data_melted['User Type'].map({'casual': 'Casual Users', 'registered': 'Registered Users'})
    
    # Create line chart
    fig = px.line(
        monthly_user_data_melted,
        x='mnth_label',
        y='Average Rentals',
        color='User Type',
        markers=True,
        labels={'mnth_label': 'Bulan', 'Average Rentals': 'Rata-rata Penyewaan', 'User Type': 'Tipe Pengguna'},
        title='Rata-rata Penyewaan Sepeda Berdasarkan Tipe Pengguna dan Bulan'
    )
    fig.update_layout(
        xaxis_title='Bulan',
        yaxis_title='Rata-rata Penyewaan',
        xaxis={'categoryorder': 'array', 'categoryarray': month_order}
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Dashboard dibuat oleh Muhammad Razi Al Kindi Nadra untuk Proyek Analisis Data")
