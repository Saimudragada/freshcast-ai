"""
FreshCast AI - LLM Business Assistant
Handles business advice, supplier info, and general bakery questions
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FreshCastLLM:
    """
    LLM-powered business assistant for bakery operations
    """
    
    def __init__(self, api_key=None):
        """
        Initialize LLM assistant
        
        Args:
            api_key: OpenAI API key (if None, loads from .env file)
        """
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("⚠️  Warning: No OpenAI API key found!")
            print("   Set OPENAI_API_KEY in .env file or pass as parameter")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.system_prompt = """You are FreshCast AI Assistant, a supply chain and business expert for small bakeries.

Your role:
- Provide practical advice for bakery operations
- Suggest suppliers and cost optimization strategies
- Answer questions about ingredient storage, quality, and substitutions
- Give actionable recommendations based on industry best practices

Keep responses:
- Concise (2-3 paragraphs max)
- Actionable with specific recommendations
- Cost-conscious (remember, this is a small business)
- Professional but friendly

If asked about forecasts or inventory numbers, remind the user that the ML model handles those queries."""
    
    def query(self, user_question, context=None):
        """
        Send query to LLM and get response
        
        Args:
            user_question: User's question
            context: Optional context (e.g., current inventory data)
        
        Returns:
            LLM response text
        """
        if not self.client:
            return "❌ LLM not configured. Please set OPENAI_API_KEY in .env file."
        
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system", 
                    "content": f"Current context: {context}"
                })
            
            # Add user question
            messages.append({
                "role": "user",
                "content": user_question
            })
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_supplier_recommendations(self, material, location="general", budget="small"):
        """
        Get supplier recommendations for raw materials
        """
        query = f"""I need to buy {material} for my small bakery. 
Location: {location}
Budget level: {budget}

Please recommend:
1. Types of suppliers to consider (wholesale, retail, online)
2. Tips for getting the best price
3. Quality considerations
4. Bulk buying advice"""
        
        return self.query(query)
    
    def get_business_advice(self, question):
        """
        Get general business advice
        """
        return self.query(question)


# ==========================================
# TEST THE LLM (only if API key is set)
# ==========================================

if __name__ == "__main__":
    print("🤖 Testing FreshCast AI - LLM Assistant")
    print("=" * 70)
    
    assistant = FreshCastLLM()
    
    if not assistant.client:
        print("\n⚠️  To test the LLM:")
        print("1. Create a .env file in the project root")
        print("2. Add: OPENAI_API_KEY=your_api_key_here")
        print("3. Run this script again")
        print("\n💡 For now, we'll skip LLM testing and use it later in the API.")
    else:
        # Test queries
        print("\n📝 Test 1: Supplier Recommendation")
        print("-" * 70)
        response = assistant.get_supplier_recommendations("flour", "United States", "small")
        print(response)
        
        print("\n📝 Test 2: Business Advice")
        print("-" * 70)
        response = assistant.get_business_advice("How can I reduce waste in my bakery?")
        print(response)
    
    print("\n" + "=" * 70)
    print("✅ LLM assistant ready!")