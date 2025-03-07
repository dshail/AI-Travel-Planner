import streamlit as st
import google.generativeai as genai
import os
import json
import urllib.parse

# Configure API Key (Ensure it's set in Streamlit Secrets)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Google API key is missing. Set the 'GOOGLE_API_KEY' environment variable.")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-1.5-pro')

# Define function to fetch travel recommendations
def get_travel_options(source, destination):
    prompt = f"""
    You are a travel assistant. Provide structured travel options from {source} to {destination}.
    Include these modes: Cab, Train, Bus, Flight.
    Return a JSON response with:
    - mode: (string) Transport mode
    - cost: (float) Estimated cost in USD
    - duration: (string) Approximate travel time

    Example response:
    [
        {{"mode": "Cab", "cost": 120, "duration": "3 hours"}},
        {{"mode": "Train", "cost": 45, "duration": "2.5 hours"}},
        {{"mode": "Bus", "cost": 30, "duration": "3.5 hours"}},
        {{"mode": "Flight", "cost": 150, "duration": "1 hour"}}
    ]
    """
    
    try:
        response = model.generate_content(prompt)
        travel_data = json.loads(response.text)
        return travel_data
    except Exception as e:
        return [{"mode": "Error", "cost": 0, "duration": str(e)}]

# 🎨 Streamlit UI Enhancements
st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="wide")

st.title("🚀 AI-Powered Travel Planner")
st.write("Plan your trip smartly with AI recommendations! 🌍")

# ✅ Organized layout
col1, col2 = st.columns(2)
with col1:
    source = st.text_input("🛫 Source", placeholder="e.g., New York")
with col2:
    destination = st.text_input("🏙 Destination", placeholder="e.g., Boston")

# 🔗 Show Google Maps Route
if source and destination:
    map_url = f"https://www.google.com/maps/dir/{source}/{destination}"
    st.markdown(f"[🌍 View Route on Google Maps]({map_url})", unsafe_allow_html=True)

# 📌 Travel Mode Preference Poll
travel_preference = st.radio(
    "Which mode of travel do you prefer?",
    ["🚗 Cab", "🚆 Train", "🚌 Bus", "✈️ Flight"]
)
st.write(f"Great choice! {travel_preference} is a convenient option. 🚀")

# 🚀 Get Travel Options
result = []
if st.button("Get Travel Options"):
    if source and destination:
        with st.spinner("Fetching travel options..."):
            result = get_travel_options(source, destination)

            if result:
                st.subheader("🛎 Travel Recommendations")
                travel_summary = ""

                for option in result:
                    travel_summary += f"🚀 **{option['mode']}** - ${option['cost']} | {option['duration']}\n"
                    st.markdown(f"**Mode:** {option['mode']} | **Cost:** ${option['cost']} | **Duration:** {option['duration']}")

                # 🎯 Budget-Based Suggestions
                budget = st.slider("💰 Set Your Budget (USD)", 10, 500, 100)
                filtered_options = [opt for opt in result if opt["cost"] <= budget]
                
                if filtered_options:
                    st.subheader("✅ Travel Options Within Your Budget:")
                    for opt in filtered_options:
                        st.markdown(f"💲 **{opt['mode']}** - ${opt['cost']} ({opt['duration']})")
                else:
                    st.warning("No options available within this budget. Try increasing it!")

                # 📢 Share on Social Media
                share_text = f"Planning a trip from {source} to {destination}? Here are AI-powered travel options:\n\n{travel_summary}\nPlan smartly: https://your-app-url"
                encoded_text = urllib.parse.quote(share_text)
                whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"

                # Display shareable link
                st.subheader("📲 Share Your Trip:")
                st.markdown(f"[📢 Share on WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

    else:
        st.error("Please enter both source and destination. 🚨")

# 🌎 Fun Travel Quiz
st.subheader("🌎 Travel Quiz: Where Should You Go?")
q1 = st.radio("Which continent do you want to explore?", ["Asia", "Europe", "North America", "Other"])
q2 = st.radio("What's your travel style?", ["Adventure", "Luxury", "Budget", "Road Trip"])

if q1 == "Europe" and q2 == "Luxury":
    st.write("💎 You should visit **Paris** or **Rome** for a luxury experience!")
elif q1 == "Asia" and q2 == "Adventure":
    st.write("🌄 Try trekking in the **Himalayas** or diving in **Bali**!")
else:
    st.write("🌍 There’s a perfect destination for everyone! Keep exploring. 🚀")

st.success("🎉 Enjoy your trip planning with AI-powered recommendations!")
