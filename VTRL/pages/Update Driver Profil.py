import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_name = "employes"

# Fonction pour récupérer tous les employés
def get_all_employees():
    collection = db[collection_name]
    return list(collection.find({}, {"_id": 0}))  # Exclut le champ "_id"

# Fonction pour supprimer un employé
def delete_employee(employee):
    collection = db[collection_name]
    collection.delete_one({"Name and ID": employee['Name and ID']})  # Utiliser 'Name and ID' pour identifier l'employé
    st.success("Profil supprimé avec succès.")

# Fonction pour mettre à jour un employé
def update_employee(old_data, new_data):
    collection = db[collection_name]
    new_data.pop('_id', None)  # S'assurer que le champ '_id' n'est pas mis à jour
    collection.update_one({"Name and ID": old_data['Name and ID']}, {"$set": new_data})  # Identifier par 'Name and ID'
    st.success("Profil mis à jour avec succès.")

# Interface principale
st.title("Gestion des employés")

# Liste déroulante des employés
employees = get_all_employees()
employee_names = [f"{emp['Name and ID']} - {emp['Position']}" for emp in employees]
selected_employee_name = st.selectbox("Sélectionnez un employé", employee_names)

if selected_employee_name:
    # Demander à l'utilisateur de choisir une action avant d'afficher les détails
    action = st.radio("Choisissez une action", ("Mettre à jour le profil", "Supprimer le profil"))

    if action:
        # Récupérer les données de l'employé sélectionné
        selected_employee = next(emp for emp in employees if f"{emp['Name and ID']} - {emp['Position']}" == selected_employee_name)

        if action == "Supprimer le profil":
            if st.button("Confirmer la suppression"):
                delete_employee(selected_employee)
        
        elif action == "Mettre à jour le profil":
            st.subheader("Mettre à jour les informations de l'employé")

            # Formulaire de mise à jour des champs spécifiés, en excluant certains champs
            updated_data = {}
            updated_data['Name and ID'] = st.text_input("Modifier 'Name and ID'", selected_employee.get('Name and ID', ''))
            updated_data['ID expiration'] = st.text_input("Modifier 'ID expiration'", selected_employee.get('ID expiration', ''))
            updated_data['Personal Phone Number'] = st.text_input("Modifier 'Personal Phone Number'", selected_employee.get('Personal Phone Number', ''))
            updated_data['Email'] = st.text_input("Modifier 'Email'", selected_employee.get('Email', ''))
            updated_data['Status'] = st.text_input("Modifier 'Status'", selected_employee.get('Status', ''))

            # Enregistrer les modifications
            if st.button("Enregistrer les modifications"):
                update_employee(selected_employee, updated_data)
