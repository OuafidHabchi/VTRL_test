import streamlit as st
import pandas as pd

# Titre de la nouvelle page
st.title("Upload and View CSV File")

# Instruction pour l'utilisateur
st.write("Please upload a CSV file to display its contents.")

# Zone de téléchargement du fichier CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Si un fichier est téléchargé
if uploaded_file is not None:
    # Lire le fichier CSV
    df = pd.read_csv(uploaded_file)
    
    # Afficher le contenu du fichier
    st.write("Here is the content of your CSV file:")
    st.write(df)
else:
    st.write("No file uploaded yet. Please upload a CSV file.")
