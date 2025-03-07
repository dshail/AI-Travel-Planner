import streamlit as st
import google.generativeai as genai

# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("API key is missing! Add GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

# Configure Google GenAI API key
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the AI model
model = genai.GenerativeModel('gemini-1.5-pro')

# Function to fetch travel recommendations
def get_travel_options(source, destination):
    prompt = f"""
    Provide travel options between {source} and {destination}. Include:
    - Cab
    - Train
    - Bus
    - Flight
    Estimate costs in USD for each mode:
    - Mode: [Mode Name], Estimated Cost: [Cost in USD]
    """
    try:
        response = model.generate_content(prompt)
        return response.text if response else "No response received."
    except Exception as e:
        return f"Error fetching travel options: {str(e)}"

# Streamlit UI
def main():
    st.title("🚀 AI-Powered Travel Planner")
    st.write("Enter your travel details below to get recommendations!")

    source = st.text_input("Source", placeholder="e.g., New York")
    destination = st.text_input("Destination", placeholder="e.g., Boston")

    if st.button("Get Travel Options"):
        if source and destination:
            with st.spinner("Fetching travel options..."):
                result = get_travel_options(source, destination)
                st.subheader("📌 Travel Recommendations")
                st.write(result)
        else:
            st.error("❌ Please enter both source and destination.")

if __name__ == "__main__":
    main()
