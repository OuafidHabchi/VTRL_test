import streamlit as st
import pandas as pd
import requests  # For sending data to the API
from pymongo import MongoClient
from datetime import datetime, timedelta

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_name = "employes"
shifts_collection = "work_shifts"  # Collection pour stocker les shifts

# Fonction pour récupérer tous les employés dans MongoDB
def get_all_employees():
    try:
        collection = db[collection_name]
        employees = list(collection.find({}, {'_id': 0}))  # Exclude the '_id' field
        return employees
    except Exception as e:
        st.error(f"Erreur lors de la récupération des employés: {e}")
        return []

# Fonction pour récupérer les shifts depuis MongoDB
def get_all_shifts():
    try:
        collection = db[shifts_collection]
        shifts = list(collection.find({}, {'_id': 0}))  # Exclude '_id' field
        return shifts
    except Exception as e:
        st.error(f"Erreur lors de la récupération des shifts: {e}")
        return []

# Fonction pour envoyer les données à l'API
def send_to_api(data):
    api_url = "https://hook.us2.make.com/6lo0leyylnmimbx2kxmajcob0xbhcc19"  # Replace with your API endpoint
    try:
        response = requests.post(api_url, json=data)
        if response.status_code == 200:
            return True
        else:
            st.error(f"Erreur lors de l'envoi des données à l'API: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Erreur lors de la connexion à l'API: {e}")
        return False

# Page title
st.title("Confirmation Sender")

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

    # Fetch shifts for the dropdown
    st.subheader("Sélectionnez un quart du travail:")
    shifts = get_all_shifts()

    # Ajouter l'option "Cancelled Shift" en premier
    shift_options = ["Cancelled Shift"]

    # Ajouter les shifts depuis MongoDB (s'il y en a)
    shift_options += [f"{shift['name']} ({shift['time']})" for shift in shifts]

    # Affichage du selectbox avec les options disponibles
    selected_shift = st.selectbox("Quart du travail", shift_options)

    # Button for confirmation
    if st.button("Confirmer"):
        # Check if at least one employee is selected
        if not selected_employees:
            st.error("Veuillez sélectionner au moins un employé.")
        else:
            # Prepare the selected employee data
            selected_data = df.loc[selected_employees, ["Name and ID", "Personal Phone Number", "Email"]]

            # Handling NaN values (e.g., empty fields in the database)
            selected_data = selected_data.fillna("")  # Replace NaN with empty string

            # Convert DataFrame to dictionary
            employee_data = selected_data.to_dict(orient="records")

            # Calculate tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            # Add message for each employee based on shift selection
            for employee in employee_data:
                name_and_id = employee["Name and ID"]

                 if "Cancelled Shift" in selected_shift:
                    message = (f"{name_and_id}, 
                                    Demain ({tomorrow}) annulé en raison de réductions d'itinéraires Amazon. Restez dispo pour une éventuelle carte-cadeau Tim Hortons.  
                                    Tomorrow ({tomorrow}) canceled due to Amazon route cuts. Stay available for a possible Tim Hortons gift card.  
                                    Cordialement, VTRL Dispatch.")
                else:
                    message = (f"{name_and_id}, 
                                    Demain ({tomorrow}) à {selected_shift}. Merci de confirmer PAR Oui. 
                                    Tomorrow ({tomorrow}) at {selected_shift}. Please confirm BY YES.")

                # Add the message to the employee's data
                employee['message'] = message

            # Prepare data to send to the API
            data_to_send = {
                "shift": selected_shift,
                "employees": employee_data
            }

            # Send the data to the API
            if send_to_api(data_to_send):
                st.success("Les confirmations ont été envoyées avec succès ! Veuillez consulter **Suivi Schedule** pour suivre les réponses.")
else:
    st.write("Aucun employé trouvé dans la base de données.")  
