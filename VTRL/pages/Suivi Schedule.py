import streamlit as st
import pandas as pd

# Replace this URL with your own Google Sheet URL (after modifying it as explained)
sheet_url = "https://docs.google.com/spreadsheets/d/14dZqtAclmYsudVHV7mlIbXyM2wSwcu55KhwCOm9_Bv8/gviz/tq?tqx=out:csv"

# Read the CSV data from the Google Sheet
df = pd.read_csv(sheet_url)

# Display the title of the app
st.title("Employee Data from Google Sheets")

# Define a function to apply custom CSS styles based on the 'confirmation' status
def color_confirmation(row):
    if row['confirmation'] == 'Yes':
        color = 'background-color: lightgreen;'
    elif row['confirmation'] == 'NO':
        color = 'background-color: lightcoral;'
    elif row['confirmation'] == 'sent':
        color = 'background-color: lightgray;'
    else:
        color = ''  # No color for other statuses
    return [color] * len(row)  # Apply the color to the entire row

# Apply the styling function to the DataFrame
styled_df = df.style.apply(color_confirmation, axis=1)

# Display the styled DataFrame in Streamlit
st.dataframe(styled_df)
