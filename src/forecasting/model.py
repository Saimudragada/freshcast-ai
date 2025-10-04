"""
FreshCast AI - Demand Forecasting Model
Uses Prophet for time series forecasting with business logic
"""

import pandas as pd
import numpy as np
from prophet import Prophet
import pickle
import os
from datetime import datetime, timedelta

class FreshCastForecaster:
    """
    Bakery demand forecasting with inventory optimization
    """
    
    def __init__(self):
        self.models = {}  # Store one model per product
        self.trained = False
        
    def prepare_data(self, df, product_name):
        """
        Prepare data for Prophet (needs 'ds' and 'y' columns)
        """
        product_data = df[df['product'] == product_name].copy()
        
        # Prophet requires specific column names
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(product_data['date']),
            'y': product_data['sales']
        })
        
        # Add additional features
        prophet_df['is_weekend'] = product_data['is_weekend'].values
        prophet_df['is_holiday'] = product_data['is_holiday'].values
        
        return prophet_df.sort_values('ds')
    
    def train(self, train_data, products=None):
        """
        Train forecasting models for each product
        """
        if products is None:
            products = train_data['product'].unique()
        
        print("🤖 Training FreshCast AI Models...")
        print("=" * 60)
        
        for product in products:
            print(f"Training model for: {product}...")
            
            # Prepare data
            prophet_df = self.prepare_data(train_data, product)
            
            # Initialize Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05,  # Flexibility for trend changes
                seasonality_prior_scale=10.0,   # Strength of seasonality
            )
            
            # Add custom seasonalities
            model.add_country_holidays(country_name='US')
            
            # Fit model
            model.fit(prophet_df)
            
            # Store model
            self.models[product] = model
            
        self.trained = True
        print(f"\n✅ Trained {len(self.models)} models successfully!")
        print("=" * 60)
    
    def predict(self, product_name, days_ahead=7):
        """
        Predict demand for next N days
        """
        if not self.trained:
            raise ValueError("Models not trained yet! Call train() first.")
        
        if product_name not in self.models:
            raise ValueError(f"No model found for product: {product_name}")
        
        # Create future dataframe
        model = self.models[product_name]
        future = model.make_future_dataframe(periods=days_ahead)
        
        # Predict
        forecast = model.predict(future)
        
        # Get only future predictions
        future_forecast = forecast.tail(days_ahead)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
        future_forecast['yhat'] = future_forecast['yhat'].clip(lower=0)  # No negative demand
        
        return future_forecast
    
    def calculate_inventory_needs(self, product_name, days_ahead=7, service_level=0.95):
        """
        Calculate production requirements with safety stock
        """
        forecast = self.predict(product_name, days_ahead)
        
        # Calculate safety stock based on prediction uncertainty
        forecast['uncertainty'] = forecast['yhat_upper'] - forecast['yhat']
        
        # Production = Expected demand + Safety stock
        # Safety stock covers uncertainty to meet service level
        forecast['recommended_production'] = (
            forecast['yhat'] + 
            forecast['uncertainty'] * service_level
        ).round().astype(int)
        
        forecast['expected_demand'] = forecast['yhat'].round().astype(int)
        
        return forecast[['ds', 'expected_demand', 'recommended_production']]
    
    def get_weekly_summary(self, product_name=None):
        """
        Get weekly production summary for all or specific product
        """
        if product_name:
            products = [product_name]
        else:
            products = list(self.models.keys())
        
        summaries = []
        
        for product in products:
            inventory = self.calculate_inventory_needs(product, days_ahead=7)
            
            summary = {
                'product': product,
                'total_demand': inventory['expected_demand'].sum(),
                'total_production': inventory['recommended_production'].sum(),
                'daily_average': inventory['expected_demand'].mean(),
            }
            summaries.append(summary)
        
        return pd.DataFrame(summaries)
    
    def get_raw_materials(self, days_ahead=7):
        """
        Calculate raw material requirements based on recipes
        
        Simplified recipe assumptions (kg per 100 units):
        """
        RECIPES = {
            'Croissant': {'flour': 12, 'butter': 8, 'eggs': 15},
            'Baguette': {'flour': 15, 'butter': 0, 'eggs': 0},
            'Sourdough': {'flour': 18, 'butter': 2, 'eggs': 0},
            'Sandwich': {'flour': 8, 'butter': 3, 'eggs': 10, 'meat': 5, 'vegetables': 3},
            'Donut': {'flour': 10, 'butter': 5, 'eggs': 12, 'sugar': 6},
            'Muffin': {'flour': 11, 'butter': 4, 'eggs': 10, 'sugar': 5},
            'Cinnamon_Roll': {'flour': 12, 'butter': 6, 'eggs': 8, 'sugar': 7},
        }
        
        # Get production needs for all products
        materials = {}
        
        for product in self.models.keys():
            inventory = self.calculate_inventory_needs(product, days_ahead)
            total_production = inventory['recommended_production'].sum()
            
            if product in RECIPES:
                for material, qty_per_100 in RECIPES[product].items():
                    needed = (total_production / 100) * qty_per_100
                    materials[material] = materials.get(material, 0) + needed
        
        # Convert to DataFrame
        materials_df = pd.DataFrame([
            {'material': mat, 'quantity_kg': round(qty, 2)}
            for mat, qty in materials.items()
        ]).sort_values('quantity_kg', ascending=False)
        
        return materials_df
    
    def save_models(self, filepath='../../models/freshcast_models.pkl'):
        """
        Save trained models to disk
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(self.models, f)
        print(f"✅ Models saved to: {filepath}")
    
    def load_models(self, filepath='../../models/freshcast_models.pkl'):
        """
        Load trained models from disk
        """
        with open(filepath, 'rb') as f:
            self.models = pickle.load(f)
        self.trained = True
        print(f"✅ Models loaded from: {filepath}")


# ==========================================
# TRAINING SCRIPT
# ==========================================

if __name__ == "__main__":
    print("\n🚀 FreshCast AI - Training Forecasting Models")
    print("=" * 60)
    
    # Load training data
    print("📊 Loading training data...")
    train_data = pd.read_csv('../../data/processed/train_data.csv')
    print(f"✅ Loaded {len(train_data):,} records")
    
    # Initialize and train
    forecaster = FreshCastForecaster()
    forecaster.train(train_data)
    
    # Save models
    forecaster.save_models()
    
    # Test predictions
    print("\n📈 Testing Predictions (Next 7 Days):")
    print("=" * 60)
    
    # Get weekly summary
    summary = forecaster.get_weekly_summary()
    print("\n🥐 Weekly Production Needs:")
    print(summary.to_string(index=False))
    
    # Get raw materials
    print("\n📦 Raw Material Requirements (Next 7 Days):")
    materials = forecaster.get_raw_materials(days_ahead=7)
    print(materials.to_string(index=False))
    
    print("\n✅ Training Complete!")
    print("=" * 60)