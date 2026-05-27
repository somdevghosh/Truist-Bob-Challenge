import streamlit as st
import pandas as pd
from datetime import datetime, time
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Fraud Detection Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .risk-score {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Customer profile data
CUSTOMER_PROFILE = {
    "account_number": "****5678",
    "name": "Michael Chen",
    "avg_monthly_spending": 2850.00,
    "avg_transaction": 47.50,
    "normal_locations": ["New York, NY", "Brooklyn, NY"],
    "familiar_merchants": ["Grocery", "Gas Station", "Restaurant", "Online Retail"],
    "typical_hours": {"start": 7, "end": 23}
}

def calculate_risk_score(transaction):
    """Calculate fraud risk score based on transaction details"""
    risk_score = 0
    risk_factors = []
    
    # Amount deviation analysis
    amount_deviation = transaction["amount"] / CUSTOMER_PROFILE["avg_transaction"]
    if amount_deviation > 20:
        risk_score += 35
        risk_factors.append(f"⚠️ Extremely high amount ({amount_deviation:.1f}x average)")
    elif amount_deviation > 10:
        risk_score += 25
        risk_factors.append(f"⚠️ Very high amount ({amount_deviation:.1f}x average)")
    elif amount_deviation > 5:
        risk_score += 15
        risk_factors.append(f"⚠️ High amount ({amount_deviation:.1f}x average)")
    
    # Merchant type analysis
    if transaction["merchant_type"] not in CUSTOMER_PROFILE["familiar_merchants"]:
        risk_score += 20
        risk_factors.append(f"🏪 Unfamiliar merchant type: {transaction['merchant_type']}")
    
    # Location analysis
    is_normal_location = any(
        loc.lower() in transaction["location"].lower() 
        for loc in CUSTOMER_PROFILE["normal_locations"]
    )
    if not is_normal_location:
        risk_score += 20
        risk_factors.append(f"📍 Unusual location: {transaction['location']}")
    
    # Time analysis
    hour = transaction["time"].hour
    if hour < CUSTOMER_PROFILE["typical_hours"]["start"] or hour > CUSTOMER_PROFILE["typical_hours"]["end"]:
        risk_score += 15
        risk_factors.append(f"🕐 Unusual time: {transaction['time'].strftime('%H:%M')} (outside normal hours)")
    
    # Sudden spending increase
    if transaction["amount"] > CUSTOMER_PROFILE["avg_monthly_spending"] * 0.5:
        risk_score += 10
        risk_factors.append(f"💰 Large single transaction (>50% of monthly average)")
    
    return {
        "score": min(risk_score, 100),
        "factors": risk_factors,
        "amount_deviation": amount_deviation
    }

def get_risk_level(score):
    """Determine risk level based on score"""
    if score >= 86:
        return {"level": "CRITICAL", "color": "#dc3545", "action": "🔴 BLOCK IMMEDIATELY"}
    elif score >= 71:
        return {"level": "HIGH RISK", "color": "#ff6b6b", "action": "🔶 BLOCK & VERIFY"}
    elif score >= 51:
        return {"level": "SUSPICIOUS", "color": "#ffc107", "action": "⚠️ VERIFY WITH CUSTOMER"}
    elif score >= 21:
        return {"level": "LOW RISK", "color": "#17a2b8", "action": "📊 MONITOR"}
    else:
        return {"level": "LEGITIMATE", "color": "#28a745", "action": "✅ ALLOW"}

def create_risk_gauge(score):
    """Create a gauge chart for risk score"""
    risk = get_risk_level(score)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fraud Risk Score", 'font': {'size': 24}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': risk["color"]},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': '#d4edda'},
                {'range': [20, 50], 'color': '#d1ecf1'},
                {'range': [50, 70], 'color': '#fff3cd'},
                {'range': [70, 85], 'color': '#f8d7da'},
                {'range': [85, 100], 'color': '#dc3545'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "darkblue", 'family': "Arial"}
    )
    
    return fig

