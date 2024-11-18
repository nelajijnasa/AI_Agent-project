import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests
import csv
from io import StringIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
serpapi_key = os.getenv("SERPAPI_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")

# Check if the API keys are set correctly
if not serpapi_key or not groq_api_key:
    st.error("API keys not found! Please ensure your SERPAPI_KEY and GROQ_API_KEY are set correctly in your .env file.")

# Function to search using SerpAPI
def search_google(query):
    search_url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": serpapi_key
    }
    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()  # Ensure we got a successful response
        return response.json()  # Return JSON response
    except requests.exceptions.RequestException as e:
        st.error(f"Error occurred while fetching search results for {query}: {e}")
        return None

# Function to connect to Google Sheets
def connect_google_sheets(sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("your_credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

# Streamlit app
def main():
    st.title("AI Agent Project: Data Search")

    # File upload or Google Sheets connection
    upload_type = st.radio("Choose the data input method", ["Upload CSV/Excel File", "Connect to Google Sheet"])

    if upload_type == "Upload CSV/Excel File":
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])

        if uploaded_file is not None:
            if uploaded_file.name.endswith("csv"):
                data = pd.read_csv(uploaded_file)
            else:
                data = pd.read_excel(uploaded_file)
            st.write("Data preview:", data.head())
            column = st.selectbox("Select column to search", data.columns)

            # After selecting the column, prompt for the related name (search criteria)
            if column:
                related_name = st.text_input(f"Enter the related name/field to search for in '{column}' (e.g., email, address, etc.)")
                
                if related_name:
                    st.write(f"Searching for {related_name} related to '{column}'...")

                    # Use the related name to construct the query template
                    prompt_template = f"Get me the {related_name} of {{company}}"

                    # Limit the number of searches (e.g., 10)
                    max_queries = 10
                    queries_processed = 0
                    results_list = []

                    # Conduct search based on the user input
                    if st.button("Fetch Google Search Results"):
                        for index, row in data.iterrows():
                            if queries_processed >= max_queries:
                                st.warning("Reached the maximum number of searches!")
                                break
                            
                            entity_name = row[column]
                            query = prompt_template.format(company=entity_name)  # Replace placeholder with company name
                            st.write(f"Searching for: {query}")

                            # Call the SerpAPI search function
                            result = search_google(query)

                            if result:
                                if 'organic_results' in result:
                                    for res in result['organic_results']:
                                        st.write(f"Title: {res['title']}")
                                        st.write(f"Link: {res['link']}")
                                        st.write(f"Snippet: {res['snippet']}")
                                        results_list.append([res['title'], res['link'], res['snippet']])
                                else:
                                    st.write(f"No results found for {query}.")
                            queries_processed += 1

                        # Save the results to a CSV file
                        if results_list:
                            output = StringIO()
                            writer = csv.writer(output)
                            writer.writerow(['Title', 'Link', 'Snippet'])
                            writer.writerows(results_list)
                            output.seek(0)

                            st.download_button(
                                label="Download Search Results as CSV",
                                data=output.getvalue(),
                                file_name="search_results.csv",
                                mime="text/csv"
                            )

    elif upload_type == "Connect to Google Sheet":
        sheet_name = st.text_input("Enter Google Sheet Name")
        if sheet_name:
            try:
                sheet = connect_google_sheets(sheet_name)
                data = pd.DataFrame(sheet.get_all_records())
                st.write("Data preview:", data.head())
                column = st.selectbox("Select column to search", data.columns)

                # After selecting the column, prompt for the related name (search criteria)
                if column:
                    related_name = st.text_input(f"Enter the related name/field to search for in '{column}' (e.g., email, address, etc.)")
                    
                    if related_name:
                        st.write(f"Searching for {related_name} related to '{column}'...")

                        # Use the related name to construct the query template
                        prompt_template = f"Get me the {related_name} of {{company}}"

                        # Limit the number of searches (e.g., 10)
                        max_queries = 10
                        queries_processed = 0
                        results_list = []

                        # Conduct search based on the user input
                        if st.button("Fetch Google Search Results"):
                            for index, row in data.iterrows():
                                if queries_processed >= max_queries:
                                    st.warning("Reached the maximum number of searches!")
                                    break
                                
                                entity_name = row[column]
                                query = prompt_template.format(company=entity_name)  # Replace placeholder with company name
                                st.write(f"Searching for: {query}")

                                # Call the SerpAPI search function
                                result = search_google(query)

                                if result:
                                    if 'organic_results' in result:
                                        for res in result['organic_results']:
                                            st.write(f"Title: {res['title']}")
                                            st.write(f"Link: {res['link']}")
                                            st.write(f"Snippet: {res['snippet']}")
                                            results_list.append([res['title'], res['link'], res['snippet']])
                                    else:
                                        st.write(f"No results found for {query}.")
                                queries_processed += 1

                            # Save the results to a CSV file
                            if results_list:
                                output = StringIO()
                                writer = csv.writer(output)
                                writer.writerow(['Title', 'Link', 'Snippet'])
                                writer.writerows(results_list)
                                output.seek(0)

                                st.download_button(
                                    label="Download Search Results as CSV",
                                    data=output.getvalue(),
                                    file_name="search_results.csv",
                                    mime="text/csv"
                                )
            except Exception as e:
                st.error(f"Error connecting to Google Sheet: {e}")
                return

if __name__ == "__main__":
    main()
