import streamlit as st
import pandas as pd
from datetime import datetime

# Get current date
current_date = datetime.now().strftime("%Y-%m-%d")

# URL of the Google Sheet published as CSV (update if needed)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN_TY54FgOENRgPn5SPsn0GWVCUovoQt5yZhhvJjZW8WtEIseWNeotcqRTfVIcFoZgYHFA4qlcYVyD/pub?gid=1218607264&single=true&output=csv"

# Load CSV data from row 13 (adjust if this isn't correct)
df = pd.read_csv(sheet_url, header=13)

# Display the application's title with today's date
st.title(f"VTRL - {current_date}")

# Verify that the DataFrame has the expected columns
columns_to_display = ['NAME', 'SHIFT', 'CONFIRM']
missing_columns = [col for col in columns_to_display if col not in df.columns]

# Check for missing columns and display an error if any
if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
else:
    # Clean up 'SHIFT' and 'CONFIRM' columns if they exist
    df['SHIFT'] = df['SHIFT'].fillna('').str.strip() if 'SHIFT' in df.columns else ''
    df['CONFIRM'] = df['CONFIRM'].fillna('').str.strip() if 'CONFIRM' in df.columns else ''

    # Define color-coding function for DataFrame rows
    def color_row(row):
        # Define color rules based on 'SHIFT' and 'CONFIRM' values
        if row['CONFIRM'] == 'TO CANCEL':
            return ['background-color: yellow'] * len(row)
        elif row['SHIFT'] == 'CUT':
            return ['background-color: lightcoral'] * len(row)
        elif row['SHIFT'] == 'CALL-OFF':
            return ['background-color: orange'] * len(row)
        elif row['CONFIRM'] == 'CONFIRMED':
            if 'Cycle 1 (W1)' in row['SHIFT']:
                return ['background-color: lightgreen'] * len(row)
            elif 'Cycle 1 (W2)' in row['SHIFT']:
                return ['background-color: lightblue'] * len(row)
            elif 'Cycle 0' in row['SHIFT']:
                return ['background-color: lightcyan'] * len(row)
            elif 'Flex' in row['SHIFT']:
                return ['background-color: pink'] * len(row)
            elif 'Crashsort' in row['SHIFT']:
                return ['background-color: deepskyblue'] * len(row)
            elif 'STANDBY' in row['SHIFT']:
                return ['background-color: lightyellow'] * len(row)
            elif 'Dispatch (Jour)' in row['SHIFT']:
                return ['background-color: orange'] * len(row)
            elif 'Dispatch (Soir)' in row['SHIFT']:
                return ['background-color: purple'] * len(row)
            elif 'Entretien' in row['SHIFT']:
                return ['background-color: lightpink'] * len(row)
        return ['background-color: lightgrey'] * len(row)

    # Display the data with color formatting
    st.dataframe(df[columns_to_display].style.apply(color_row, axis=1))
