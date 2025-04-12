import streamlit as st
import pandas as pd
from datetime import datetime, date
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

st.sidebar.title("FinSight")
st.sidebar.page_link("app.py", label="Dashboard", icon="📊")
st.sidebar.page_link("pages/upload_receipt.py", label="Upload Receipt", icon="📄")
st.sidebar.page_link("pages/ai_insights.py", label="AI Insights", icon="💡")

st.title("🎓 Smart Spending Insights")

if st.session_state.receipts_data:
    # Create a copy of the items to avoid modifying the original list in session state
    items_serializable = []
    for item in st.session_state.receipts_data:
        item_copy = item.copy()
        if 'Date' in item_copy and isinstance(item_copy['Date'], date):
            item_copy['Date'] = item_copy['Date'].isoformat()
        items_serializable.append(item_copy)

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Analyze these spending items and provide concise, actionable insights in markdown format:
        {json.dumps(items_serializable, indent=2)}

        Format your response as follows:

        # 🔑 Key Insights
        [Provide 2-3 most important points in bullet points]

        # 📊 Spending Patterns
        [3-4 bullet points about spending habits]

        # 💰 Potential Savings
        [3-4 specific areas where money can be saved]

        # 📚 Smart Spending Tips
        [3-4 actionable tips]

        Keep each bullet point extremely concise (max 1 line).
        Total reading time should be under 2.5 minutes.
        Use emojis and markdown formatting for better readability.
        """
        response = model.generate_content(prompt)
        
        # Split the response into sections
        sections = response.text.split('#')
        insights = {}
        
        for section in sections[1:]:  # Skip the first empty split
            if section.strip():
                header, content = section.split('\n', 1)
                insights[header.strip()] = content.strip()
        
        # Create a 2x2 grid layout
        col1, col2 = st.columns(2)
        
        with col1:
            # Key Insights Card
            st.markdown("""
            <div style='background-color: #2b2b2b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #3d3d3d;'>
                <h3 style='color: #ffffff;'>🔑 Key Insights</h3>
                <div style='color: #ffffff; line-height: 1.5;'>{key_insights}</div>
            </div>
            """.format(key_insights=insights.get('🔑 Key Insights', '').replace('\n', '<br>')), unsafe_allow_html=True)
            
            # Spending Patterns Card
            st.markdown("""
            <div style='background-color: #2b2b2b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #3d3d3d;'>
                <h3 style='color: #ffffff;'>📊 Spending Patterns</h3>
                <div style='color: #ffffff; line-height: 1.5;'>{spending_patterns}</div>
            </div>
            """.format(spending_patterns=insights.get('📊 Spending Patterns', '').replace('\n', '<br>')), unsafe_allow_html=True)
        
        with col2:
            # Potential Savings Card
            st.markdown("""
            <div style='background-color: #2b2b2b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #3d3d3d;'>
                <h3 style='color: #ffffff;'>💰 Potential Savings</h3>
                <div style='color: #ffffff; line-height: 1.5;'>{potential_savings}</div>
            </div>
            """.format(potential_savings=insights.get('💰 Potential Savings', '').replace('\n', '<br>')), unsafe_allow_html=True)
            
            # Smart Spending Tips Card
            st.markdown("""
            <div style='background-color: #2b2b2b; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #3d3d3d;'>
                <h3 style='color: #ffffff;'>📚 Smart Spending Tips</h3>
                <div style='color: #ffffff; line-height: 1.5;'>{smart_tips}</div>
            </div>
            """.format(smart_tips=insights.get('📚 Smart Spending Tips', '').replace('\n', '<br>')), unsafe_allow_html=True)
        
        # Add educational tips section
        st.subheader("💡 Quick Tips for Smart Spending")
        st.markdown("""
        - **Track Every Dollar**: Use apps or spreadsheets to monitor spending
        - **Wait 24 Hours**: Avoid impulse buys by waiting a day
        - **Compare Prices**: Always shop around for better deals
        - **Plan Meals**: Reduce food waste and save on groceries
        - **Review Subscriptions**: Cancel unused services monthly
        """)
        
    except Exception as e:
        st.error(f"Error generating insights: {str(e)}")
else:
    st.info("Upload some receipts to get personalized spending insights and learn how to save money!") 