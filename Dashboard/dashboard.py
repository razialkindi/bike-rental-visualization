import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from PIL import Image

# Set page config
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    # Ganti path file sesuai dengan lokasi data Anda
    orders_df = pd.read_csv('orders_dataset.csv')
    customers_df = pd.read_csv('customers_dataset.csv')
    order_items_df = pd.read_csv('order_items_dataset.csv')
    products_df = pd.read_csv('products_dataset.csv')
    sellers_df = pd.read_csv('sellers_dataset.csv')
    
    # Konversi kolom tanggal
    orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
    orders_df['order_approved_at'] = pd.to_datetime(orders_df['order_approved_at'])
    orders_df['order_delivered_carrier_date'] = pd.to_datetime(orders_df['order_delivered_carrier_date'])
    orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
    orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'])
    
    # Ekstrak tahun dan bulan
    orders_df['year'] = orders_df['order_purchase_timestamp'].dt.year
    orders_df['month'] = orders_df['order_purchase_timestamp'].dt.month
    orders_df['month_year'] = orders_df['order_purchase_timestamp'].dt.strftime('%Y-%m')
    
    return orders_df, customers_df, order_items_df, products_df, sellers_df

orders_df, customers_df, order_items_df, products_df, sellers_df = load_data()

# Merge data untuk analisis
order_detail = pd.merge(
    orders_df, 
    order_items_df, 
    on='order_id'
)

# Sidebar
st.sidebar.title("E-Commerce Analysis")
st.sidebar.image("https://img.freepik.com/free-vector/ecommerce-web-page-concept-illustration_114360-8204.jpg", width=200)

# Sidebar menu
menu = st.sidebar.radio(
    "Menu:",
    ["Overview", "Sales Analysis", "Customer Analysis", "Geographic Analysis", "Product Analysis"]
)

