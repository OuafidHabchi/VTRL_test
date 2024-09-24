import streamlit as st
import pandas as pd
import requests

# URL du webhook
webhook_url = "https://hook.us2.make.com/52m7piv6y7e4g4k3y7hyi5qigul5d6v6"

# URL de la Google Sheet (CSV)
sheet_url = "https://docs.google.com/spreadsheets/d/14dZqtAclmYsudVHV7mlIbXyM2wSwcu55KhwCOm9_Bv8/gviz/tq?tqx=out:csv"

# Lire les données CSV depuis Google Sheets avec gestion des lignes mal formatées
try:
    df = pd.read_csv(sheet_url, on_bad_lines='skip', low_memory=False)
except pd.errors.ParserError as e:
    st.error(f"Error while parsing CSV: {e}")
    df = None

if df is not None:
    # Nettoyer les colonnes
    df.columns = df.columns.str.strip()

    # Filtrer les lignes non vides (au moins une cellule remplie)
    non_empty_rows = df.dropna(how='all')

    # Compter le nombre de lignes avec des données
    total_non_empty = len(non_empty_rows)

    # Créer une liste allant de 2 à total_non_empty + 1
    response_list = list(range(2, total_non_empty + 2))

    # Convertir les données en CSV
    csv_data = non_empty_rows.to_csv(index=False)

    # Afficher les étapes pour commencer une nouvelle journée
    st.title("Start a New Day")

    # Étape 1: Télécharger le fichier CSV
    st.subheader("Step 1: Download the CSV file")
    st.write("Before you start, you need to download the latest CSV file containing yesterday's confirmations.")
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name='responses.csv',
        mime='text/csv'
    )

    # Étape 2: Envoyer les données au webhook
    st.subheader("Step 2: New day")
    st.write("After downloading the CSV, click the button below to start a new day by clearing out the old confirmations .")

    if st.button("clearing out the old confirmations"):
        # Préparer le payload sous forme d'objet JSON pour le webhook
        payload = {"responses": response_list}

        # Envoyer la liste au webhook
        try:
            response = requests.post(webhook_url, json=payload)
            
            # Vérifier si l'envoi a réussi
            if response.status_code == 200:
                st.success("The data was successfully sent to the webhook.")
            else:
                st.error(f"Error in sending. Response code: {response.status_code}")

        except Exception as e:
            st.error(f"An error occurred while sending the data: {e}")
