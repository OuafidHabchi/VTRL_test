import streamlit as st
import pandas as pd
import requests  # For sending data to the API
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_name = "employes"

# Fonction pour récupérer tous les employés dans MongoDB
def get_all_employees():
    collection = db[collection_name]
    employees = list(collection.find({}, {'_id': 0}))  # Exclude the '_id' field
    return employees

# Page title
st.title("Schedule des employés")

# Fetch employees for selection
employees = get_all_employees()

if employees:
    # Convert to DataFrame
    df = pd.DataFrame(employees)
    
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
            selected_data = df.loc[selected_employees, ["Name and ID", "Personal Phone Number","Email"]]
            employee_data = selected_data.to_dict(orient="records")
           
            # Calculate tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            # Create messages for each employee
            messages = []
            for employee in employee_data:
                name_and_id = employee["Name and ID"]
                message = (f"CONFIRMATION: {name_and_id}, vous travaillez demain ({tomorrow}) à {selected_shift}, "
                           "svp confirmer votre présence.")
                messages.append({
                    "name_and_id": name_and_id,
                    "message": message
                })

            # Prepare data to send to the API (formatted according to your request)
            data_to_send = {
                "shift": selected_shift,
                "employees": employee_data,
                "messages": messages
            }

            # Send the data to the API
            api_url = "https://hooks.zapier.com/hooks/catch/19888094/2hwjq84/"  # Replace with your API endpoint
            response = requests.post(api_url, json=data_to_send)

            if response.status_code == 200:
                st.success("Les informations ont été envoyées avec succès!")
            else:
                st.error(f"Erreur lors de l'envoi des données à l'API: {response.status_code}")
else:
    st.write("Aucun employé trouvé dans la base de données.")
