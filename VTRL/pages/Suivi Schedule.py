import streamlit as st
import pandas as pd
import requests  # For sending data to the API
from datetime import datetime, timedelta

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

# Multiselect for employee selection
st.subheader("Select one or more employees to send a confirmation message:")
selected_employees = st.multiselect(
    "Employees",
    options=df.index,  # Select by index
    format_func=lambda x: f"{df.loc[x, 'Name']} ({df.loc[x, 'ID']})"  # Customize display for dropdown
)

# Dropdown (selectbox) for work shifts
st.subheader("Select a work shift:")
work_shifts = [
    "09:15 AM",
    "09:30 AM",
    "16:00 PM",
]
selected_shift = st.selectbox("Work Shift", work_shifts)

# Button to confirm message sending
if st.button("Send Confirmation"):
    if not selected_employees:
        st.error("Please select at least one employee.")
    else:
        # Prepare data for the selected employees
        selected_data = df.loc[selected_employees, ["Name", "ID", "Phone", "Email"]]
        employee_data = selected_data.to_dict(orient="records")

        # Calculate tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        # Prepare messages and track the confirmation status
        for employee in employee_data:
            name = employee["Name"]
            employee_id = employee["ID"]
            message = (f"CONFIRMATION: {name} (ID: {employee_id}), you are scheduled to work tomorrow ({tomorrow}) at {selected_shift}. "
                       "Please confirm your availability.")

            # Add the message to the employee's data for API submission
            employee['message'] = message

            # Simulate sending the message
            st.info(f"Sending message to {name} (ID: {employee_id})...")
            # Uncomment below for actual API sending, here it's just simulated
            # api_url = "https://your-api-endpoint"  # Replace with actual API URL
            # response = requests.post(api_url, json={"shift": selected_shift, "employee": employee})
            # if response.status_code == 200:
            #     st.success(f"Message successfully sent to {name}.")
            # else:
            #     st.error(f"Error sending message to {name}: {response.status_code}.")

            # For demo purposes, mark the employee as "sent"
            df.loc[df['ID'] == employee_id, 'confirmation'] = 'sent'

        # Reapply the styling after updates
        styled_df = df.style.apply(color_confirmation, axis=1)
        st.dataframe(styled_df)
