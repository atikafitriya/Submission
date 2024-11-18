import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style = 'dark')

st.set_page_config(
    page_title="Brazilian E-Commerce Public",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded")

all_df = pd.read_csv("C:/Users/msi modern 15/OneDrive/Dokumen/DICODING IDCamp/Project Data Analys/Dashboard/all_data.csv")
print(all_df.head())

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column]) 
    
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("C:/Users/msi modern 15/OneDrive/Dokumen/DICODING IDCamp/Project Data Analys/Logo Brazilian E-Commerce.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    ) 

#Helper function shipping_duration
def create_shipping_duration_df(df):
    df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')

    df['shipping_duration'] = (df['shipping_limit_date'] - df['order_purchase_timestamp']).dt.days
    df['year'] = df['order_purchase_timestamp'].dt.year
    df['month'] = df['order_purchase_timestamp'].dt.month
    
    order_purchase_timestamp = df.groupby(['year', 'month'])['order_purchase_timestamp'].count().reset_index()
    order_purchase_timestamp['order_purchase_timestamp'] = pd.to_datetime(order_purchase_timestamp[['year', 'month']].assign(day=1))
    shipping_duration = df.groupby(['year', 'month'])['shipping_duration'].mean().reset_index()
    shipping_duration['period'] = pd.to_datetime(shipping_duration[['year', 'month']].assign(day=1))
    
    return shipping_duration

#Helper function monthly_revenue_df
def create_monthly_revenue_df(df):
    df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], errors='coerce')
    if df['shipping_limit_date'].isnull().any():
        print("Ada nilai yang tidak bisa dikonversi menjadi datetime dalam 'shipping_limit_date'.")

    df['year'] = df['shipping_limit_date'].dt.year
    df['month'] = df['shipping_limit_date'].dt.month

    df['revenue'] = df['price'] + df['freight_value']

    monthly_revenue = df.groupby(['year', 'month'])['revenue'].sum().reset_index()

    monthly_revenue['period'] = monthly_revenue['year'].astype(str) + '-' + monthly_revenue['month'].astype(str).str.zfill(2)

    return monthly_revenue

#Helper function rfm_df
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]
rfm_df = create_rfm_df(main_df)
monthly_revenue_df = create_monthly_revenue_df(main_df)
shipping_duration = create_shipping_duration_df(main_df)

st.header('Brazilian E-Commerce Public Dashboard:sparkles:')

#Shipping Duration
st.subheader("Shipping Duration")

shipping_duration = create_shipping_duration_df(main_df)
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(x="period", y="shipping_duration", data=shipping_duration, palette=['#90CAF9'], ax=ax)

ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=25, rotation=45)
ax.set_ylabel("Shipping Duration (days)", fontsize=30)
ax.set_xlabel("Order Purchase Timestamp", fontsize=30)
ax.set_title("Shipping Duration Over Time", fontsize=35)
ax.grid(True)

st.pyplot(fig)

#Monthly Revenue
st.subheader("Monthly Revenue")

monthly_revenue_df = create_monthly_revenue_df(main_df)
fig, ax = plt.subplots(figsize=(16, 8))
sns.lineplot(x="month", y="revenue", data=monthly_revenue_df, palette=['#90CAF9'], ax=ax)

ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=25, rotation=45)
ax.set_ylabel("Revenue", fontsize=30)
ax.set_xlabel("Month", fontsize=30)
ax.set_title("Monthly Revenue", fontsize=35)
ax.grid(True)

st.pyplot(fig)

#Favorite payment method
st.subheader("Favorite Payment Method")

payment_counts = all_df['payment_type'].value_counts().reset_index()
payment_counts.columns = ['payment_type', 'count']

fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(x='payment_type', y='count', data=payment_counts, color="#90CAF9", ax=ax)

ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=25)
ax.set_ylabel("Count", fontsize=30)
ax.set_xlabel("Payment Type", fontsize=30)
ax.set_title("Favorite Payment Method", fontsize=35)
ax.legend()

st.pyplot(fig)

#The 5 Highest Number of Customers
st.subheader("The 5 Highest Number of Customers")

top_cities = all_df['customer_city'].value_counts().head(5).reset_index()
top_cities.columns = ['customer_city', 'customer_count']
top_states = all_df['customer_state'].value_counts().head(5).reset_index()
top_states.columns = ['customer_state', 'customer_count']

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

sns.barplot(x="customer_count", y="customer_city", data=top_cities, palette=['lightblue'], ax=ax[0])
ax[0].set_ylabel("Cities Customer", fontsize=30)
ax[0].set_xlabel("Number of Customers", fontsize=30)sss
ax[0].set_title("Top 5 Cities by Customer Count", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=25)
ax[0].tick_params(axis='x', labelsize=25)

sns.barplot(x="customer_count", y="customer_state", data=top_states, palette=['lightblue'], ax=ax[1])
ax[1].set_ylabel("States Customer", fontsize=30)
ax[1].set_xlabel("Number of Customers", fontsize=30)
ax[1].set_title("Top 5 States by Customer Count", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=25)
ax[1].tick_params(axis='x', labelsize=25)

st.pyplot(fig)

#Best Customer Based on RFM Parameters
st.subheader("Best Customer Based on RFM Parameters")
 
col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "R$", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=["#72BCD4"], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15, rotation=90)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=["#72BCD4"], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15, rotation=90)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=["#72BCD4"], ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15, rotation=90)

plt.suptitle("Best Customer Based on RFM Parameters", fontsize=20)
plt.show()
 
st.pyplot(fig)
 
st.caption('Copyright (c) Submission Data Analys Dicoding IDCamp 2024')