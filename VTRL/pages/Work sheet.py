import streamlit as st
import pandas as pd
from datetime import datetime

# Get current date
current_date = datetime.now().strftime("%Y-%m-%d")

# URL of the Google Sheet published as CSV
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN_TY54FgOENRgPn5SPsn0GWVCUovoQt5yZhhvJjZW8WtEIseWNeotcqRTfVIcFoZgYHFA4qlcYVyD/pub?gid=1218607264&single=true&output=csv"

# Load the CSV without headers to inspect structure
df = pd.read_csv(sheet_url, header=None)

# Display the title and the initial rows of the DataFrame to inspect
st.title(f"VTRL - {current_date}")
st.write("Initial rows of data (for inspection):")
st.write(df.head(20))  # Display the first 20 rows to understand structure

st.write("Column names (for inspection):", df.columns.tolist())

# Uncomment the following line and adjust the header parameter after identifying the correct header row
# df = pd.read_csv(sheet_url, header=correct_row_number)
