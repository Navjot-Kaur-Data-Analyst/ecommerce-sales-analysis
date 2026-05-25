# -------------------------------------------------------
# Project: E-commerce Sales & Customer Behaviour Analysis
# Author: Navjot Kaur
# University: IU International University of Applied Sciences, Berlin
# Date: October 2025
# Dataset: Brazilian E-Commerce Public Dataset (Olist) - Kaggle
# -------------------------------------------------------

# I started this project as part of my MSc Computer Science program
# The goal is to understand sales patterns, customer behaviour
# and delivery performance of a Brazilian e-commerce platform

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# set the path where i saved my dataset
# change this to your own path if you're running this
DATA_PATH = "data/"

# -------------------------------------------------------
# STEP 1 - Load the CSV files
# -------------------------------------------------------

print("Loading data files...")

orders = pd.read_csv(DATA_PATH + "olist_orders_dataset.csv")
order_items = pd.read_csv(DATA_PATH + "olist_order_items_dataset.csv")
customers = pd.read_csv(DATA_PATH + "olist_customers_dataset.csv")
products = pd.read_csv(DATA_PATH + "olist_products_dataset.csv")
payments = pd.read_csv(DATA_PATH + "olist_order_payments_dataset.csv")
reviews = pd.read_csv(DATA_PATH + "olist_order_reviews_dataset.csv")
category_translation = pd.read_csv(DATA_PATH + "product_category_name_translation.csv")

print("Files loaded successfully")
print(f"Total orders in dataset: {len(orders)}")

# -------------------------------------------------------
# STEP 2 - First look at the data
# -------------------------------------------------------

# checking shape and columns of each table
print("\n--- Orders table ---")
print(orders.shape)
print(orders.dtypes)
print(orders.isnull().sum())

print("\n--- Order items table ---")
print(order_items.shape)
print(order_items.isnull().sum())

# -------------------------------------------------------
# STEP 3 - Clean the orders table
# -------------------------------------------------------

# convert date columns - they came in as strings
date_columns = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in date_columns:
    orders[col] = pd.to_datetime(orders[col], errors='coerce')

# remove rows where purchase date is missing - cant use these
orders.dropna(subset=['order_purchase_timestamp'], inplace=True)

# separate delivered orders for delivery time analysis
delivered_orders = orders[orders['order_status'] == 'delivered'].copy()
print(f"\nDelivered orders: {len(delivered_orders)}")
print(f"Other statuses: {orders['order_status'].value_counts().to_dict()}")

# fill missing delivery dates with estimated date
# this is a reasonable assumption since we dont have actual date
delivered_orders['order_delivered_customer_date'].fillna(
    delivered_orders['order_estimated_delivery_date'], inplace=True
)

# extract time features - useful for trend analysis later
orders['year'] = orders['order_purchase_timestamp'].dt.year
orders['month'] = orders['order_purchase_timestamp'].dt.month
orders['day_of_week'] = orders['order_purchase_timestamp'].dt.day_name()
orders['hour'] = orders['order_purchase_timestamp'].dt.hour
orders['year_month'] = orders['order_purchase_timestamp'].dt.strftime('%Y-%m')

# calculate delivery time in days
delivered_orders['delivery_days'] = (
    delivered_orders['order_delivered_customer_date'] -
    delivered_orders['order_purchase_timestamp']
).dt.days

delivered_orders['estimated_days'] = (
    delivered_orders['order_estimated_delivery_date'] -
    delivered_orders['order_purchase_timestamp']
).dt.days

# check if order was late
delivered_orders['is_late'] = (
    delivered_orders['order_delivered_customer_date'] >
    delivered_orders['order_estimated_delivery_date']
)

late_pct = delivered_orders['is_late'].mean() * 100
print(f"Late delivery rate: {late_pct:.1f}%")

# -------------------------------------------------------
# STEP 4 - Clean the products table
# -------------------------------------------------------

# add english category names
products = products.merge(category_translation, on='product_category_name', how='left')
products['product_category_name_english'].fillna('unknown', inplace=True)

