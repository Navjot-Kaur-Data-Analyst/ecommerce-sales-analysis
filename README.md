# E-commerce Sales & Customer Behaviour Analysis

**Tools:** Python · MySQL · Microsoft Excel · Power BI  
**Dataset:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — Kaggle  
**Project Duration:** October 2025 – January 2026  

## Project Overview

This project analyses sales performance, customer behaviour and delivery patterns of a Brazilian e-commerce platform. The dataset contains 96,000+ real orders across 27 states and 71 product categories.

I wanted to understand what drives revenue growth, which product categories perform best, and where delivery problems occur. The analysis covers the full data pipeline from raw CSV files to an interactive dashboard.

## Key Findings

- Revenue grew from **R$57K in 2016** to over **R$1.1M per month by late 2017** — roughly 8x growth
- **Health & beauty** is the top revenue category (R$1.44M), followed by watches and bed/bath products
- **São Paulo** accounts for 37% of all revenue (R$5.9M), with RJ and MG as distant second and third
- **73% of customers** pay by credit card, with an average of 3.7 installments per transaction
- **8.1% of orders** are delivered late — mostly in northern states with longer shipping distances
- **97% of customers** only buy once — very low retention rate, a major business challenge

## Project Structure

```
ecommerce-sales-analysis/
│
├── olist_phase2_cleaning_eda.py     # Data cleaning and EDA in Python
├── olist_phase3_analysis.sql        # SQL queries in MySQL
├── olist_dashboard.html             # Interactive dashboard (open in browser)
├── README.md
│
└── plots/
    ├── plot_01_monthly_revenue.png
    ├── plot_02_top_categories.png
    ├── plot_03_order_heatmap.png
    ├── plot_04_delivery_time.png
    ├── plot_05_order_status.png
    └── plot_06_customer_segments.png
```

## Dashboard Preview

> Open `olist_dashboard.html` in any browser to see the fully interactive dashboard.  
> Use the year filter buttons to switch between 2016, 2017 and 2018 views.

## Charts Generated

**1. Monthly Revenue Trend**  
Clear upward growth from late 2016 with a sharp spike in November 2017 (Black Friday).

**2. Top 10 Product Categories**  
Health & beauty leads, followed by watches/gifts and bed/bath. Electronics rank lower despite higher average prices.

**3. Order Volume Heatmap**  
Most orders placed between 10am–4pm on weekdays. Sunday evenings also show a spike.

**4. Delivery Time Distribution**  
Median delivery time is around 12 days. Significant tail of late deliveries beyond 20 days.

**5. Order Status Breakdown**  
Over 96% of orders are delivered successfully. Cancelled orders account for less than 1%.

**6. Customer Segments**  
97% one-time buyers vs 3% repeat buyers — highlights retention as a key business problem.

## SQL Highlights

The SQL analysis includes:
- Monthly revenue trend with GROUP BY
- Top categories and states ranked by revenue  
- Late delivery rate per state
- Customer segmentation using CTEs
- Seller ranking using `RANK()` window function
- Month-over-month growth using `LAG()` window function

## How to Run

**Python script:**
```bash
pip install pandas numpy matplotlib seaborn
python olist_phase2_cleaning_eda.py
```

**SQL queries:**
1. Import CSV files into MySQL Workbench
2. Run `olist_phase3_analysis.sql`

**Dashboard:**  
Open `olist_dashboard.html` directly in Chrome or Firefox — no server needed.

## About

**Navjot Kaur**  
MSc Computer Science · IU International University of Applied Sciences, Berlin  
Specialisation: Data Analysis, Machine Learning, Python  

[LinkedIn](https://linkedin.com) · [Email](mailto:your@email.com)
