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
    try:
        collection = db[collection_name]
        employees = list(collection.find({}, {'_id': 0}))  # Exclude the '_id' field
        return employees
    except Exception as e:
        st.error(f"Erreur lors de la récupération des employés: {e}")
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
        "Cycle 0 (06:00 AM)",
        "Cycle 1 (w1) (09:15 AM)",
        "Cycle 1 (w2) (09:30 AM)",
        "Cycle 2 (12:00 PM)",
        "Flex (16:00 PM)",
        "Cancelled Shift"
    ]
    selected_shift = st.selectbox("Quart du travail", work_shifts)

    # Button for confirmation
    if st.button("Confirmer"):
        # Check if at least one employee is selected
        if not selected_employees:
            st.error("Veuillez sélectionner au moins un employé.")
        else:
            # Prepare the selected employee data
            selected_data = df.loc[selected_employees, ["Name and ID", "Personal Phone Number", "Email"]]
            employee_data = selected_data.to_dict(orient="records")

            # Calculate tomorrow's date
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

            # Add message for each employee based on shift selection
            for employee in employee_data:
                name_and_id = employee["Name and ID"]

                if selected_shift == "Cancelled Shift":
                    message = (f"Cher(e) {name_and_id}, \n\n"
                               "En raison de réductions d'itinéraires imprévues de la part d'Amazon, "
                               f"votre quart de travail pour demain ({tomorrow}) est annulé. "
                               "Restez disponible au cas où, et vous pourriez obtenir une carte-cadeau Tim Hortons.\n\n"
                               "Due to unforeseen route reductions from Amazon, your shift for tomorrow "
                               f"({tomorrow}) has been cancelled. Stay available, and you might receive a "
                               "Tim Hortons gift card if needed.\n\n"
                               "Cordialement, \n VTRL Dispatch")
                else:
                    message = (f"Cher(e) {name_and_id}, \n\n"
                               f"Vous êtes programmé(e) pour travailler demain ({tomorrow}) à {selected_shift}. \n"
                               "Merci de bien vouloir confirmer votre disponibilité en répondant à ce message.\n\n"
                               "Cordialement,\n"
                               f"Dear {name_and_id}, \n\n"
                               f"You are scheduled to work tomorrow ({tomorrow}) at {selected_shift}. \n"
                               "Please confirm your availability by responding to this message.\n\n"
                               "Best regards, \nVTRL Dispatch")

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
