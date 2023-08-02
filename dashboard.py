import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

all_data = pd.read_csv("all_data.csv")


def create_daily_orders_df(all_data):
    daily_orders_df = all_data.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "total_order",
        "payment_value": "total_payment"
    }, inplace=True)
    return daily_orders_df
def create_product_items_df(all_data):
    product_item_df = all_data.groupby('product_category_name').size().sort_values(ascending=False).reset_index(
        name='count')
    return product_item_df


def create_payment_type_tr_df(all_data):
    payment_type_tr = all_data.groupby('payment_type').size().sort_values(ascending=False).reset_index(name='count')
    return payment_type_tr


def create_top_5_categories_df(all_data):
    top_5_categories = all_data.groupby('product_category_name')['review_score'].mean().sort_values().reset_index(name='mean').head(5)
    return top_5_categories


def create_top_5_state_df(all_data):
    top_5_state = all_data.groupby('customer_state').size().sort_values(ascending=False).reset_index(name='count').head(
        5)
    top_5_state.rename(columns={
        "customer_state": "customer_state"
    }, inplace=True)
    return top_5_state

def create_top_5_seller_df(all_data):
    top_5_seller = all_data.groupby('seller_id').size().sort_values(ascending=False).reset_index(name='count').head(5)
    top_5_seller.rename(columns={
        "seller_id": "seller_id"
    }, inplace=True)
    return top_5_seller


def create_rfm_df(df):
    rfm_df = all_data.groupby(by="customer_id", as_index=False).agg({
        "order_approved_at": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_approved_at"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df


datetime_columns = ["order_approved_at", "delivery_time"]
all_data.sort_values(by="order_approved_at", inplace=True)
all_data.reset_index(inplace=True)

for column in datetime_columns:
    all_data[column] = pd.to_datetime(all_data[column])

min_date = all_data["order_approved_at"].min()
max_date = all_data["order_approved_at"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
main_df = all_data[(all_data["order_approved_at"] >= str(start_date)) &
                   (all_data["order_approved_at"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
product_items_df = create_product_items_df(main_df)
payment_type_tr_df = create_payment_type_tr_df(main_df)
top_5_categories_df = create_top_5_categories_df(main_df)
top_5_state_df = create_top_5_state_df(main_df)
top_5_seller = create_top_5_seller_df(main_df)
rfm_df = create_rfm_df(main_df)


st.header('Jakcloth collection Dashboard :sparkles:')

st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.total_order.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_payment = format_currency(daily_orders_df.total_payment.sum(), "USD ", locale='es_CO')
    st.metric("Total Payment", value=total_payment)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["total_order"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

###########################
st.subheader("Product")
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(25, 15))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        y="product_category_name",
        x="count",
        data=product_items_df.sort_values(by="count", ascending=False).head(5),
        palette = colors,
        ax=ax
    )
    ax.set_title("Best Performing Product", loc="center", fontsize=70)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=45)
    ax.tick_params(axis='y', labelsize=40)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(25, 15))

    colors = ["#90CAF9","#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="product_category_name",
        x="count",
        data=product_items_df.sort_values(by="count", ascending=True).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Worst Performing Product", loc="center", fontsize=70)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.invert_xaxis()
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.tick_params(axis='x', labelsize=45)
    ax.tick_params(axis='y', labelsize=40)
    st.pyplot(fig)

cols1, cols2 = st.columns(2)
with cols1:
    fig, ax = plt.subplots(figsize=(25, 15))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        y="product_category_name",
        x="mean",
        data=top_5_categories_df.sort_values(by="mean", ascending=False).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Top 5 Product Categories by Review Score", loc="center", fontsize=70)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=45)
    ax.tick_params(axis='y', labelsize=40)
    st.pyplot(fig)

with cols2:
    fig, ax = plt.subplots(figsize=(25, 15))

    colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        y="product_category_name",
        x="mean",
        data=top_5_categories_df.sort_values(by="mean", ascending=True).head(5),
        palette=colors,
        ax=ax
    )
    ax.set_title("Bottom 5 Product Categories by Review Score", loc="center", fontsize=70)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.invert_xaxis()
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()
    ax.tick_params(axis='x', labelsize=45)
    ax.tick_params(axis='y', labelsize=40)
    st.pyplot(fig)

######################
st.subheader("Payment")
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="payment_type",
    y="count",
    data=payment_type_tr_df.sort_values(by="count", ascending=False).head(5),
    palette=colors,
    ax=ax
)
ax.set_title("Customer Count for Each Payment Type", loc="center", fontsize=30)
ax.set_ylabel("Payment Type")
ax.set_xlabel("Customer Count")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


##########################
st.subheader("Customer Location")
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_state",
    y="count",
    data=top_5_state_df.sort_values(by="count", ascending=False).head(5),
    palette=colors,
    ax=ax
)
ax.set_title("Total of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

##########################
st.subheader("Seller Order")
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="count",
    y="seller_id",
    data=top_5_seller.sort_values(by="seller_id", ascending=False).head(5),
    palette=colors,
    ax=ax
)
ax.set_title("Top 5 seller", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)
##########################
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "USD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors,
            ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
            palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
            palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.caption('Copyright (c) Jakcloth 2023')
