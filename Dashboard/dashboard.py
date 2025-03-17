import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# =======================
# CONFIG
# =======================
st.set_page_config(page_title='🚴♂ Bike Sharing Dashboard', layout='wide')

# =======================
# LOAD DATA
# =======================
@st.cache_data
def load_data():
    main_data = pd.read_csv('dashboard/main_data.csv')
    return main_data

main_data = load_data()

# =======================
# SIDEBAR - FILTERS
# =======================
st.sidebar.header("Filter Data")

# Filter Year
year_options = main_data['yr'].map({0: '2011', 1: '2012'}).unique()
selected_year = st.sidebar.multiselect("Pilih Tahun", options=year_options, default=year_options)

# Filter Season
season_options = main_data['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}).unique()
selected_season = st.sidebar.multiselect("Pilih Musim", options=season_options, default=season_options)

# Filter Weather
weather_options = main_data['weathersit'].map({1: 'Cerah', 2: 'Berawan', 3: 'Hujan'}).unique()
selected_weather = st.sidebar.multiselect("Pilih Cuaca", options=weather_options, default=weather_options)

# Filter Workingday
workingday_options = ['Bekerja', 'Libur']
selected_workingday = st.sidebar.multiselect("Hari Kerja/Libur", options=workingday_options, default=workingday_options)

# Mapping filter back to data
main_data['yr_label'] = main_data['yr'].map({0: '2011', 1: '2012'})
main_data['season_label'] = main_data['season'].map({1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'})
main_data['weathersit_label'] = main_data['weathersit'].map({1: 'Cerah', 2: 'Berawan', 3: 'Hujan'})
main_data['workingday_label'] = main_data['workingday'].map({1: 'Bekerja', 0: 'Libur'})

# Apply filters
filtered_data = main_data[
    (main_data['yr_label'].isin(selected_year)) &
    (main_data['season_label'].isin(selected_season)) &
    (main_data['weathersit_label'].isin(selected_weather)) &
    (main_data['workingday_label'].isin(selected_workingday))
]

# =======================
# TITLE
# =======================
st.title('🚴‍♂ Bike Sharing Dashboard')
st.markdown('### Analisis Penyewaan Sepeda per Jam - Capital Bikeshare Data 2011-2012')

st.markdown(f"Jumlah Data: {filtered_data.shape[0]} records")

# =======================
# PERTANYAAN 1: Pengaruh Cuaca terhadap Penyewaan
# =======================
st.header('1. Pengaruh Cuaca terhadap Jumlah Penyewaan Sepeda')

col1, col2 = st.columns(2)

with col1:
    st.subheader('Barplot Jumlah Penyewaan per Kondisi Cuaca')
    fig1, ax1 = plt.subplots()
    sns.barplot(x='weathersit_label', y='cnt', data=filtered_data, palette='Blues', estimator='mean', ax=ax1)
    ax1.set_xlabel('Kondisi Cuaca')
    ax1.set_ylabel('Rata-rata Penyewaan')
    st.pyplot(fig1)

with col2:
    st.subheader('Boxplot Penyewaan per Kondisi Cuaca')
    fig2, ax2 = plt.subplots()
    sns.boxplot(x='weathersit_label', y='cnt', data=filtered_data, palette='Pastel1', ax=ax2)
    ax2.set_xlabel('Kondisi Cuaca')
    ax2.set_ylabel('Jumlah Penyewaan')
    st.pyplot(fig2)

# =======================
# PERTANYAAN 2: Waktu Terbaik dalam Sehari
# =======================
st.header('2. Waktu Terbaik dalam Sehari untuk Penyewaan Sepeda')

hourly_avg = filtered_data.groupby('hr')['cnt'].mean().reset_index()
pivot_heatmap = filtered_data.pivot_table(values='cnt', index='weekday', columns='hr', aggfunc='mean')

col3, col4 = st.columns(2)

with col3:
    st.subheader('Lineplot Rata-rata Penyewaan Sepeda per Jam')
    fig3, ax3 = plt.subplots()
    sns.lineplot(x='hr', y='cnt', data=hourly_avg, marker='o', ax=ax3)
    ax3.set_xlabel('Jam')
    ax3.set_ylabel('Rata-rata Penyewaan')
    ax3.set_title('Pola Penyewaan Sepeda per Jam')
    ax3.grid(True)
    st.pyplot(fig3)

with col4:
    st.subheader('Heatmap Penyewaan Sepeda (Hari vs Jam)')
    fig4, ax4 = plt.subplots(figsize=(12, 5))
    sns.heatmap(pivot_heatmap, cmap='YlGnBu', ax=ax4)
    ax4.set_xlabel('Jam')
    ax4.set_ylabel('Hari (0=Senin)')
    ax4.set_title('Distribusi Penyewaan Sepeda per Hari & Jam')
    st.pyplot(fig4)

# =======================
# PERTANYAAN 3: Pengaruh Kelembapan dan Suhu
# =======================
st.header('3. Pengaruh Kelembapan dan Suhu terhadap Penggunaan Sepeda')

col5, col6 = st.columns(2)

with col5:
    st.subheader('Scatterplot Suhu vs Penyewaan Sepeda')
    fig5, ax5 = plt.subplots()
    sns.scatterplot(x='temp', y='cnt', data=filtered_data, alpha=0.6, ax=ax5)
    sns.regplot(x='temp', y='cnt', data=filtered_data, scatter=False, color='red', ax=ax5)
    ax5.set_xlabel('Suhu (normalized)')
    ax5.set_ylabel('Jumlah Penyewaan')
    ax5.set_title('Pengaruh Suhu terhadap Penyewaan Sepeda')
    st.pyplot(fig5)

with col6:
    st.subheader('Scatterplot Kelembapan vs Penyewaan Sepeda')
    fig6, ax6 = plt.subplots()
    sns.scatterplot(x='hum', y='cnt', data=filtered_data, alpha=0.6, ax=ax6)
    sns.regplot(x='hum', y='cnt', data=filtered_data, scatter=False, color='red', ax=ax6)
    ax6.set_xlabel('Kelembapan (normalized)')
    ax6.set_ylabel('Jumlah Penyewaan')
    ax6.set_title('Pengaruh Kelembapan terhadap Penyewaan Sepeda')
    st.pyplot(fig6)

# =======================
# PERTANYAAN 4: Casual vs Registered
# =======================
st.header('4. Perilaku Peminjaman Casual vs Registered')

col7, col8 = st.columns(2)

with col7:
    st.subheader('Barplot Rata-rata Penyewaan Casual vs Registered')
    avg_user_type = filtered_data[['casual', 'registered']].mean()
    fig7, ax7 = plt.subplots()
    sns.barplot(x=avg_user_type.index, y=avg_user_type.values, palette='muted', ax=ax7)
    ax7.set_ylabel('Rata-rata Penyewaan')
    ax7.set_title('Rata-rata Penyewaan Casual vs Registered')
    st.pyplot(fig7)

with col8:
    st.subheader('Lineplot Tren Casual vs Registered')
    fig8, ax8 = plt.subplots(figsize=(14,6))
    sns.lineplot(x='dteday', y='casual', data=filtered_data, label='Casual', ax=ax8)
    sns.lineplot(x='dteday', y='registered', data=filtered_data, label='Registered', ax=ax8)
    ax8.set_xlabel('Tanggal')
    ax8.set_ylabel('Jumlah Penyewaan')
    ax8.set_title('Tren Penyewaan Casual vs Registered')
    ax8.legend()
    st.pyplot(fig8)

# =======================
# FOOTER
# =======================
st.markdown("---")
st.caption("Dashboard by Muhammad Razi Al Kindi Nadra - DBC Coding Camp 🚀")