# fill missing dimensions with median
# not the most accurate but good enough for this analysis
dim_cols = ['product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm']
for col in dim_cols:
    products[col].fillna(products[col].median(), inplace=True)

print(f"\nProducts cleaned. Total categories: {products['product_category_name_english'].nunique()}")

# -------------------------------------------------------
# STEP 5 - Clean order_items and calculate revenue
# -------------------------------------------------------

order_items.drop_duplicates(inplace=True)

# total revenue per item = price + shipping
order_items['revenue'] = order_items['price'] + order_items['freight_value']

print(f"\nTotal revenue in dataset: R${order_items['revenue'].sum():,.0f}")

# -------------------------------------------------------
# STEP 6 - Merge everything into one master dataframe
# -------------------------------------------------------

print("\nMerging tables...")

master_df = (
    orders
    .merge(order_items, on='order_id', how='inner')
    .merge(customers, on='customer_id', how='left')
    .merge(products, on='product_id', how='left')
)

# add payment info separately (one order can have multiple payments)
payment_summary = payments.groupby('order_id')['payment_value'].sum().reset_index()
master_df = master_df.merge(payment_summary, on='order_id', how='left')

print(f"Master dataframe shape: {master_df.shape}")
print(f"Date range: {master_df['order_purchase_timestamp'].min().date()} to {master_df['order_purchase_timestamp'].max().date()}")

# save for later use in SQL and Power BI
master_df.to_csv(DATA_PATH + "master_cleaned.csv", index=False)
print("Saved master_cleaned.csv")

# -------------------------------------------------------
# STEP 7 - Basic summary statistics
# -------------------------------------------------------

print("\n====== SUMMARY ======")
print(f"Total orders:        {master_df['order_id'].nunique():,}")
print(f"Total customers:     {master_df['customer_id'].nunique():,}")
print(f"Total revenue:       R${master_df['revenue'].sum():,.2f}")
print(f"Avg order value:     R${master_df.groupby('order_id')['revenue'].sum().mean():.2f}")
print(f"Product categories:  {master_df['product_category_name_english'].nunique()}")

# -------------------------------------------------------
# STEP 8 - Visualisations
# -------------------------------------------------------

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 5)
plt.rcParams['figure.dpi'] = 120

# -- Chart 1: Monthly Revenue Trend --
monthly = (
    master_df[master_df['year'].isin([2017, 2018])]
    .groupby('year_month')['revenue']
    .sum()
    .reset_index()
    .sort_values('year_month')
)

fig, ax = plt.subplots()
ax.plot(monthly['year_month'], monthly['revenue'],
        color='#185FA5', linewidth=2, marker='o', markersize=4)
ax.fill_between(monthly['year_month'], monthly['revenue'],
                alpha=0.08, color='#185FA5')
