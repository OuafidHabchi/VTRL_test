import streamlit as st
import pandas as pd
import requests  # For sending data to the API
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_name = "employes"

# Fetch data from Google Sheets (include CSV format)
sheet_url = "https://docs.google.com/spreadsheets/d/14dZqtAclmYsudVHV7mlIbXyM2wSwcu55KhwCOm9_Bv8/gviz/tq?tqx=out:csv"

# Load Google Sheet into DataFrame
df_sheet = pd.read_csv(sheet_url)

# Function to fetch all employees from MongoDB
def get_all_employees():
    collection = db[collection_name]
    employees = list(collection.find({}, {'_id': 0}))  # Exclude the '_id' field
    return employees

# Page title
st.title("Schedule des employés")

# Fetch employees for selection
employees = get_all_employees()

if employees:
    # Convert to DataFrame from MongoDB data
    df = pd.DataFrame(employees)

    # Merge with the Google Sheet data to get 'confirmation' status
    df = df.merge(df_sheet[['Name and ID', 'confirmation']], on='Name and ID', how='left')

    # Multiselect for employee selection
    selected_employees = st.multiselect(
        "Sélectionnez un ou plusieurs employés pour le planning:",
        options=df.index,  # Select rows by index
        format_func=lambda x: f"{df.loc[x, 'Name and ID']}"  # Display 'Name and ID' in the selection dropdown
    )

    # Dropdown (selectbox) for work shifts
    st.subheader("Sélectionnez un quart du travail:")
    work_shifts = [
        "09:15 AM",
        "9:30 AM",
        "16:00 PM",
    ]
    selected_shift = st.selectbox("Quart du travail", work_shifts)

    # Button for confirmation
    if st.button("Confirmer"):
        # Check if at least one employee is selected
        if not selected_employees:
            st.error("Veuillez sélectionner au moins un employé.")
        else:
            # Prepare the selected employee data
            selected_data = df.loc[selected_employees, ["Name and ID", "Personal Phone Number", "Email", "confirmation"]]
            employee_data = selected_data.to_dict(orient="records")

            # Calculate tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            # Prepare a list for employees to be contacted
            employees_to_contact = []

            # Add message for each employee who has not been contacted yet
            for employee in employee_data:
                if employee['confirmation'] == 'sent':
                    st.warning(f"{employee['Name and ID']} a déjà reçu un message.")
                    continue  # Skip if the employee has already been contacted
                
                name_and_id = employee["Name and ID"]
                message = (f"CONFIRMATION: {name_and_id}, vous travaillez demain ({tomorrow}) à {selected_shift}, "
                           f"svp confirmer votre présence.\n"
                           "\n"
                           f"CONFIRMATION: {name_and_id}, you are scheduled to work tomorrow ({tomorrow}) at {selected_shift}, "
                           "please confirm your availability.")
                
                # Add the message to the employee's data
                employee['message'] = message
                employees_to_contact.append(employee)  # Only contact employees who have not been contacted

            if employees_to_contact:
                # Prepare data to send to the API
                data_to_send = {
                    "shift": selected_shift,
                    "employees": employees_to_contact
                }

                # Send the data to the API
                api_url = "https://hook.us2.make.com/6lo0leyylnmimbx2kxmajcob0xbhcc19"  # Replace with your API endpoint
                response = requests.post(api_url, json=data_to_send)

                if response.status_code == 200:
                    st.success("Les confirmations ont été envoyées avec succès ! Veuillez consulter **Suivi Schedule** pour suivre les réponses.")

                    # Update the confirmation status locally (you can update Google Sheets if needed)
                    for employee in employees_to_contact:
                        df.loc[df['Name and ID'] == employee['Name and ID'], 'confirmation'] = 'sent'
                else:
                    st.error(f"Erreur lors de l'envoi des données à l'API: {response.status_code}")
            else:
                st.info("Tous les employés sélectionnés ont déjà été contactés.")
else:
    st.write("Aucun employé trouvé dans la base de données.")
