import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Penjualan",
    page_icon="📊",
    layout="wide"
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    # Contoh data dummy, dalam kasus nyata bisa diganti dengan data dari database atau file CSV
    np.random.seed(42)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    
    # Membuat data dummy penjualan
    data = {
        'Tanggal': dates,
        'Penjualan': np.random.randint(100, 1000, size=len(dates)),
        'Kategori': np.random.choice(['Elektronik', 'Pakaian', 'Makanan', 'Perabotan', 'Lainnya'], size=len(dates)),
        'Region': np.random.choice(['Jawa', 'Sumatera', 'Kalimantan', 'Sulawesi', 'Papua'], size=len(dates)),
        'Profit': np.random.randint(10, 200, size=len(dates))
    }
    
    df = pd.DataFrame(data)
    # Tambahkan kolom bulan dan tahun untuk memudahkan filtering
    df['Bulan'] = df['Tanggal'].dt.month_name()
    df['Tahun'] = df['Tanggal'].dt.year
    return df

# Load data
df = load_data()

# Judul Dashboard
st.title("📊 Dashboard Analisis Penjualan")
st.markdown("Dashboard ini menampilkan visualisasi data penjualan untuk analisis performa bisnis.")

# Sidebar untuk filter
st.sidebar.header("Filter Data")

# Filter tahun
tahun_list = df['Tahun'].unique().tolist()
tahun_filter = st.sidebar.multiselect(
    "Pilih Tahun:",
    options=tahun_list,
    default=tahun_list
)

# Filter bulan
bulan_list = df['Bulan'].unique().tolist()
bulan_filter = st.sidebar.multiselect(
    "Pilih Bulan:",
    options=bulan_list,
    default=bulan_list
)

# Filter kategori
kategori_list = df['Kategori'].unique().tolist()
kategori_filter = st.sidebar.multiselect(
    "Pilih Kategori Produk:",
    options=kategori_list,
    default=kategori_list
)

# Filter region
region_list = df['Region'].unique().tolist()
region_filter = st.sidebar.multiselect(
    "Pilih Region:",
    options=region_list,
    default=region_list
)

# Menerapkan filter
filtered_df = df[
    (df['Tahun'].isin(tahun_filter)) &
    (df['Bulan'].isin(bulan_filter)) &
    (df['Kategori'].isin(kategori_filter)) &
    (df['Region'].isin(region_filter))
]

# Tampilkan jumlah data yang difilter
st.sidebar.info(f"Data terfilter: {filtered_df.shape[0]} baris")

# Tampilkan tombol untuk melihat data
if st.sidebar.checkbox("Tampilkan Data Mentah"):
    st.subheader("Data Mentah")
    st.dataframe(filtered_df)

# KPI Metrics
st.subheader("Key Performance Indicators (KPI)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    total_penjualan = filtered_df['Penjualan'].sum()
    st.metric("Total Penjualan", f"{total_penjualan:,}")

with col2:
    rata_penjualan = filtered_df['Penjualan'].mean()
    st.metric("Rata-rata Penjualan Harian", f"{rata_penjualan:.2f}")

with col3:
    total_profit = filtered_df['Profit'].sum()
    st.metric("Total Profit", f"{total_profit:,}")

with col4:
    profit_margin = (total_profit / total_penjualan) * 100 if total_penjualan > 0 else 0
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

# Visualisasi 1: Tren Penjualan Bulanan
st.subheader("Tren Penjualan Bulanan")
monthly_sales = filtered_df.groupby(['Tahun', 'Bulan'])['Penjualan'].sum().reset_index()
# Urutkan bulan
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']
monthly_sales['Bulan'] = pd.Categorical(monthly_sales['Bulan'], categories=month_order, ordered=True)
monthly_sales = monthly_sales.sort_values(['Tahun', 'Bulan'])

# Buat label untuk sumbu x yang menggabungkan bulan dan tahun
monthly_sales['Bulan-Tahun'] = monthly_sales['Bulan'] + ' ' + monthly_sales['Tahun'].astype(str)

fig_monthly = px.line(
    monthly_sales, 
    x='Bulan-Tahun', 
    y='Penjualan',
    markers=True,
    title='Tren Penjualan Bulanan'
)
fig_monthly.update_layout(xaxis_title='Bulan', yaxis_title='Total Penjualan')
st.plotly_chart(fig_monthly, use_container_width=True)

# Visualisasi 2: Penjualan per Kategori
st.subheader("Penjualan per Kategori")
col1, col2 = st.columns(2)

with col1:
    category_sales = filtered_df.groupby('Kategori')['Penjualan'].sum().reset_index()
    fig_category = px.pie(
        category_sales, 
        values='Penjualan', 
        names='Kategori',
        title='Distribusi Penjualan per Kategori',
        hole=0.4
    )
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    category_profit = filtered_df.groupby('Kategori')['Profit'].sum().reset_index()
    fig_profit = px.bar(
        category_profit,
        x='Kategori',
        y='Profit',
        title='Profit per Kategori',
        color='Kategori'
    )
    st.plotly_chart(fig_profit, use_container_width=True)

# Visualisasi 3: Penjualan per Region
st.subheader("Analisis Penjualan per Region")
region_sales = filtered_df.groupby('Region')['Penjualan'].sum().reset_index()
fig_region = px.bar(
    region_sales,
    x='Region',
    y='Penjualan',
    title='Penjualan per Region',
    color='Region'
)
st.plotly_chart(fig_region, use_container_width=True)

# Visualisasi 4: Heatmap Penjualan (Bulan vs Kategori)
st.subheader("Heatmap Penjualan (Bulan vs Kategori)")
heatmap_data = filtered_df.pivot_table(
    index='Bulan', 
    columns='Kategori', 
    values='Penjualan', 
    aggfunc='sum'
)
# Urutkan bulan
heatmap_data = heatmap_data.reindex(month_order)

fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Kategori", y="Bulan", color="Penjualan"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    aspect="auto",
    title="Heatmap Penjualan (Bulan vs Kategori)"
)
st.plotly_chart(fig_heatmap, use_container_width=True)

# Analisis korelasi
st.subheader("Analisis Korelasi")
correlation = filtered_df[['Penjualan', 'Profit']].corr()
fig_corr = px.imshow(
    correlation,
    text_auto=True,
    labels=dict(x="Variabel", y="Variabel", color="Korelasi"),
    x=correlation.columns,
    y=correlation.index,
    color_continuous_scale='RdBu_r',
    aspect="auto",
    title="Korelasi antara Penjualan dan Profit"
)
st.plotly_chart(fig_corr, use_container_width=True)

# Download data
st.subheader("Download Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download data sebagai CSV",
    data=csv,
    file_name='data_penjualan.csv',
    mime='text/csv',
)

# Footer
st.markdown("---")
st.markdown("Dashboard dibuat dengan ❤️ menggunakan Streamlit")