ax.set_title('Monthly Revenue Trend (2017-2018)', fontsize=13, fontweight='bold')
ax.set_xlabel('Month')
ax.set_ylabel('Revenue (R$)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(DATA_PATH + 'plot_01_monthly_revenue.png', bbox_inches='tight')
plt.show()
print("Saved plot 1")

# -- Chart 2: Top 10 Product Categories --
top_cats = (
    master_df.groupby('product_category_name_english')['revenue']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig, ax = plt.subplots()
ax.barh(top_cats['product_category_name_english'][::-1],
        top_cats['revenue'][::-1],
        color='#1D9E75')
ax.set_title('Top 10 Product Categories by Revenue', fontsize=13, fontweight='bold')
ax.set_xlabel('Total Revenue (R$)')
plt.tight_layout()
plt.savefig(DATA_PATH + 'plot_02_top_categories.png', bbox_inches='tight')
plt.show()
print("Saved plot 2")

# -- Chart 3: Order Volume Heatmap by Day and Hour --
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

heatmap_data = (
    master_df.groupby(['day_of_week', 'hour'])['order_id']
    .nunique()
    .reset_index()
    .pivot(index='day_of_week', columns='hour', values='order_id')
    .reindex(day_order)
)

fig, ax = plt.subplots(figsize=(14, 5))
sns.heatmap(heatmap_data, cmap='Blues', ax=ax, linewidths=0.3)
ax.set_title('Order Volume by Day and Hour', fontsize=13, fontweight='bold')
ax.set_xlabel('Hour of day')
ax.set_ylabel('')
plt.tight_layout()
plt.savefig(DATA_PATH + 'plot_03_order_heatmap.png', bbox_inches='tight')
plt.show()
print("Saved plot 3")

# -- Chart 4: Delivery Time Distribution --
clean_delivery = delivered_orders[
    (delivered_orders['delivery_days'] > 0) &
    (delivered_orders['delivery_days'] < 60)
]

fig, ax = plt.subplots()
ax.hist(clean_delivery['delivery_days'], bins=30,
        color='#534AB7', edgecolor='white', linewidth=0.5)
median_days = clean_delivery['delivery_days'].median()
ax.axvline(median_days, color='red', linestyle='--', linewidth=1.5,
           label=f'Median: {median_days:.0f} days')
ax.set_title('Delivery Time Distribution', fontsize=13, fontweight='bold')
ax.set_xlabel('Days to deliver')
ax.set_ylabel('Number of orders')
ax.legend()
plt.tight_layout()
plt.savefig(DATA_PATH + 'plot_04_delivery_time.png', bbox_inches='tight')
plt.show()
print("Saved plot 4")

# -- Chart 5: Order Status Breakdown --
status_counts = orders['order_status'].value_counts()

fig, ax = plt.subplots(figsize=(7, 5))
ax.pie(status_counts,
       labels=status_counts.index,
       autopct='%1.1f%%',
       startangle=140)
ax.set_title('Order Status Breakdown', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(DATA_PATH + 'plot_05_order_status.png', bbox_inches='tight')
plt.show()
print("Saved plot 5")

# -- Chart 6: One-time vs Repeat Customers --
customer_purchase_count = master_df.groupby('customer_unique_id')['order_id'].nunique()
one_time = (customer_purchase_count == 1).sum()
repeat = (customer_purchase_count > 1).sum()

fig, ax = plt.subplots(figsize=(6, 5))
ax.bar(['One-time', 'Repeat'], [one_time, repeat],
       color=['#185FA5', '#1D9E75'], width=0.5)
ax.set_title('One-time vs Repeat Customers', fontsize=13, fontweight='bold')
ax.set_ylabel('Number of customers')
for i, v in enumerate([one_time, repeat]):
    ax.text(i, v + 200, f'{v:,}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(DATA_PATH + 'plot_06_customer_segments.png', bbox_inches='tight')
plt.show()
print("Saved plot 6")

# -------------------------------------------------------
# STEP 9 - Export summary CSVs for Excel and Power BI
# -------------------------------------------------------

# monthly summary
monthly_summary = (
    master_df.groupby(['year', 'month'])
    .agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('revenue', 'sum'),
        avg_order_value=('revenue', 'mean')
    )
    .reset_index()
)
monthly_summary.to_csv(DATA_PATH + 'summary_monthly_revenue.csv', index=False)

# category summary
category_summary = (
    master_df.groupby('product_category_name_english')
    .agg(
        total_orders=('order_id', 'nunique'),
        total_revenue=('revenue', 'sum'),
        avg_price=('price', 'mean')
    )
    .sort_values('total_revenue', ascending=False)
    .reset_index()
)
category_summary.to_csv(DATA_PATH + 'summary_category_revenue.csv', index=False)

# state summary
state_summary = (
    master_df.groupby('customer_state')
    .agg(
        total_customers=('customer_unique_id', 'nunique'),
        total_orders=('order_id', 'nunique'),
        total_revenue=('revenue', 'sum')
    )
    .sort_values('total_revenue', ascending=False)
    .reset_index()
)
state_summary.to_csv(DATA_PATH + 'summary_state_revenue.csv', index=False)

print("\nDone! All files saved.")
print("Summary CSVs saved to data/ folder")
