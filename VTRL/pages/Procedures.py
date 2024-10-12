import streamlit as st
from pymongo import MongoClient
import requests
import math

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_employees = db["employes"]
collection_procedures = db["procedures"]

# Fonction pour récupérer les procédures depuis la collection
def get_procedure_names():
    procedures = collection_procedures.find({})
    return [procedure["Nom"] for procedure in procedures]

# Fonction pour récupérer une procédure par nom
def get_procedure_by_name(name):
    return collection_procedures.find_one({"Nom": name})

# Fonction pour ajouter une nouvelle procédure
def add_procedure(nom, body_en, body_fr, url_en, url_fr):
    new_procedure = {
        "Nom": nom,
        "Body_en": body_en,
        "Body_fr": body_fr,
        "URL_en": url_en,
        "URL_fr": url_fr
    }
    collection_procedures.insert_one(new_procedure)

# Fonction pour mettre à jour une procédure
def update_procedure(name, updated_data):
    collection_procedures.update_one({"Nom": name}, {"$set": updated_data})

# Fonction pour supprimer une procédure
def delete_procedure(name):
    collection_procedures.delete_one({"Nom": name})

# Titre de l'application
st.title("Gestion des procédures")

# Choix du mode : Ajouter, Mettre à jour, ou Envoyer
option = st.selectbox("Choisissez une option", ["Ajouter une procédure", "Mettre à jour une procédure", "Envoyer une procédure"])

if option == "Ajouter une procédure":
    st.header("Ajouter une nouvelle procédure")
    
    # Entrée pour les informations de la nouvelle procédure
    new_nom = st.text_input("Nom de la procédure")
    new_body_en = st.text_area("Contenu de la procédure (Body en anglais)")
    new_body_fr = st.text_area("Contenu de la procédure (Body en français)")
    new_url_en = st.text_input("URL de la procédure (en anglais)")
    new_url_fr = st.text_input("URL de la procédure (en français)")
    
    # Bouton pour ajouter la procédure
    if st.button("Ajouter la procédure"):
        add_procedure(new_nom, new_body_en, new_body_fr, new_url_en, new_url_fr)
        st.success("Nouvelle procédure ajoutée avec succès")

elif option == "Mettre à jour une procédure":
    st.header("Mettre à jour une procédure")
    
    # Afficher la liste déroulante des procédures existantes
    procedure_names = get_procedure_names()
    selected_procedure_name = st.selectbox("Sélectionnez une procédure", procedure_names)
    
    if selected_procedure_name:
        procedure = get_procedure_by_name(selected_procedure_name)
        
        # Afficher les champs à modifier
        updated_nom = st.text_input("Nom", value=procedure["Nom"])
        updated_body_en = st.text_area("Contenu (Body en anglais)", value=procedure.get("Body_en", ""))
        updated_body_fr = st.text_area("Contenu (Body en français)", value=procedure.get("Body_fr", ""))
        updated_url_en = st.text_input("URL (en anglais)", value=procedure.get("URL_en", ""))
        updated_url_fr = st.text_input("URL (en français)", value=procedure.get("URL_fr", ""))
        
        # Bouton pour mettre à jour la procédure
        if st.button("Mettre à jour"):
            updated_data = {
                "Nom": updated_nom,
                "Body_en": updated_body_en,
                "Body_fr": updated_body_fr,
                "URL_en": updated_url_en,
                "URL_fr": updated_url_fr
            }
            update_procedure(selected_procedure_name, updated_data)
            st.success("Procédure mise à jour avec succès")
        
        # Bouton pour supprimer la procédure
        if st.button("Supprimer la procédure"):
            delete_procedure(selected_procedure_name)
            st.success("Procédure supprimée avec succès")

elif option == "Envoyer une procédure":

    # Fonction pour récupérer les employés depuis la collection
    def get_employee_names_and_ids():
        employees = collection_employees.find({})
        return [{"name": employee["Name and ID"], "personal_phone": employee["Personal Phone Number"], "email": employee["Email"]} for employee in employees]

    # Fonction pour vérifier que les données sont conformes au format JSON
    def sanitize_data(data):
        if isinstance(data, (float, int)) and (math.isinf(data) or math.isnan(data)):
            return None
        return data

    # Fonction pour nettoyer les données avant l'envoi
    def sanitize_payload(payload):
        if isinstance(payload, dict):
            return {key: sanitize_payload(value) for key, value in payload.items()}
        elif isinstance(payload, list):
            return [sanitize_payload(item) for item in payload]
        else:
            return sanitize_data(payload)

    # Titre de la section "Envoyer une procédure"
    st.header("Envoyer une procédure")

    # 1. Sélection des employés
    employee_data = get_employee_names_and_ids()
    employee_names = [emp["name"] for emp in employee_data]

    # Case à cocher pour sélectionner tous les employés
    select_all = st.checkbox("Sélectionner tous les employés")

    # Si "Sélectionner tous les employés" est coché, nous n'affichons pas la liste des employés
    if not select_all:
        selected_employees = st.multiselect("Sélectionnez les employés à qui envoyer la procédure", employee_names)
    else:
        selected_employees = employee_names  # Tous les employés sont sélectionnés implicitement

    # 2. Choix de la méthode d'envoi (email ou téléphone)
    send_via = st.selectbox("Choisissez la méthode d'envoi", ["Email", "Phone"])

    # 3. Sélection de la procédure
    procedure_names = get_procedure_names()
    selected_procedure_name = st.selectbox("Sélectionnez une procédure à envoyer", procedure_names)

    # Partie de validation et envoi des données
    if st.button("Envoyer la procédure"):
        # Vérification que l'utilisateur a sélectionné au moins un employé, une procédure, et une méthode d'envoi
        if not selected_employees:
            st.error("Veuillez sélectionner au moins un employé.")
        elif not send_via:
            st.error("Veuillez sélectionner une méthode d'envoi.")
        elif not selected_procedure_name:
            st.error("Veuillez sélectionner une procédure.")
        else:
            # Récupération des informations des employés sélectionnés
            selected_employee_info = [emp for emp in employee_data if emp["name"] in selected_employees]
            
            # Récupération des informations de la procédure
            procedure = get_procedure_by_name(selected_procedure_name)
            
            # Préparation des données à envoyer avec Body_en et Body_fr
            data = {
                "employees": [
                    {
                        "name": emp["name"],
                        "personal_phone": emp["personal_phone"],
                        "email": emp["email"]
                    } for emp in selected_employee_info
                ],
                "procedure": {
                    "name": procedure["Nom"],
                    "body_en": procedure.get("Body_en", ""),  # Utilise Body_en
                    "body_fr": procedure.get("Body_fr", ""),  # Utilise Body_fr
                    "url_en": procedure.get("URL_en", ""),    # Utilise URL_en
                    "url_fr": procedure.get("URL_fr", "")     # Utilise URL_fr
                },
                "send_via": send_via
            }

            # Nettoyage des données
            sanitized_data = sanitize_payload(data)

            # Envoi de la requête POST au webhook
            webhook_url = "https://hook.us2.make.com/5u0rc648tifai2vhewnrnsfyjd1j4woh"
            response = requests.post(webhook_url, json=sanitized_data)

            # Vérification du succès de l'envoi
            if response.status_code == 200:
                st.success("Procédure envoyée avec succès.")
            else:
                st.error(f"Échec de l'envoi de la procédure. Code de réponse : {response.status_code}")
