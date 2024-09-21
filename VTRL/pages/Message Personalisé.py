import streamlit as st
import pandas as pd
from pymongo import MongoClient
import requests
import json
import math

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_name = "employes"

# Fonction pour récupérer tous les employés
def get_all_employees():
    collection = db[collection_name]
    return list(collection.find({}, {"_id": 0, "Name and ID": 1, "Personal Phone Number": 1}))  # Récupérer les employés avec leur nom et téléphone

# Fonction pour nettoyer et préparer les données au format JSON
def clean_employee_data(data):
    for employee in data['employees']:
        # Assurer que les numéros de téléphone soient des chaînes de caractères
        if isinstance(employee['phone'], float):
            if math.isnan(employee['phone']):
                employee['phone'] = None  # Remplacer NaN par None (qui sera null en JSON)
            else:
                # Convertir les numéros de téléphone float en chaînes de caractères
                employee['phone'] = str(int(employee['phone']))
        elif isinstance(employee['phone'], str):
            # Garder les numéros sous forme de chaîne de caractères
            pass
        else:
            # Si ce n'est ni une chaîne ni un float, convertir en chaîne
            employee['phone'] = str(employee['phone'])
    return data

# Interface principale
st.title("Send a personalized message")

# Récupérer la liste des employés
employees = get_all_employees()
employee_names = [f"{emp['Name and ID']}" for emp in employees]

# Sélection des employés
selected_employees = st.multiselect("Sélectionnez les employés à contacter", employee_names)

# Option pour sélectionner tous les employés
select_all = st.checkbox("Sélectionner tous les employés")

if select_all:
    selected_employees = employee_names  # Si coché, tous les employés sont sélectionnés

# Zone de texte pour écrire le message
message = st.text_area("Écrire le message à envoyer")

# Champ de saisie pour le lien du document
document_link = st.text_input("Lien du document (facultatif)")

# Bouton pour envoyer le message
if st.button("Envoyer le message"):
    # Si aucun employé n'est sélectionné
    if not selected_employees:
        st.warning("Veuillez sélectionner au moins un employé.")
    elif not message:
        st.warning("Veuillez écrire un message avant d'envoyer.")
    else:
        # Filtrer les employés sélectionnés avec leur nom et numéro de téléphone
        selected_employees_data = [
            {"name": emp['Name and ID'], "phone": emp['Personal Phone Number']}
            for emp in employees if emp['Name and ID'] in selected_employees
        ]

        # Préparer les données initiales
        data = {
            "message": message,
            "employees": selected_employees_data,  # Liste des employés avec nom et numéro
            "document_link": document_link  # Ajouter le lien du document aux données
        }

        # Nettoyer les données avant de les envoyer (convertir float en string et gérer les NaN)
        cleaned_data = clean_employee_data(data)

        # Envoyer les données via le webhook
        webhook_url = "https://hook.us2.make.com/6lo0leyylnmimbx2kxmajcob0xbhcc19"  # Remplacez par votre URL de webhook
        try:
            # Envoi via requests en format JSON avec les employés et le lien du document
            response = requests.post(webhook_url, json=cleaned_data)

            if response.status_code == 200:
                st.success("Message envoyé avec succès à tous les employés sélectionnés !")
            else:
                st.error(f"Erreur lors de l'envoi : {response.status_code}")
        except Exception as e:
            st.error(f"Une erreur est survenue lors de l'envoi : {e}")