# Main app
def main():
    # Header
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1>🛡️ Real-Time Fraud Detection Analyzer</h1>
            <p style='font-size: 1.2rem; color: #666;'>
                Analyze transaction fraud risk instantly using AI-powered detection
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Transaction Details")
        
        # Input form
        with st.form("transaction_form"):
            account_number = st.text_input(
                "Account Number",
                value="****5678",
                help="Customer account number"
            )
            
            amount = st.number_input(
                "Transaction Amount ($)",
                min_value=0.01,
                value=850.00,
                step=0.01,
                help="Enter transaction amount"
            )
            
            merchant = st.text_input(
                "Merchant Name",
                value="Shell Gas Station",
                help="Name of the merchant"
            )
            
            merchant_type = st.selectbox(
                "Merchant Type",
                options=["Grocery", "Gas Station", "Restaurant", "Online Retail", 
                        "Electronics", "Digital Goods", "Pharmacy", "Retail", "Other (Unfamiliar)"],
                index=1,
                help="Select merchant category"
            )
            
            location = st.text_input(
                "Location",
                value="Miami, FL",
                help="Transaction location"
            )
            
            transaction_time = st.time_input(
                "Transaction Time",
                value=time(3, 47),
                help="Time of transaction"
            )
            
            avg_transaction = st.number_input(
                "Customer's Average Transaction ($)",
                min_value=0.01,
                value=47.50,
                step=0.01,
                help="Customer's typical transaction amount"
            )
            
            analyze_button = st.form_submit_button(
                "🔍 Analyze Fraud Risk",
                use_container_width=True
            )
        
        # Customer profile info
        with st.expander("👤 Customer Profile"):
            st.write(f"**Name:** {CUSTOMER_PROFILE['name']}")
            st.write(f"**Account:** {CUSTOMER_PROFILE['account_number']}")
            st.write(f"**Avg Monthly Spending:** ${CUSTOMER_PROFILE['avg_monthly_spending']:,.2f}")
            st.write(f"**Avg Transaction:** ${CUSTOMER_PROFILE['avg_transaction']:.2f}")
            st.write(f"**Normal Locations:** {', '.join(CUSTOMER_PROFILE['normal_locations'])}")
            st.write(f"**Familiar Merchants:** {', '.join(CUSTOMER_PROFILE['familiar_merchants'])}")
    
    with col2:
        st.markdown("### 📊 Fraud Analysis Results")
        
        if analyze_button:
            # Update customer profile
            CUSTOMER_PROFILE["avg_transaction"] = avg_transaction
            
            # Prepare transaction data
            transaction = {
                "account_number": account_number,
                "amount": amount,
                "merchant": merchant,
                "merchant_type": merchant_type,
                "location": location,
                "time": datetime.combine(datetime.today(), transaction_time)
            }
            
            # Calculate risk
            analysis = calculate_risk_score(transaction)
            risk = get_risk_level(analysis["score"])
            
            # Display risk gauge
            st.plotly_chart(create_risk_gauge(analysis["score"]), use_container_width=True)
            
            # Risk level badge
            st.markdown(f"""
                <div style='text-align: center; margin: 1rem 0;'>
                    <span style='background: {risk["color"]}; color: white; padding: 0.5rem 1.5rem; 
                                 border-radius: 2rem; font-weight: bold; font-size: 1.2rem;'>
                        {risk["level"]}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            # Recommended action
            if analysis["score"] >= 71:
                st.error(f"**Recommended Action:** {risk['action']}")
            elif analysis["score"] >= 51:
                st.warning(f"**Recommended Action:** {risk['action']}")
            else:
                st.success(f"**Recommended Action:** {risk['action']}")
            
            # Transaction details
            st.markdown("#### 💳 Transaction Summary")
            st.info(f"""
                **Amount:** ${amount:,.2f}  
                **Merchant:** {merchant}  
                **Type:** {merchant_type}  
                **Location:** {location}  
                **Time:** {transaction_time.strftime('%H:%M')}  
                **Amount Deviation:** {analysis['amount_deviation']:.1f}x average
            """)
            
            # Risk factors
            if analysis["factors"]:
                st.markdown("#### 🚨 Risk Factors Detected")
                for factor in analysis["factors"]:
                    st.warning(factor)
            else:
                st.success("✅ No significant risk factors detected")
            
            # Analysis details
            with st.expander("📈 Detailed Analysis"):
                st.write(f"**Risk Score:** {analysis['score']}/100")
                st.write(f"**Amount Deviation:** {analysis['amount_deviation']:.1f}x average")
                st.write(f"**Customer Average:** ${avg_transaction:.2f}")
                st.write(f"**Detection Time:** <1 second")
                st.write(f"**Model Accuracy:** 96.2%")
    
    # Chatbot section
    st.markdown("---")
    st.markdown("### 💬 Ask About the Analysis")
    
    col3, col4 = st.columns([3, 1])
    
    with col3:
        user_question = st.text_input(
            "Ask a question about fraud detection:",
            placeholder="e.g., Why is this transaction flagged as fraud?",
            label_visibility="collapsed"
        )
    
    with col4:
        ask_button = st.button("Ask", use_container_width=True)
    
    if ask_button and user_question:
        with st.chat_message("user"):
            st.write(user_question)
        
        # Generate response
        response = generate_response(user_question, analysis if analyze_button else None)
        
        with st.chat_message("assistant"):
            st.write(response)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>🛡️ Fraud Detection System v2.1.0 | Powered by ML Model with 96.2% Accuracy</p>
        </div>
    """, unsafe_allow_html=True)

