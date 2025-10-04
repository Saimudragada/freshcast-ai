"""
FreshCast AI - FastAPI Application
Main API that integrates ML forecasting and LLM assistant
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from forecasting.model import FreshCastForecaster
from llm.assistant import FreshCastLLM
from router import QueryRouter

# Initialize FastAPI app
app = FastAPI(
    title="FreshCast AI",
    description="AI-Powered Demand Forecasting & Business Intelligence for Bakeries",
    version="1.0.0"
)

# Initialize components
forecaster = FreshCastForecaster()
llm_assistant = FreshCastLLM()
router = QueryRouter()

# Load trained models
try:
    forecaster.load_models('../../models/freshcast_models.pkl')
    print("✅ Forecasting models loaded successfully!")
except Exception as e:
    print(f"⚠️  Warning: Could not load models - {e}")

# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    query_type: str
    confidence: float
    used_ml: bool
    used_llm: bool

class ForecastRequest(BaseModel):
    product: str
    days_ahead: int = 7

# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "🥐 FreshCast AI is running!",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/query", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    """
    Main query endpoint - handles any user question
    Routes to ML or LLM based on query type
    """
    try:
        # Route the query
        routing = router.route(request.question)
        
        answer = ""
        
        # Handle ML-based queries
        if routing['use_ml']:
            if routing['query_type'].value == 'raw_materials':
                # Get raw materials
                materials = forecaster.get_raw_materials(routing['time_period'])
                answer = f"📦 Raw Materials Needed (Next {routing['time_period']} days):\n\n"
                for _, row in materials.iterrows():
                    answer += f"• {row['material'].title()}: {row['quantity_kg']} kg\n"
            
            elif routing['product']:
                # Product-specific forecast
                inventory = forecaster.calculate_inventory_needs(
                    routing['product'], 
                    routing['time_period']
                )
                total_demand = inventory['expected_demand'].sum()
                total_production = inventory['recommended_production'].sum()
                
                answer = f"📊 Forecast for {routing['product']} (Next {routing['time_period']} days):\n\n"
                answer += f"• Expected Demand: {total_demand} units\n"
                answer += f"• Recommended Production: {total_production} units\n"
                answer += f"• Daily Average: {int(total_demand / routing['time_period'])} units\n"
            
            else:
                # Overall summary
                summary = forecaster.get_weekly_summary()
                answer = f"📊 Production Summary (Next {routing['time_period']} days):\n\n"
                for _, row in summary.iterrows():
                    answer += f"• {row['product']}: {int(row['total_production'])} units\n"
        
        # Handle LLM-based queries
        if routing['use_llm']:
            llm_response = llm_assistant.query(request.question)
            if answer:  # Combine with ML answer if both used
                answer += f"\n\n💡 Additional Insight:\n{llm_response}"
            else:
                answer = llm_response
        
        # Fallback if nothing matched
        if not answer:
            answer = "I'm not sure how to answer that. Try asking about inventory needs, forecasts, or business advice!"
        
        return QueryResponse(
            answer=answer,
            query_type=routing['query_type'].value,
            confidence=routing['confidence'],
            used_ml=routing['use_ml'],
            used_llm=routing['use_llm']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forecast/{product}")
def get_forecast(product: str, days_ahead: int = 7):
    """
    Get detailed forecast for a specific product
    """
    try:
        # Normalize product name
        product_map = {
            'croissant': 'Croissant',
            'baguette': 'Baguette',
            'sourdough': 'Sourdough',
            'sandwich': 'Sandwich',
            'donut': 'Donut',
            'muffin': 'Muffin',
            'cinnamon_roll': 'Cinnamon_Roll',
            'cinnamon roll': 'Cinnamon_Roll'
        }
        
        product_name = product_map.get(product.lower(), product)
        
        # Get forecast
        forecast = forecaster.predict(product_name, days_ahead)
        inventory = forecaster.calculate_inventory_needs(product_name, days_ahead)
        
        return {
            "product": product_name,
            "days_ahead": days_ahead,
            "total_expected_demand": int(inventory['expected_demand'].sum()),
            "total_recommended_production": int(inventory['recommended_production'].sum()),
            "daily_forecast": inventory.to_dict(orient='records')
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/materials")
def get_materials(days_ahead: int = 7):
    """
    Get raw material requirements
    """
    try:
        materials = forecaster.get_raw_materials(days_ahead)
        return {
            "days_ahead": days_ahead,
            "materials": materials.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary")
def get_summary(days_ahead: int = 7):
    """
    Get production summary for all products
    """
    try:
        summary = forecaster.get_weekly_summary()
        return {
            "days_ahead": days_ahead,
            "products": summary.to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting FreshCast AI API...")
    print("📍 API will be available at: http://localhost:8000")
    print("📖 Interactive docs at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)