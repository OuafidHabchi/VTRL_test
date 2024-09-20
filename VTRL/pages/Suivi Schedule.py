import streamlit as st
import pandas as pd

# Replace this URL with your own Google Sheet URL
sheet_url = "https://docs.google.com/spreadsheets/d/14dZqtAclmYsudVHV7mlIbXyM2wSwcu55KhwCOm9_Bv8/gviz/tq?tqx=out:csv"

# Read the CSV data from the Google Sheet
df = pd.read_csv(sheet_url)

# Display the actual column names in the DataFrame to check for mismatches
st.write("Columns in the DataFrame:", df.columns.tolist())

# Strip any leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Now ensure only the specific columns are displayed: 'nom', 'cycle', 'confirmation', 'tel'
expected_columns = ['nom', 'cycle', 'confirmation', 'tel']

# Filter out the columns that actually exist in the DataFrame
existing_columns = [col for col in expected_columns if col in df.columns]

# If there are missing columns, display an error
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns: {missing_columns}")

# Select only the columns that exist in the DataFrame
df = df[existing_columns]

# Display the title of the app
st.title("Employee Data from Google Sheets (Selected Columns Only)")

# Function to determine if the response is positive
def is_positive_response(response):
    positive_responses = {"yes", "oui", "y", "confirmed", "ok"}  # Add more variations if needed
    return str(response).strip().lower() in positive_responses

# Function to assign color based on the 'cycle' if 'confirmation' is 'sent'
def get_shift_color(row):
    if 'cycle' in row:  # Ensure 'cycle' column exists
        cycle = row['cycle']
        if "Cycle 0" in cycle:
             return 'background-color: lightblue;'  # Light blue for Cycle 0
        elif "Cycle 1 (w1)" in cycle:
            return 'background-color: #ffff99;'  # Lighter yellow for Cycle 1 (w1)v
        elif "Cycle 1 (w2)" in cycle:
            return 'background-color: #ffd700;'  # Darker yellow (gold) for Cycle 1 (w2)
        elif "Cycle 2" in cycle:
           return 'background-color: #dda0dd;'  # Mauve-like color for Cycle 2 (Plum)
        elif "Flex" in cycle:
            return 'background-color: #9370DB;'  # Medium purple for evening shift (Flex)
        elif "Cancelled" in cycle:
            return 'background-color: lightgray;'  # Gray for Cancelled Shift
    return 'background-color: white;'  # Default color if no specific cycle color is found

# Define a function to apply custom CSS styles based on the 'confirmation' status and responses
def color_confirmation(row):
    response = row['confirmation'].strip().lower() if 'confirmation' in row else 'unknown'
    
    if is_positive_response(response):
        color = 'background-color: lightgreen;'  # Green for positive responses (Yes, Oui, etc.)
    elif response == 'sent':
        # Color based on cycle type if confirmation is 'sent'
        color = get_shift_color(row)
    else:
        color = 'background-color: lightcoral;'  # Red for negative or unknown responses
    
    return [color] * len(row)  # Apply the color to the entire row

# Apply the styling function to the DataFrame
styled_df = df.style.apply(color_confirmation, axis=1)

# Display the styled DataFrame in Streamlit
st.dataframe(styled_df)
