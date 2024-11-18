import os
from dotenv import load_dotenv
import streamlit as st
from utils import process_data, save_results
from api_handler import search_google, connect_google_sheets
import pandas as pd

def main():
    st.title("AI Agent Project: Data Search")
    
    # Load environment variables
    load_dotenv()
    
    # Verify API keys
    if not os.getenv("SERPAPI_KEY") or not os.getenv("GROQ_API_KEY"):
        st.error("API keys not found! Please check your .env file.")
        return

    # File upload or Google Sheets connection
    upload_type = st.radio("Choose data input method", 
                          ["Upload CSV/Excel File", "Connect to Google Sheet"])

    if upload_type == "Upload CSV/Excel File":
        process_file_upload()
    else:
        process_google_sheets()

def process_file_upload():
    uploaded_file = st.file_uploader("Upload CSV/Excel file", 
                                   type=["csv", "xlsx"])
    if uploaded_file:
        data = process_data(uploaded_file)
        handle_data_processing(data)

def process_google_sheets():
    sheet_name = st.text_input("Enter Google Sheet Name")
    if sheet_name:
        try:
            sheet = connect_google_sheets(sheet_name)
            data = pd.DataFrame(sheet.get_all_records())
            handle_data_processing(data)
        except Exception as e:
            st.error(f"Error connecting to Google Sheet: {e}")

def handle_data_processing(data):
    st.write("Data preview:", data.head())
    column = st.selectbox("Select column to search", data.columns)
    
    if column:
        related_name = st.text_input("Enter search criteria")
        if related_name and st.button("Fetch Google Search Results"):
            results = search_google(data[column], related_name)
            if results:
                save_results(results)

if __name__ == "__main__":
    main()