# Overview
if menu == "Overview":
    st.title("📊 E-Commerce Dashboard")
    st.write("Dashboard ini menampilkan analisis data e-commerce dari dataset Brazilian E-Commerce.")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Orders", f"{len(orders_df):,}")
    
    with col2:
        total_revenue = order_items_df['price'].sum()
        st.metric("Total Revenue", f"R$ {total_revenue:,.2f}")
    
    with col3:
        avg_order_value = total_revenue / len(orders_df)
        st.metric("Avg Order Value", f"R$ {avg_order_value:,.2f}")
    
    with col4:
        st.metric("Total Customers", f"{len(customers_df):,}")
    
    # Orders per month
    st.subheader("Orders by Month")
    
    # Group data by month_year and count orders
    monthly_orders = orders_df.groupby('month_year').size().reset_index(name='order_count')
    monthly_orders['month_year'] = pd.to_datetime(monthly_orders['month_year'])
    monthly_orders = monthly_orders.sort_values('month_year')
    
    # Plot
    fig = px.line(
        monthly_orders, 
        x='month_year', 
        y='order_count',
        title='Number of Orders Over Time',
        labels={'month_year': 'Month', 'order_count': 'Number of Orders'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Order status distribution
    st.subheader("Order Status Distribution")
    
    status_count = orders_df['order_status'].value_counts().reset_index()
    status_count.columns = ['status', 'count']
    
    fig = px.pie(
        status_count, 
        values='count', 
        names='status',
        title='Order Status Distribution',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

# Sales Analysis
elif menu == "Sales Analysis":
    st.title("💰 Sales Analysis")
    
    # Sales trend over time
    st.subheader("Sales Trend Over Time")
    
    # Merge orders with order items to get sales data
    sales_data = pd.merge(orders_df, order_items_df, on='order_id')
    
    # Group by month_year and sum the price
    monthly_sales = sales_data.groupby('month_year')['price'].sum().reset_index()
    monthly_sales['month_year'] = pd.to_datetime(monthly_sales['month_year'])
    monthly_sales = monthly_sales.sort_values('month_year')
    
    # Plot
    fig = px.line(
        monthly_sales, 
        x='month_year', 
        y='price',
        title='Sales Over Time',
        labels={'month_year': 'Month', 'price': 'Sales (R$)'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sales by payment type
    st.subheader("Sales by Payment Type")
    
    # Get payment info
    payment_data = pd.merge(
        orders_df[['order_id', 'order_purchase_timestamp']], 
        order_items_df[['order_id', 'price']], 
        on='order_id'
    )
    
    # Group by payment type and sum the price
    payment_sales = payment_data.groupby('payment_type')['price'].sum().reset_index()
    
    # Plot
    fig = px.bar(
        payment_sales, 
        x='payment_type', 
        y='price',
        title='Sales by Payment Type',
        labels={'payment_type': 'Payment Type', 'price': 'Sales (R$)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Customer Analysis
elif menu == "Customer Analysis":
    st.title("👥 Customer Analysis")
    
    # Customer distribution by state
    st.subheader("Customer Distribution by State")
    
    state_counts = customers_df['customer_state'].value_counts().reset_index()
    state_counts.columns = ['state', 'count']
    
    # Plot
    fig = px.bar(
        state_counts.head(10), 
        x='state', 
        y='count',
        title='Top 10 States by Customer Count',
        labels={'state': 'State', 'count': 'Number of Customers'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Customer repeat purchase analysis
    st.subheader("Customer Repeat Purchase Analysis")
    
    # Count orders per customer
    customer_orders = orders_df.groupby('customer_id').size().reset_index(name='order_count')
    
    # Count customers with different numbers of orders
    purchase_counts = customer_orders['order_count'].value_counts().sort_index().reset_index()
    purchase_counts.columns = ['number_of_orders', 'number_of_customers']
    
    # Plot
    fig = px.bar(
        purchase_counts, 
        x='number_of_orders', 
        y='number_of_customers',
        title='Number of Customers by Order Count',
        labels={'number_of_orders': 'Number of Orders', 'number_of_customers': 'Number of Customers'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Geographic Analysis
elif menu == "Geographic Analysis":
    st.title("🗺 Geographic Analysis")
    
    # Sales by state
    st.subheader("Sales by State")
    
    # Merge data to get sales by state
    geo_sales = pd.merge(
        orders_df, 
        order_items_df, 
        on='order_id'
    )
    geo_sales = pd.merge(
        geo_sales, 
        customers_df[['customer_id', 'customer_state']], 
        on='customer_id'
    )
    
    # Group by state and sum the price
    state_sales = geo_sales.groupby('customer_state')['price'].sum().reset_index()
    
    # Plot
    fig = px.choropleth(
        state_sales,
        locations='customer_state', 
        locationmode='ISO-3166-2:BR',
        color='price',
        scope='south america',
        title='Sales by State',
        labels={'price': 'Sales (R$)', 'customer_state': 'State'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Delivery time by state
    st.subheader("Average Delivery Time by State")
    
    # Calculate delivery time
    delivery_df = orders_df.copy()
    delivery_df['delivery_time'] = (delivery_df['order_delivered_customer_date'] - 
                                   delivery_df['order_purchase_timestamp']).dt.days
    
    # Merge with customer data
    delivery_by_state = pd.merge(
        delivery_df[['customer_id', 'delivery_time']], 
        customers_df[['customer_id', 'customer_state']], 
        on='customer_id'
    )
    
    # Calculate average delivery time by state
    avg_delivery_time = delivery_by_state.groupby('customer_state')['delivery_time'].mean().reset_index()
    
    # Plot
    fig = px.bar(
        avg_delivery_time.sort_values('delivery_time', ascending=False), 
        x='customer_state', 
        y='delivery_time',
        title='Average Delivery Time by State (Days)',
        labels={'customer_state': 'State', 'delivery_time': 'Avg. Delivery Time (Days)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Product Analysis
elif menu == "Product Analysis":
    st.title("📦 Product Analysis")
    
    # Top product categories
    st.subheader("Top Product Categories")
    
    # Merge data to get product categories
    product_data = pd.merge(
        order_items_df, 
        products_df, 
        on='product_id'
    )
    
    # Group by category and count
    category_counts = product_data['product_category_name'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    
    # Plot
    fig = px.bar(
        category_counts.head(10), 
        x='count', 
        y='category',
        title='Top 10 Product Categories',
        labels={'count': 'Number of Orders', 'category': 'Category'},
        orientation='h'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Price distribution by category
    st.subheader("Price Distribution by Category")
    
    # Select top 5 categories for better visualization
    top_categories = category_counts.head(5)['category'].tolist()
    filtered_data = product_data[product_data['product_category_name'].isin(top_categories)]
    
    # Plot
    fig = px.box(
        filtered_data, 
        x='product_category_name', 
        y='price',
        title='Price Distribution for Top 5 Categories',
        labels={'product_category_name': 'Category', 'price': 'Price (R$)'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    """
    *E-Commerce Analysis Dashboard*  
    Data Source: Brazilian E-Commerce Public Dataset by Olist
    """
)
