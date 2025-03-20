import pandas as pd
import plotly.express as px
import streamlit as st

# ===================== #
# 🚴 DATA LOADING 🚴
# ===================== #
@st.cache_data
def load_data():
    df = pd.read_csv('dashboard/main_data.csv')
    
    # Mapping kolom
    season_mapping = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
    weather_mapping = {1: 'Cerah/Berawan', 2: 'Berkabut/Berawan', 3: 'Gerimis/Sedang', 4: 'Hujan Deras/Badai'}
    day_mapping = {0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 4: "Kamis", 5: "Jumat", 6: "Sabtu"}

    # Terapkan mapping
    df['season'] = df['season'].map(season_mapping)
    df['weathersit'] = df['weathersit'].map(weather_mapping)
    df['weekday'] = df['weekday'].map(day_mapping)

    # Kolom tambahan
    df['month'] = pd.to_datetime(df['dteday']).dt.month
    df['rush_hour'] = df['hr'].apply(lambda x: 'Sibuk' if 7 <= x <= 19 else 'Sepi')
    df['workingday_label'] = df['workingday'].replace({0: 'Akhir Pekan', 1: 'Hari Kerja'})

    return df

# Load data
main_df = load_data()

# ===================== #
# SIDEBAR
# ===================== #
st.sidebar.title("Filter Data 🚴")
season_filter = st.sidebar.multiselect(
    "Pilih Musim:",
    options=main_df['season'].unique(),
    default=main_df['season'].unique()
)

weather_filter = st.sidebar.multiselect(
    "Pilih Cuaca:",
    options=main_df['weathersit'].unique(),
    default=main_df['weathersit'].unique()
)

day_filter = st.sidebar.multiselect(
    "Pilih Hari:",
    options=main_df['weekday'].unique(),
    default=main_df['weekday'].unique()
)

time_filter = st.sidebar.multiselect(
    "Pilih Jam:",
    options=sorted(main_df['hr'].unique()),
    default=sorted(main_df['hr'].unique())
)

# ===================== #
# FILTER DATA
# ===================== #
filtered_df = main_df[
    (main_df['season'].isin(season_filter)) &
    (main_df['weathersit'].isin(weather_filter)) &
    (main_df['weekday'].isin(day_filter)) &
    (main_df['hr'].isin(time_filter))
]

# ===================== #
# HEADER
# ===================== #
st.title("🚴 Dashboard Bike Sharing 🚴")
st.markdown("**Analisis Data Peminjaman Sepeda** berdasarkan musim, cuaca, hari, dan jam tertentu. Silakan gunakan filter di sidebar untuk eksplorasi lebih lanjut!")

st.markdown("---")

# ===================== #
# DATAFRAME
# ===================== #
with st.expander("📄 Lihat Data Mentah"):
    st.dataframe(filtered_df)

# ===================== #
# VISUALISASI 1: Penggunaan Sepeda per Musim
# ===================== #
st.subheader("1️⃣ Perbandingan Penggunaan Layanan Berdasarkan Musim")

fig_season = px.bar(
    filtered_df.groupby('season')['cnt'].sum().reset_index(),
    x='season',
    y='cnt',
    color='season',
    labels={'cnt': 'Jumlah Penyewaan', 'season': 'Musim'},
    title='Jumlah Penyewaan Sepeda Berdasarkan Musim'
)
st.plotly_chart(fig_season, use_container_width=True)

# ===================== #
# VISUALISASI 2: Penyewaan Sepeda Berdasarkan Tanggal & Musim
# ===================== #
fig_season_date = px.bar(
    filtered_df.groupby(['season', 'dteday'])['cnt'].sum().reset_index(),
    x='dteday',
    y='cnt',
    color='season',
    labels={'cnt': 'Jumlah Penyewaan', 'dteday': 'Tanggal'},
    title='Jumlah Penyewaan Sepeda per Tanggal & Musim'
)
st.plotly_chart(fig_season_date, use_container_width=True)

# ===================== #
# VISUALISASI 3: Penyewaan Sepeda Berdasarkan Jam
# ===================== #
st.subheader("2️⃣ Penyewaan Sepeda Berdasarkan Jam")

fig_hour = px.line(
    filtered_df.groupby('hr')['cnt'].sum().reset_index(),
    x='hr',
    y='cnt',
    labels={'cnt': 'Jumlah Penyewaan', 'hr': 'Jam'},
    title='Jumlah Penyewaan Sepeda Berdasarkan Jam'
)
st.plotly_chart(fig_hour, use_container_width=True)

fig_rush = px.bar(
    filtered_df.groupby('rush_hour')['cnt'].sum().reset_index(),
    x='rush_hour',
    y='cnt',
    color='rush_hour',
    labels={'cnt': 'Jumlah Penyewaan', 'rush_hour': 'Kategori Jam'},
    title='Perbandingan Jam Sibuk dan Sepi'
)
st.plotly_chart(fig_rush, use_container_width=True)

# ===================== #
# VISUALISASI 4: Penyewaan Sepeda Berdasarkan Hari
# ===================== #
st.subheader("3️⃣ Penyewaan Sepeda Berdasarkan Hari")

fig_day = px.box(
    filtered_df,
    x='weekday',
    y='cnt',
    color='weekday',
    labels={'cnt': 'Jumlah Penyewaan', 'weekday': 'Hari'},
    title='Perbandingan Penyewaan Sepeda per Hari'
)
st.plotly_chart(fig_day, use_container_width=True)

fig_working = px.box(
    filtered_df,
    x='workingday_label',
    y='cnt',
    color='workingday_label',
    labels={'cnt': 'Jumlah Penyewaan', 'workingday_label': 'Jenis Hari'},
    title='Perbandingan Hari Kerja vs Akhir Pekan'
)
st.plotly_chart(fig_working, use_container_width=True)

# ===================== #
# VISUALISASI 5: Pengaruh Cuaca terhadap Penyewaan Sepeda
# ===================== #
st.subheader("4️⃣ Pengaruh Cuaca terhadap Penyewaan Sepeda")

fig_weather_pie = px.pie(
    filtered_df.groupby('weathersit')['cnt'].sum().reset_index(),
    names='weathersit',
    values='cnt',
    title='Distribusi Penyewaan Berdasarkan Kondisi Cuaca'
)
st.plotly_chart(fig_weather_pie, use_container_width=True)

fig_weather_month = px.bar(
    filtered_df.groupby(['month', 'weathersit'])['cnt'].sum().reset_index(),
    x='month',
    y='cnt',
    color='weathersit',
    labels={'cnt': 'Jumlah Penyewaan', 'month': 'Bulan', 'weathersit': 'Cuaca'},
    title='Penggunaan Sepeda Berdasarkan Cuaca per Bulan'
)
st.plotly_chart(fig_weather_month, use_container_width=True)

# ===================== #
# FOOTER
# ===================== #
st.markdown("---")
st.caption("🚀 Dibuat oleh Razialkindi - Dicoding 2024 🚴‍♂️")
