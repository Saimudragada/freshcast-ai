"""
FreshCast AI - Intelligent Query Router
Routes user queries to ML model or LLM based on query type
"""

import re
from enum import Enum

class QueryType(Enum):
    """Types of queries the system can handle"""
    FORECAST_DEMAND = "forecast_demand"          # ML Model
    INVENTORY_NEEDS = "inventory_needs"          # ML Model
    RAW_MATERIALS = "raw_materials"              # ML Model
    BUSINESS_ADVICE = "business_advice"          # LLM
    SUPPLIER_INFO = "supplier_info"              # LLM
    GENERAL_QUESTION = "general_question"        # LLM

class QueryRouter:
    """
    Routes user queries to appropriate handler (ML or LLM)
    """
    
    def __init__(self):
        # Keywords for ML-based queries (data-driven)
        self.ml_keywords = {
            'forecast': ['forecast', 'predict', 'prediction', 'expect', 'anticipated'],
            'demand': ['demand', 'need', 'sales', 'sell', 'sold'],
            'inventory': ['inventory', 'stock', 'produce', 'production', 'make', 'bake'],
            'materials': ['material', 'ingredient', 'flour', 'eggs', 'butter', 'sugar'],
            'quantity': ['how many', 'how much', 'quantity', 'amount'],
            'time': ['today', 'tomorrow', 'next week', 'this week', 'next', 'week', 'day'],
        }
        
        # Keywords for LLM-based queries (knowledge-driven)
        self.llm_keywords = {
            'supplier': ['supplier', 'buy', 'purchase', 'vendor', 'where', 'cheap', 'price'],
            'advice': ['should i', 'recommend', 'suggest', 'advice', 'tips', 'help', 'how to'],
            'quality': ['quality', 'fresh', 'store', 'storage', 'shelf life'],
            'recipe': ['recipe', 'substitute', 'alternative', 'replace'],
        }
        
        # Product names
        self.products = [
            'croissant', 'baguette', 'sourdough', 'sandwich', 
            'donut', 'muffin', 'cinnamon roll', 'cinnamon_roll'
        ]
    
    def classify_query(self, query):
        """
        Classify query into ML or LLM category
        Returns: (QueryType, confidence_score)
        """
        query_lower = query.lower()
        
        # Count keyword matches
        ml_score = 0
        llm_score = 0
        
        # Check ML keywords
        for category, keywords in self.ml_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    ml_score += 1
        
        # Check LLM keywords
        for category, keywords in self.llm_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    llm_score += 1
        
        # Specific pattern matching for better accuracy
        
        # Pattern 1: "How many/much [product] [time]"
        if re.search(r'how (many|much).*?(croissant|baguette|sourdough|sandwich|donut|muffin)', query_lower):
            return QueryType.FORECAST_DEMAND, 0.9
        
        # Pattern 2: "What do we/I need"
        if re.search(r'what.*(do|should).*(we|i).*need', query_lower):
            if any(word in query_lower for word in ['ingredient', 'material', 'flour', 'eggs']):
                return QueryType.RAW_MATERIALS, 0.85
            else:
                return QueryType.INVENTORY_NEEDS, 0.85
        
        # Pattern 3: "Production/inventory for [time]"
        if any(word in query_lower for word in ['production', 'inventory', 'stock']):
            return QueryType.INVENTORY_NEEDS, 0.8
        
        # Pattern 4: "Where to buy/find/purchase"
        if re.search(r'where.*(buy|find|purchase|get)', query_lower):
            return QueryType.SUPPLIER_INFO, 0.9
        
        # Pattern 5: "Should I" questions (advice)
        if query_lower.startswith('should i') or 'recommend' in query_lower:
            return QueryType.BUSINESS_ADVICE, 0.85
        
        # Default decision based on scores
        if ml_score > llm_score:
            return QueryType.FORECAST_DEMAND, 0.6
        elif llm_score > ml_score:
            return QueryType.BUSINESS_ADVICE, 0.6
        else:
            return QueryType.GENERAL_QUESTION, 0.5
    
    def extract_product(self, query):
        """
        Extract product name from query
        """
        query_lower = query.lower()
        
        for product in self.products:
            if product in query_lower:
                # Normalize product name
                return product.replace(' ', '_').title().replace('_', '_')
        
        return None
    
    def extract_time_period(self, query):
        """
        Extract time period (days) from query
        """
        query_lower = query.lower()
        
        # Check for specific time mentions
        if 'today' in query_lower:
            return 1
        elif 'tomorrow' in query_lower:
            return 1
        elif 'next week' in query_lower or 'this week' in query_lower:
            return 7
        elif 'next month' in query_lower:
            return 30
        
        # Check for number + days/weeks
        match = re.search(r'(\d+)\s*(day|week|month)', query_lower)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            
            if unit == 'day':
                return num
            elif unit == 'week':
                return num * 7
            elif unit == 'month':
                return num * 30
        
        # Default to 7 days (next week)
        return 7
    
    def route(self, query):
        """
        Main routing function
        Returns: {
            'query_type': QueryType,
            'confidence': float,
            'product': str or None,
            'time_period': int,
            'use_ml': bool,
            'use_llm': bool
        }
        """
        query_type, confidence = self.classify_query(query)
        product = self.extract_product(query)
        time_period = self.extract_time_period(query)
        
        # Determine which system to use
        use_ml = query_type in [
            QueryType.FORECAST_DEMAND,
            QueryType.INVENTORY_NEEDS,
            QueryType.RAW_MATERIALS
        ]
        
        use_llm = query_type in [
            QueryType.BUSINESS_ADVICE,
            QueryType.SUPPLIER_INFO,
            QueryType.GENERAL_QUESTION
        ]
        
        return {
            'query_type': query_type,
            'confidence': confidence,
            'product': product,
            'time_period': time_period,
            'use_ml': use_ml,
            'use_llm': use_llm,
            'original_query': query
        }


# ==========================================
# TEST THE ROUTER
# ==========================================

if __name__ == "__main__":
    router = QueryRouter()
    
    # Test queries
    test_queries = [
        "How many croissants do we need for next week?",
        "What raw materials should I order?",
        "Where can I buy cheap flour?",
        "Should I increase production for the holidays?",
        "What's our inventory needs for sandwiches tomorrow?",
        "How to store sourdough bread properly?",
        "Production forecast for donuts this week",
    ]
    
    print("🧠 Testing FreshCast AI Query Router")
    print("=" * 70)
    
    for query in test_queries:
        result = router.route(query)
        
        print(f"\n📝 Query: {query}")
        print(f"   Type: {result['query_type'].value}")
        print(f"   Confidence: {result['confidence']:.0%}")
        print(f"   Product: {result['product']}")
        print(f"   Time Period: {result['time_period']} days")
        print(f"   Use ML: {'✅' if result['use_ml'] else '❌'}")
        print(f"   Use LLM: {'✅' if result['use_llm'] else '❌'}")
    
    print("\n" + "=" * 70)
    print("✅ Router testing complete!")