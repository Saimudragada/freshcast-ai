"""
FreshCast AI - Web Dashboard
Simple interface for bakery owners to interact with the system
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="FreshCast AI",
    page_icon="🥐",
    layout="wide"
)

# API endpoint
API_URL = "http://localhost:8000"

# ==========================================
# HEADER
# ==========================================

st.title("🥐 FreshCast AI")
st.markdown("### AI-Powered Demand Forecasting for Your Bakery")
st.markdown("---")

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("📊 Quick Stats")

try:
    # Get summary data
    response = requests.get(f"{API_URL}/summary?days_ahead=7")
    if response.status_code == 200:
        summary_data = response.json()
        products_df = pd.DataFrame(summary_data['products'])
        
        total_production = products_df['total_production'].sum()
        total_demand = products_df['total_demand'].sum()
        
        st.sidebar.metric("Total Weekly Production", f"{int(total_production)} units")
        st.sidebar.metric("Total Weekly Demand", f"{int(total_demand)} units")
        st.sidebar.metric("Products Tracked", len(products_df))
    else:
        st.sidebar.warning("⚠️ Could not connect to API")
except:
    st.sidebar.error("❌ API not running. Start with: `python src/api/main.py`")

st.sidebar.markdown("---")
st.sidebar.markdown("**💡 Business Impact**")
st.sidebar.info("Reduce waste by 30%\nIncrease profit by 5-10%")

# ==========================================
# MAIN CONTENT
# ==========================================

# Tab navigation
tab1, tab2, tab3, tab4 = st.tabs(["💬 Ask Questions", "📊 Production Forecast", "📦 Raw Materials", "📈 Analytics"])

# ==========================================
# TAB 1: Question Interface
# ==========================================

with tab1:
    st.header("Ask FreshCast AI")
    st.markdown("Ask any question about your bakery operations!")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_question = st.text_input(
            "Your Question:",
            placeholder="e.g., How many sandwiches do we need for next week?"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    if ask_button and user_question:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": user_question}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display answer
                    st.success("✅ Answer:")
                    st.markdown(f"**{result['answer']}**")
                    
                    # Show metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Query Type", result['query_type'])
                    with col2:
                        st.metric("Confidence", f"{result['confidence']*100:.0f}%")
                    with col3:
                        sources = []
                        if result['used_ml']:
                            sources.append("ML Model")
                        if result['used_llm']:
                            sources.append("LLM")
                        st.metric("Source", " + ".join(sources))
                else:
                    st.error("❌ Error getting response")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Example questions
    st.markdown("---")
    st.markdown("**💡 Try these questions:**")
    examples = [
        "How many croissants do we need for next week?",
        "What raw materials should I order?",
        "Show me production needs for all products",
        "How many donuts for tomorrow?",
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            st.code(example, language=None)

# ==========================================
# TAB 2: Production Forecast
# ==========================================

with tab2:
    st.header("📊 7-Day Production Forecast")
    
    try:
        response = requests.get(f"{API_URL}/summary?days_ahead=7")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['products'])
            
            # Chart
            fig = px.bar(
                df,
                x='product',
                y=['total_demand', 'total_production'],
                title='Weekly Demand vs Production',
                barmode='group',
                labels={'value': 'Units', 'variable': 'Metric'},
                color_discrete_map={'total_demand': '#FF6B6B', 'total_production': '#4ECDC4'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.markdown("### Detailed Breakdown")
            st.dataframe(
                df.style.format({
                    'total_demand': '{:.0f}',
                    'total_production': '{:.0f}',
                    'daily_average': '{:.1f}'
                }),
                use_container_width=True
            )
        else:
            st.error("Could not load forecast data")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==========================================
# TAB 3: Raw Materials
# ==========================================

with tab3:
    st.header("📦 Raw Material Requirements")
    
    days = st.slider("Forecast Period (days)", 1, 30, 7)
    
    try:
        response = requests.get(f"{API_URL}/materials?days_ahead={days}")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data['materials'])
            
            # Chart
            fig = px.bar(
                df,
                x='material',
                y='quantity_kg',
                title=f'Raw Materials Needed (Next {days} Days)',
                labels={'quantity_kg': 'Quantity (kg)', 'material': 'Material'},
                color='quantity_kg',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Shopping list
            st.markdown("### 🛒 Shopping List")
            for _, row in df.iterrows():
                st.markdown(f"- **{row['material'].title()}**: {row['quantity_kg']} kg")
        else:
            st.error("Could not load materials data")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# ==========================================
# TAB 4: Analytics
# ==========================================

with tab4:
    st.header("📈 Business Analytics")
    
    # Load historical data
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        df_train = pd.read_csv('../data/processed/train_data.csv')
        df_train['date'] = pd.to_datetime(df_train['date'])
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_revenue = df_train['revenue'].sum()
        total_waste_cost = df_train['waste_cost'].sum()
        avg_service_level = df_train['service_level'].mean()
        waste_rate = (df_train['waste'].sum() / df_train['production'].sum() * 100)
        
        with col1:
            st.metric("Total Revenue", f"${total_revenue:,.0f}")
        with col2:
            st.metric("Waste Cost", f"${total_waste_cost:,.0f}")
        with col3:
            st.metric("Service Level", f"{avg_service_level:.1f}%")
        with col4:
            st.metric("Waste Rate", f"{waste_rate:.1f}%")
        
        # Business Impact
        st.markdown("---")
        st.markdown("### 💰 Potential Business Impact")
        
        waste_savings = total_waste_cost * 0.3  # 30% reduction
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"""
            **With FreshCast AI:**
            - Reduce waste by 30%: **${waste_savings:,.0f}/year savings**
            - Improve service level to 99%
            - Optimize inventory levels
            """)
        
        with col2:
            st.success(f"""
            **ROI Calculation:**
            - Implementation cost: ~$1,000
            - Annual savings: ${waste_savings:,.0f}
            - Payback period: **<1 month**
            - ROI: **{(waste_savings/1000)*100:.0f}%**
            """)
        
    except Exception as e:
        st.error(f"Could not load analytics: {str(e)}")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
    <p>🥐 FreshCast AI v1.0.0 | Built with Prophet, FastAPI & Streamlit</p>
    <p>Helping small bakeries reduce waste and optimize production</p>
    </div>
    """,
    unsafe_allow_html=True
)