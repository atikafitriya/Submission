import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set_theme(style = 'dark')

st.set_page_config(
    page_title="Brazilian E-Commerce Public",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded")

all_df = pd.read_csv("C:/Users/msi modern 15/Documents/DICODING IDCamp/Project Data Analys/Dashboard/all_data.csv")
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
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")#jangan lupa ganti gambar logonya
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    ) 

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

st.header('Brazilian E-Commerce Public Dashboard:sparkles:')

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
ax[0].set_xlabel("Number of Customers", fontsize=30)
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