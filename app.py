import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

# Load API keys securely for Streamlit Cloud
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("🚨 Google API key is missing! Please add GOOGLE_API_KEY in Streamlit Cloud secrets.")
    st.stop()
if "GOOGLE_MAPS_API_KEY" not in st.secrets:
    st.error("🚨 Maps API key is missing! Please add GOOGLE_MAPS_API_KEY in Streamlit Cloud secrets.")
    st.stop()

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]

# Configure LangChain's Google GenAI model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
memory = ConversationBufferMemory()

# Prompt Template (unchanged)
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a travel assistant providing detailed travel options."),
    ("human", """Find travel options from {source} to {destination} for {travel_date}. 
    Include details for cab, train, bus, and flights with estimated costs in USD, travel time, 
    and emphasize eco-friendly alternatives (e.g., carbon offsets, electric vehicles, renewable energy use). 
    If a preferred mode is specified ({mode}), prioritize it. If a budget is provided ({budget} USD), 
    tailor recommendations to stay within it.""")
])

# Function to get travel options with caching
@st.cache_data
def get_travel_options(source, destination, travel_date, mode="Any", budget=None):
    try:
        prior_context = memory.load_memory_variables({})
        context_str = prior_context.get("history", "")
        
        prompt = prompt_template.format_messages(
            source=source, 
            destination=destination, 
            travel_date=travel_date, 
            mode=mode,
            budget=budget if budget else "not specified"
        )
        
        response = chat_model.invoke(prompt)
        memory.save_context(
            {"user": f"{source} to {destination} on {travel_date}, mode: {mode}, budget: {budget}"}, 
            {"AI": response.content}
        )
        return response.content
    except Exception as e:
        if "API key" in str(e):
            return "⚠️ Invalid or missing Google API key. Check your Streamlit Cloud secrets."
        elif "rate limit" in str(e):
            return "⚠️ Rate limit exceeded. Try again later."
        else:
            return f"⚠️ Error fetching travel options: {str(e)}"

# Function to generate a Google Maps embed URL with separate Maps API key
def get_map_url(source, destination):
    base_url = "https://www.google.com/maps/embed/v1/directions"
    params = f"?key={GOOGLE_MAPS_API_KEY}&origin={source}&destination={destination}&mode=driving"
    return f"{base_url}{params}"

# Streamlit UI
def main():
    st.title("🚀 AI-Powered Travel Planner")
    st.write("Enter your travel details below to get recommendations!")

    # Initialize session state for saved trips
    if "saved_trips" not in st.session_state:
        st.session_state.saved_trips = []

    # Input Fields
    col1, col2 = st.columns(2)
    with col1:
        source = st.text_input("Source", placeholder="e.g., San Francisco")
    with col2:
        destination = st.text_input("Destination", placeholder="e.g., Los Angeles")

    travel_date = st.date_input("Select Travel Date")
    mode = st.selectbox("Preferred Mode of Transport", ["Any", "Flight", "Train", "Bus", "Cab"])
    budget = st.number_input("Budget (USD)", min_value=0, value=0, step=10, help="Set to 0 for no budget limit")

    # Fetch Travel Options
    if st.button("Get Travel Options"):
        if source and destination:
            with st.spinner("Fetching travel options..."):
                budget_value = budget if budget > 0 else None
                result = get_travel_options(source, destination, travel_date, mode, budget_value)
                st.subheader("📌 Travel Recommendations")
                st.markdown(result)

                # Save Trip Option
                trip_details = {
                    "source": source,
                    "destination": destination,
                    "date": str(travel_date),
                    "mode": mode,
                    "budget": budget_value,
                    "result": result
                }
                if st.button("Save This Trip"):
                    st.session_state.saved_trips.append(trip_details)
                    st.success("Trip saved!")

                # Display Map with separate Maps API key
                st.subheader("🗺️ Route Map")
                map_url = get_map_url(source, destination)
                st.components.v1.iframe(map_url, height=400)

        else:
            st.error("❌ Please enter both source and destination.")

    # Display Saved Trips
    if st.session_state.saved_trips:
        st.subheader("💾 Saved Trips")
        for i, trip in enumerate(st.session_state.saved_trips):
            with st.expander(f"Trip {i+1}: {trip['source']} to {trip['destination']} on {trip['date']}"):
                st.write(f"Mode: {trip['mode']}")
                st.write(f"Budget: ${trip['budget'] if trip['budget'] else 'Not specified'}")
                st.markdown(trip["result"])

if __name__ == "__main__":
    main()
