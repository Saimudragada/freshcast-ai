"""
FreshCast AI - Realistic Bakery Sales Data Generator
Based on 20+ years of supply chain industry patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Set random seed for reproducibility
np.random.seed(42)

# ==========================================
# BUSINESS PARAMETERS (Industry Standards)
# ==========================================

PRODUCTS = {
    'Croissant': {'baseline': 35, 'price': 3.5, 'cost': 1.2, 'shelf_life': 1},
    'Baguette': {'baseline': 45, 'price': 2.8, 'cost': 0.9, 'shelf_life': 1},
    'Sourdough': {'baseline': 25, 'price': 5.5, 'cost': 2.0, 'shelf_life': 3},
    'Sandwich': {'baseline': 28, 'price': 6.5, 'cost': 2.8, 'shelf_life': 1},
    'Donut': {'baseline': 40, 'price': 2.5, 'cost': 0.8, 'shelf_life': 2},
    'Muffin': {'baseline': 30, 'price': 3.2, 'cost': 1.1, 'shelf_life': 2},
    'Cinnamon_Roll': {'baseline': 22, 'price': 4.0, 'cost': 1.5, 'shelf_life': 2},
}

SEASONAL_PATTERNS = {
    'January': 0.85, 'February': 0.90, 'March': 0.95, 'April': 1.0,
    'May': 1.05, 'June': 0.95, 'July': 0.90, 'August': 0.92,
    'September': 1.05, 'October': 1.1, 'November': 1.2, 'December': 1.3,
}

DAY_OF_WEEK_MULTIPLIERS = {
    'Monday': 0.85, 'Tuesday': 0.90, 'Wednesday': 0.95, 'Thursday': 1.0,
    'Friday': 1.15, 'Saturday': 1.4, 'Sunday': 1.3,
}

WEATHER_IMPACT = {'Sunny': 1.1, 'Cloudy': 1.0, 'Rainy': 0.85, 'Stormy': 0.7}

HOLIDAYS = [
    '2023-01-01', '2023-02-14', '2023-03-17', '2023-04-09',
    '2023-05-28', '2023-07-04', '2023-09-04', '2023-10-31',
    '2023-11-23', '2023-12-25', '2023-12-31',
    '2024-01-01', '2024-02-14', '2024-03-17', '2024-03-31',
    '2024-05-27', '2024-07-04', '2024-09-02', '2024-10-31',
    '2024-11-28', '2024-12-25', '2024-12-31',
]

def generate_bakery_sales(start_date='2023-01-01', end_date='2024-12-31'):
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    data = []
    
    for date in date_range:
        day_name = date.strftime('%A')
        month_name = date.strftime('%B')
        is_holiday = date.strftime('%Y-%m-%d') in HOLIDAYS
        is_weekend = day_name in ['Saturday', 'Sunday']
        
        weather = np.random.choice(
            list(WEATHER_IMPACT.keys()), 
            p=[0.5, 0.3, 0.15, 0.05]
        )
        
        for product, specs in PRODUCTS.items():
            base_demand = specs['baseline']
            
            seasonal_mult = SEASONAL_PATTERNS[month_name]
            dow_mult = DAY_OF_WEEK_MULTIPLIERS[day_name]
            weather_mult = WEATHER_IMPACT[weather]
            holiday_mult = 1.5 if is_holiday else 1.0
            
            expected_demand = (
                base_demand * seasonal_mult * dow_mult * 
                weather_mult * holiday_mult
            )
            
            noise = np.random.normal(1.0, 0.15)
            actual_demand = max(0, int(expected_demand * noise))
            
            safety_stock_mult = 1.1 if is_weekend or is_holiday else 1.05
            production = int(expected_demand * safety_stock_mult)
            
            sales = min(actual_demand, production)
            waste = max(0, production - sales)
            stockout = max(0, actual_demand - sales)
            
            revenue = sales * specs['price']
            production_cost = production * specs['cost']
            waste_cost = waste * specs['cost']
            profit = revenue - production_cost
            
            service_level = (sales / actual_demand * 100) if actual_demand > 0 else 100
            
            data.append({
                'date': date,
                'year': date.year,
                'month': date.month,
                'month_name': month_name,
                'day': date.day,
                'day_of_week': day_name,
                'day_of_week_num': date.dayofweek,
                'week_of_year': date.isocalendar()[1],
                'is_weekend': is_weekend,
                'is_holiday': is_holiday,
                'weather': weather,
                'product': product,
                'actual_demand': actual_demand,
                'production': production,
                'sales': sales,
                'waste': waste,
                'stockout': stockout,
                'price': specs['price'],
                'cost_per_unit': specs['cost'],
                'revenue': round(revenue, 2),
                'production_cost': round(production_cost, 2),
                'waste_cost': round(waste_cost, 2),
                'profit': round(profit, 2),
                'service_level': round(service_level, 2),
                'shelf_life_days': specs['shelf_life'],
            })
    
    return pd.DataFrame(data)

# ==========================================
# GENERATE AND SAVE
# ==========================================

print("🥐 Generating FreshCast AI Training Data...")
print("=" * 60)

df = generate_bakery_sales('2023-01-01', '2024-12-31')

print(f"✅ Generated {len(df):,} records")
print(f"📅 Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"🥐 Products: {df['product'].nunique()}")

# Business metrics
total_revenue = df['revenue'].sum()
total_cost = df['production_cost'].sum()
total_waste_cost = df['waste_cost'].sum()
total_profit = df['profit'].sum()
avg_service_level = df['service_level'].mean()
waste_rate = (df['waste'].sum() / df['production'].sum() * 100)

print("\n" + "=" * 60)
print("💰 BUSINESS METRICS")
print("=" * 60)
print(f"Total Revenue:        ${total_revenue:,.2f}")
print(f"Total Profit:         ${total_profit:,.2f}")
print(f"Profit Margin:        {(total_profit/total_revenue*100):.1f}%")
print(f"Waste Cost:           ${total_waste_cost:,.2f}")
print(f"Service Level:        {avg_service_level:.1f}%")
print(f"Waste Rate:           {waste_rate:.1f}%")

# Save files
os.makedirs('../data/raw', exist_ok=True)
os.makedirs('../data/processed', exist_ok=True)

df.to_csv('../data/raw/bakery_sales_2023_2024.csv', index=False)
print(f"\n✅ Saved: data/raw/bakery_sales_2023_2024.csv")

# Train/test split
train_cutoff = '2024-10-01'
df_train = df[df['date'] < train_cutoff]
df_test = df[df['date'] >= train_cutoff]

df_train.to_csv('../data/processed/train_data.csv', index=False)
df_test.to_csv('../data/processed/test_data.csv', index=False)

print(f"✅ Saved: data/processed/train_data.csv ({len(df_train):,} records)")
print(f"✅ Saved: data/processed/test_data.csv ({len(df_test):,} records)")

print("\n🎉 Data generation complete!")
print("=" * 60)