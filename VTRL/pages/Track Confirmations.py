import streamlit as st
import pandas as pd
import pytz
from pymongo import MongoClient
import requests

# Connexion à MongoDB pour récupérer les shifts et leurs couleurs
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
shifts_collection = "work_shifts"

# Récupérer la liste des shifts et des couleurs correspondantes
def get_shifts_colors():
    shifts = list(db[shifts_collection].find({}, {'_id': 0, 'name': 1, 'color': 1}))
    return {shift['name']: shift['color'] for shift in shifts}

# Dictionnaire des couleurs des shifts (hors "Cancelled Shift")
shift_colors = get_shifts_colors()

# URL de la Google Sheet (CSV) - Utilisation du bon format d'URL CSV
sheet_url = "https://docs.google.com/spreadsheets/d/1trM5WUwUnEFvD6ckVMplyR1iZtmKTeXhpPwPTS54E5s/gviz/tq?tqx=out:csv"

# Lire les données CSV depuis Google Sheets avec gestion des lignes mal formatées
try:
    df = pd.read_csv(sheet_url, on_bad_lines='skip', low_memory=False)
except pd.errors.ParserError as e:
    st.error(f"Error while parsing CSV: {e}")
    df = None

if df is not None:
    # Nettoyer les colonnes
    df.columns = df.columns.str.strip()

    # Vérifier si les colonnes attendues existent
    expected_columns = ['nom', 'cycle', 'confirmation', 'tel', 'date']
    existing_columns = [col for col in expected_columns if col in df.columns]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    
    # Si des colonnes sont manquantes, afficher une erreur
    if missing_columns:
        st.error(f"Missing columns: {', '.join(missing_columns)}")
    else:
        # Filtrer pour garder uniquement les colonnes attendues
        df = df[existing_columns]

        # Convertir la colonne 'date' en format datetime (si présente)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')  # Convert to datetime

            # Définir le fuseau horaire de Montréal (UTC-4 ou UTC-5 avec EDT/EST)
            montreal_tz = pytz.timezone('America/Montreal')

            # Vérifier si la colonne est tz-aware ou naive et convertir en fonction
            if pd.api.types.is_datetime64tz_dtype(df['date']):
                # Si la colonne est déjà timezone-aware, on applique tz_convert
                df['date'] = df['date'].dt.tz_convert(montreal_tz)
            else:
                # Si la colonne n'a pas de timezone, on applique tz_localize
                df['date'] = df['date'].dt.tz_localize('UTC').dt.tz_convert(montreal_tz)

        # Afficher le titre de l'application
        st.title("Drivers Confirmations Tracker")

        # Fonction pour déterminer si la réponse est positive
        positive_responses = {"yes", "oui", "y", "confirmed", "ok", "okay", "je confirme"}
        
        def is_positive_response(response):
            return str(response).strip().lower() in positive_responses if pd.notna(response) else False

        # Filtrer les réponses positives
        positive_df = df[df['confirmation'].apply(is_positive_response)]

        # Filtrer les réponses "sent"
        sent_df = df[df['confirmation'].str.strip().str.lower() == 'sent']

        # Filtrer toutes les autres réponses (ni positives ni 'sent')
        other_df = df[~df['confirmation'].apply(is_positive_response) & 
                      (df['confirmation'].str.strip().str.lower() != 'sent')]

        # Afficher les nombres en gras et plus grands avec st.markdown
        st.markdown(f"### **Confirmed Responses: {len(positive_df)}**")
        st.markdown(f"### **Pending Responses: {len(sent_df)}**")
        st.markdown(f"### **Declined Responses: {len(other_df)}**")

        # Fonction pour assigner des couleurs en fonction du 'cycle' et d'une couleur prédéfinie pour "Cancelled Shift"
        def get_shift_color(row):
            if 'cycle' in row:
                cycle = row['cycle']
                # Si le shift est "Cancelled Shift", toujours renvoyer la couleur orange
                if "Cancelled Shift" in cycle:
                    return 'background-color: orange;'  # Couleur orange pour "Cancelled Shift"
                # Utiliser les couleurs stockées pour les autres shifts
                for shift_name, color in shift_colors.items():
                    if shift_name in cycle:
                        return f'background-color: {color};'  # Utiliser la couleur stockée dans MongoDB
            return 'background-color: white;'  # Couleur par défaut si aucun cycle spécifique n'est trouvé

        # Définir une fonction pour appliquer des styles CSS personnalisés en fonction de la confirmation
        def color_confirmation(row):
            response = str(row['confirmation']).strip().lower() if pd.notna(row['confirmation']) else 'unknown'
            
            if is_positive_response(response):
                color = 'background-color: lightgreen;'  # Vert pour les réponses positives (Yes, Oui, etc.)
            elif response == 'sent':
                # Couleur en fonction du type de cycle si la confirmation est 'sent'
                color = get_shift_color(row)
            else:
                color = 'background-color: lightcoral;'  # Rouge pour les réponses négatives ou inconnues
            
            return [color] * len(row)  # Appliquer la couleur à toute la ligne

        # Grouper les données par 'cycle' et afficher des tableaux séparés
        if 'cycle' in df.columns:
            grouped = df.groupby('cycle')
            for cycle, group in grouped:
                st.markdown(f"### {cycle}")  # Afficher le cycle en tant qu'en-tête
                styled_group = group.style.apply(color_confirmation, axis=1)
                st.table(styled_group)  # Afficher le DataFrame stylisé pour ce groupe
        else:
            st.error("The 'cycle' column is missing from the dataset.")