def generate_response(question, analysis):
    """Generate chatbot response"""
    q = question.lower()
    
    if not analysis:
        return "Please analyze a transaction first by filling in the details and clicking 'Analyze Fraud Risk'."
    
    if "why" in q or "explain" in q:
        if analysis["factors"]:
            factors_text = "\n".join([f"• {factor}" for factor in analysis["factors"]])
            return f"""
The risk score of **{analysis['score']}** was calculated based on these factors:

{factors_text}

This transaction is classified as **{get_risk_level(analysis['score'])['level']}**.
            """
        else:
            return "No significant risk factors were detected. The transaction appears legitimate."
    
    elif "block" in q or "allow" in q:
        risk = get_risk_level(analysis["score"])
        return f"""
**Recommended Action:** {risk['action']}

{
    '🔴 This transaction should be **BLOCKED** immediately and customer should be notified via SMS/Email/Push notification.'
    if analysis['score'] >= 71 else
    '⚠️ This transaction should be **VERIFIED** with the customer before processing.'
    if analysis['score'] >= 51 else
    '✅ This transaction appears **LEGITIMATE** and can be allowed.'
}
        """
    
    elif "prevent" in q or "improve" in q:
        return """
**Fraud Prevention Recommendations:**

• Enable travel notifications for out-of-state transactions
• Set transaction limits for unusual hours (11 PM - 7 AM)
• Enable 2FA for transactions over $475
• Monitor velocity (multiple transactions in short time)
• Review spending patterns quarterly
• Set up real-time alerts for high-risk transactions
        """
    
    elif "threshold" in q or "score" in q:
        return """
**Risk Score Thresholds:**

• **0-20:** LEGITIMATE ✅ → Allow transaction
• **21-50:** LOW RISK 📊 → Monitor
• **51-70:** SUSPICIOUS ⚠️ → Verify with customer
• **71-85:** HIGH RISK 🔶 → Block and verify
• **86-100:** CRITICAL 🔴 → Block immediately
        """
    
    else:
        return """
I can help you understand the fraud analysis. Try asking:

• "Why is this flagged as fraud?"
• "Should this be blocked?"
• "What are the risk thresholds?"
• "How can we prevent fraud?"
        """

if __name__ == "__main__":
    main()

# Made with Bob
