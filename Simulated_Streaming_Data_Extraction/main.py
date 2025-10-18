import os
import time
import pandas as pd
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime, timedelta
import kaggle
import zipfile

# ======== DATABASE CONNECTION SETUP ======== #
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB2", "customer_shopping_db")
PG_HOST = "localhost"
PG_PORT = "5432"

if not PG_USER or not PG_PASSWORD:
    raise EnvironmentError("Database credentials not found in environment variables.")

# Create the database if it doesn't exist
try:
    conn = psycopg2.connect(
        dbname="postgres",
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {PG_DB}")
        print(f"Database '{PG_DB}' created.")
    else:
        print(f"ℹ Database '{PG_DB}' already exists.")
    cur.close()
    conn.close()
except Exception as e:
    print("Error creating database:", e)

# ======== CONNECT TO TARGET DATABASE ======== #
try:
    conn = psycopg2.connect(
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT
    )
    cur = conn.cursor()
except Exception as e:
    raise ConnectionError("Error connecting to target database:", e)

# ======== CREATE STAGING TABLE ======== #
create_table_query = """
CREATE TABLE IF NOT EXISTS staging_sales (
    transaction_id SERIAL PRIMARY KEY,
    transaction_time TIMESTAMP,
    customer_id VARCHAR(50),
    age INT,
    gender VARCHAR(10),
    item_purchased TEXT,
    category TEXT,
    purchase_amount_usd NUMERIC,
    location TEXT,
    size TEXT,
    color TEXT,
    season TEXT,
    review_rating NUMERIC,
    subscription_status TEXT,
    payment_method TEXT,
    shipping_type TEXT,
    discount_applied BOOLEAN,
    promo_code_used BOOLEAN,
    previous_purchases INT,
    preferred_payment_method TEXT,
    frequency_of_purchases TEXT
);
"""
cur.execute(create_table_query)
conn.commit()
print("Staging_sales table ready.")

# ======== DOWNLOAD KAGGLE DATASET ======== #
dataset = 'bhadramohit/customer-shopping-latest-trends-dataset'
download_path = os.path.dirname(os.path.abspath(__file__))  # current folder of main.py

# Download dataset (no unzip to avoid nested folder)
kaggle.api.dataset_download_files(dataset, path=download_path, unzip=False)

# Find the downloaded zip file
zip_file = None
for f in os.listdir(download_path):
    if f.endswith('.zip'):
        zip_file = os.path.join(download_path, f)
        break

if zip_file:
    # Extract CSV directly into current folder
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(download_path)
    os.remove(zip_file)
    print("Dataset downloaded and extracted directly into Simulated_Streaming_Data_Extraction folder.")
else:
    print("No zip file found after Kaggle download.")


# ======== READ CSV & ADD TIMESTAMP ======== #
# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Automatically find the CSV file in the same folder
csv_file = None
for f in os.listdir(current_dir):
    if f.endswith('.csv'):
        csv_file = os.path.join(current_dir, f)
        break

if csv_file:
    df = pd.read_csv(csv_file)
    print(f"Loaded CSV: {os.path.basename(csv_file)} ({len(df)} rows)")
else:
    raise FileNotFoundError("No CSV file found in current directory.")


# Generate artificial timestamp column (10-second intervals)
start_time = datetime.now()
df["transaction_time"] = [
    start_time + timedelta(seconds=i * 10) for i in range(len(df))
]

# Replace NaNs with None for SQL insert
df = df.where(pd.notnull(df), None)

# ======== STREAMING INSERTION ======== #
insert_query = """
INSERT INTO staging_sales (
    transaction_time, customer_id, age, gender, item_purchased, category,
    purchase_amount_usd, location, size, color, season, review_rating,
    subscription_status, payment_method, shipping_type, discount_applied,
    promo_code_used, previous_purchases, preferred_payment_method, frequency_of_purchases
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

print("Starting simulated streaming to PostgreSQL...")

try:
    for i, row in df.iterrows():
        data_tuple = tuple(row[col] for col in [
            "transaction_time", "Customer ID", "Age", "Gender", "Item Purchased",
            "Category", "Purchase Amount (USD)", "Location", "Size", "Color", "Season",
            "Review Rating", "Subscription Status", "Payment Method", "Shipping Type",
            "Discount Applied", "Promo Code Used", "Previous Purchases",
            "Preferred Payment Method", "Frequency of Purchases"
        ])
        cur.execute(insert_query, data_tuple)
        conn.commit()

        print(f"Inserted row {i+1}/{len(df)} at {row['transaction_time']}")
        time.sleep(0.05)  # simulate streaming delay (0.5s per record)

except Exception as e:
    print("Error during streaming insert:", e)
    conn.rollback()
finally:
    cur.close()
    conn.close()
    print("Streaming completed and connection closed.")
