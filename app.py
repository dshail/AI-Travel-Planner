import streamlit as st
import google.generativeai as genai
import os
import json

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
if st.button("Get Travel Options"):
    if source and destination:
        with st.spinner("Fetching travel options..."):
            result = get_travel_options(source, destination)

            if result:
                st.subheader("🛎 Travel Recommendations")
                for option in result:
                    st.markdown(f"**Mode:** {option['mode']} | **Cost:** ${option['cost']} | **Duration:** {option['duration']}")
    else:
        st.error("Please enter both source and destination. 🚨")

st.success("🎉 Enjoy your trip planning with AI-powered recommendations!")
