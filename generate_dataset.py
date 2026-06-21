"""
generate_dataset.py
Generates a realistic synthetic food delivery orders dataset for
"Food Delivery Sales & Customer Insights" analysis.

The data is deliberately made "messy" (missing values, duplicate rows,
inconsistent text casing) so the analysis notebook has real cleaning
work to perform, matching the project brief.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)

N_ORDERS = 650

areas = [
    "Anna Nagar", "T Nagar", "Adyar", "Velachery",
    "Tambaram", "Mylapore", "Nungambakkam", "Porur"
]

dishes = {
    "Chicken Biryani": ("Biryani", 220),
    "Mutton Biryani": ("Biryani", 280),
    "Veg Biryani": ("Biryani", 170),
    "Paneer Butter Masala": ("North Indian", 190),
    "Butter Naan": ("North Indian", 40),
    "Chole Bhature": ("North Indian", 130),
    "Masala Dosa": ("South Indian", 90),
    "Idli Sambar": ("South Indian", 70),
    "Filter Coffee": ("Beverages", 30),
    "Veg Fried Rice": ("Chinese", 140),
    "Egg Fried Rice": ("Chinese", 150),
    "Veg Manchurian": ("Chinese", 160),
    "Chicken 65": ("Starters", 200),
    "Chicken Shawarma": ("Fast Food", 150),
    "Veg Burger": ("Fast Food", 110),
    "Margherita Pizza": ("Fast Food", 250),
    "Cold Coffee": ("Beverages", 80),
    "Gulab Jamun": ("Desserts", 60),
}

dish_names = list(dishes.keys())
# Make biryani / fast-food items more popular than others (realistic skew)
weights = np.array([
    14, 8, 6, 7, 5, 5, 6, 5, 4, 5, 4, 4, 6, 7, 6, 8, 4, 4
], dtype=float)
weights = weights / weights.sum()

payment_methods = ["UPI", "Card", "Cash on Delivery", "Wallet"]
payment_weights = [0.45, 0.20, 0.20, 0.15]

start_date = datetime(2026, 1, 1)

rows = []
for i in range(1, N_ORDERS + 1):
    order_id = 1000 + i
    customer_id = f"CUST{rng.integers(1, 220):04d}"

    day_offset = rng.integers(0, 90)
    order_date = start_date + timedelta(days=int(day_offset))

    # Order time skewed toward lunch (12-14) and dinner (19-22) peaks
    # hours 8..23 -> 16 hours
    hour_choices = list(range(8, 24))
    hour_p = np.array([
        1, 1, 2, 4, 9, 10, 6, 3,
        3, 4, 6, 9, 10, 9, 6, 3
    ], dtype=float)
    hour_p = hour_p / hour_p.sum()
    order_hour = rng.choice(hour_choices, p=hour_p)
    order_minute = rng.integers(0, 60)
    order_time = f"{order_hour:02d}:{order_minute:02d}"

    area = rng.choice(areas)
    dish = rng.choice(dish_names, p=weights)
    category, base_price = dishes[dish]
    qty = rng.choice([1, 1, 1, 2, 2, 3], p=[0.35, 0.2, 0.15, 0.15, 0.1, 0.05])
    price = base_price
    total_amount = price * qty

    delivery_time = rng.integers(18, 55)
    rating = rng.choice([3, 4, 4, 5, 5, 5], p=[0.1, 0.2, 0.2, 0.2, 0.15, 0.15])
    payment = rng.choice(payment_methods, p=payment_weights)

    rows.append({
        "order_id": order_id,
        "customer_id": customer_id,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "order_time": order_time,
        "area": area,
        "dish_name": dish,
        "category": category,
        "quantity": qty,
        "price": price,
        "total_amount": total_amount,
        "delivery_time_mins": delivery_time,
        "rating": rating,
        "payment_method": payment,
    })

df = pd.DataFrame(rows)

# ---- Introduce realistic messiness ----

# 1. Inconsistent casing / spacing in 'area' for a subset of rows
messy_idx = rng.choice(df.index, size=40, replace=False)
def messy_area(a):
    choice = rng.integers(0, 3)
    if choice == 0:
        return a.lower()
    elif choice == 1:
        return f" {a} "
    else:
        return a.upper()
df.loc[messy_idx, "area"] = df.loc[messy_idx, "area"].apply(messy_area)

# 2. Missing values in rating and delivery_time_mins
missing_rating_idx = rng.choice(df.index, size=35, replace=False)
df.loc[missing_rating_idx, "rating"] = np.nan

missing_delivery_idx = rng.choice(df.index, size=28, replace=False)
df.loc[missing_delivery_idx, "delivery_time_mins"] = np.nan

# 3. Missing payment_method for a few rows
missing_payment_idx = rng.choice(df.index, size=15, replace=False)
df.loc[missing_payment_idx, "payment_method"] = np.nan

# 4. Duplicate rows (simulate accidental double-logging of an order)
dup_rows = df.sample(n=22, random_state=7)
df = pd.concat([df, dup_rows], ignore_index=True)

# 5. Shuffle so duplicates aren't neatly at the bottom
df = df.sample(frac=1, random_state=11).reset_index(drop=True)

df.to_csv("/home/claude/food_delivery_project/food_delivery_orders.csv", index=False)
print("Dataset generated:", df.shape)
print(df.head())
