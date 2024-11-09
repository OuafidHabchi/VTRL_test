import streamlit as st
import pandas as pd
from datetime import datetime

# Get the current date
current_date = datetime.now().strftime("%Y-%m-%d")

# URL of the published Google Sheet in CSV format
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN_TY54FgOENRgPn5SPsn0GWVCUovoQt5yZhhvJjZW8WtEIseWNeotcqRTfVIcFoZgYHFA4qlcYVyD/pub?gid=1218607264&single=true&output=csv"

# Read the CSV data starting from row 12 (header=11)
try:
    df = pd.read_csv(sheet_url, header=11)
    st.write("Data Preview:", df.head())  # Display a preview to check if data is loaded correctly
except Exception as e:
    st.error("Failed to load data. Please check the sheet URL or format.")
    st.stop()

# Display the app title with the current date
st.title(f"VTRL - {current_date}")

# Expected columns
columns_to_display = ['NAME', 'SHIFT', 'CONFIRM']

# Check for missing columns
missing_columns = [col for col in columns_to_display if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns: {missing_columns}")
    st.stop()

# Clean the 'SHIFT' column and fill empty values in 'CONFIRM'
df['SHIFT'] = df['SHIFT'].fillna('').str.strip()
df['CONFIRM'] = df.get('CONFIRM', '')

# Function to color rows based on conditions
def color_row(row):
    if row['CONFIRM'] == 'TO CANCEL':
        return ['background-color: yellow'] * len(row)
    if row['SHIFT'] == 'CUT':
        return ['background-color: lightcoral'] * len(row)
    if row['SHIFT'] == 'CALL-OFF':
        return ['background-color: orange'] * len(row)
    if row['CONFIRM'] == 'CONFIRMED':
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

# Filter data by shifts
shift_tables = {
    "Cycle 0": df[df['SHIFT'].str.contains("Cycle 0", na=False)],
    "Cycle 1 (W1)": df[df['SHIFT'].str.contains("Cycle 1 \\(W1\\)", na=False)],
    "Cycle 1 (W2)": df[df['SHIFT'].str.contains("Cycle 1 \\(W2\\)", na=False)],
    "Flex": df[df['SHIFT'].str.contains("Flex", na=False)],
    "Crashsort": df[df['SHIFT'].str.contains("Crashsort", na=False)],
    "STANDBY": df[df['SHIFT'].str.contains("STANDBY", na=False)],
    "CUT": df[df['SHIFT'].str.contains("CUT", na=False)],
    "Dispatch (Jour)": df[df['SHIFT'].str.contains("Dispatch \\(Jour\\)", na=False)],
    "Dispatch (Soir)": df[df['SHIFT'].str.contains("Dispatch \\(Soir\\)", na=False)],
    "CALL-OFF": df[df['SHIFT'].str.contains("CALL-OFF", na=False)],
    "Entretien": df[df['SHIFT'].str.contains("Entretien", na=False)]
}

# Display tables with title and count
for title, data in shift_tables.items():
    if not data.empty:
        count = data['NAME'].nunique()
        st.subheader(f"{title} ({count} DAs)")
        st.dataframe(data[columns_to_display].style.apply(color_row, axis=1))
    else:
        st.subheader(title)
        st.write("No data found for this shift.")
