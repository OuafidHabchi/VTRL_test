import streamlit as st
import pandas as pd
from pymongo import MongoClient

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

# URL de la Google Sheet (à remplacer par le tien si nécessaire)
sheet_url = "https://docs.google.com/spreadsheets/d/14dZqtAclmYsudVHV7mlIbXyM2wSwcu55KhwCOm9_Bv8/gviz/tq?tqx=out:csv"

# Lire les données CSV depuis Google Sheets
df = pd.read_csv(sheet_url)

# Strip any leading/trailing spaces from column names
df.columns = df.columns.str.strip()

# Now ensure only the specific columns are displayed: 'nom', 'cycle', 'confirmation', 'tel'
expected_columns = ['nom', 'cycle', 'confirmation', 'tel']

# Filter out the columns that actually exist in the DataFrame
existing_columns = [col for col in expected_columns if col in df.columns]

# If there are missing columns, display an error
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    st.error(f"Missing columns: {missing_columns}")

# Select only the columns that exist in the DataFrame
df = df[existing_columns]

# Display the title of the app
st.title("Drivers Confirmations Tracker")

# Fonction pour déterminer si la réponse est positive
positive_responses = {"yes", "oui", "y", "confirmed", "ok", "okay","je confirme"}  # Variations des réponses positives
def is_positive_response(response):
    return str(response).strip().lower() in positive_responses

# Filtrer les réponses positives
positive_df = df[df['confirmation'].apply(is_positive_response)]

# Filtrer les réponses "sent"
sent_df = df[df['confirmation'].str.strip().str.lower() == 'sent']

# Filtrer toutes les autres réponses (ni positives ni 'sent')
other_df = df[~df['confirmation'].apply(is_positive_response) & (df['confirmation'].str.strip().str.lower() != 'sent')]

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
    response = row['confirmation'].strip().lower() if 'confirmation' in row else 'unknown'
    
    if is_positive_response(response):
        color = 'background-color: lightgreen;'  # Vert pour les réponses positives (Yes, Oui, etc.)
    elif response == 'sent':
        # Couleur en fonction du type de cycle si la confirmation est 'sent'
        color = get_shift_color(row)
    else:
        color = 'background-color: lightcoral;'  # Rouge pour les réponses négatives ou inconnues
    
    return [color] * len(row)  # Appliquer la couleur à toute la ligne

# Grouping the DataFrame by 'cycle' and displaying separate tables
if 'cycle' in df.columns:
    grouped = df.groupby('cycle')
    for cycle, group in grouped:
        st.markdown(f"### {cycle}")  # Display cycle as a header
        styled_group = group.style.apply(color_confirmation, axis=1)
        st.dataframe(styled_group)  # Display the styled dataframe for this group
else:
    st.error("The 'cycle' column is missing from the dataset.")
