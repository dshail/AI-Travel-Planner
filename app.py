import streamlit as st
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import AIMessage, HumanMessage
from langchain.memory import ConversationBufferMemory

# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("API key is missing! Add GOOGLE_API_KEY in Streamlit secrets.")
    st.stop()

# Configure LangChain's Google GenAI model
chat_model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)
memory = ConversationBufferMemory()  # Optional: To track user queries

# LangChain Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a travel assistant providing optimal travel options."),
    ("human", "Find travel options from {source} to {destination}. Provide details for cab, train, bus, and flights. Include estimated costs in USD.")
])

# Function to get travel options using LangChain
def get_travel_options(source, destination):
    try:
        # Format prompt with user input
        prompt = prompt_template.format_messages(source=source, destination=destination)
        
        # Get response from LangChain model
        response = chat_model.invoke(prompt)
        
        # Store conversation in memory (optional)
        memory.save_context({"user": f"{source} to {destination}"}, {"AI": response.content})
        
        return response.content
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
