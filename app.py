import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

# Load API key securely
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("🚨 API key is missing! Please add GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Configure LangChain's Google GenAI model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
memory = ConversationBufferMemory()  # Optional: To track user queries

# Improved LangChain Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a travel assistant providing detailed travel options."),
    ("human", """Find travel options from {source} to {destination}. 
    Include details for cab, train, bus, and flights with estimated costs in USD, travel time, 
    and eco-friendly alternatives if available.""")
])

# Function to get travel options with caching
@st.cache_data
def get_travel_options(source, destination):
    try:
        prompt = prompt_template.format_messages(source=source, destination=destination)
        response = chat_model.invoke(prompt)
        memory.save_context({"user": f"{source} to {destination}"}, {"AI": response.content})
        return response.content
    except Exception as e:
        return f"⚠️ Error fetching travel options: {str(e)}"

# Streamlit UI
def main():
    st.title("🚀 AI-Powered Travel Planner")
    st.write("Enter your travel details below to get recommendations!")

    # Input Fields
    col1, col2 = st.columns(2)
    with col1:
        source = st.text_input("Source", placeholder="e.g., New York")
    with col2:
        destination = st.text_input("Destination", placeholder="e.g., Boston")

    travel_date = st.date_input("Select Travel Date")
    mode = st.selectbox("Preferred Mode of Transport", ["Any", "Flight", "Train", "Bus", "Cab"])

    # Fetch Travel Options
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
