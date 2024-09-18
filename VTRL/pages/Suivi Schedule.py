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
    # Normalize the confirmation value to lowercase
    confirmation = row['confirmation'].strip().lower()
    
    if confirmation in ['yes', 'oui', 'Yes', 'Oui', 'ok', 'Confirmed','YES']:
        color = 'background-color: lightgreen;'  # Green for confirmations
    elif confirmation in ['no', 'non', 'No','NN','nn','Non']:
        color = 'background-color: lightcoral;'  # Red for rejections
    elif confirmation == 'sent':
        color = 'background-color: lightgray;'  # Gray for 'sent'
    else:
        color = ''  # No color for other statuses or empty values
    
    return [color] * len(row)  # Apply the color to the entire row


# Apply the styling function to the DataFrame
styled_df = df.style.apply(color_confirmation, axis=1)

# Display the styled DataFrame in Streamlit
st.dataframe(styled_df)
