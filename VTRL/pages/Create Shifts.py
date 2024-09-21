import streamlit as st
from pymongo import MongoClient
import pandas as pd

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
shifts_collection = "work_shifts"  # Collection pour stocker les shifts

# Liste de 10 couleurs prédéfinies
color_options = {
    "Light Blue": "#ADD8E6",
    "Yellow": "#FFFF99",
    "Gold": "#FFD700",
    "Plum": "#DDA0DD",
    "Medium Purple": "#9370DB",
    "Light Gray": "#D3D3D3",
    "Coral": "#FF7F50",
    "Light Pink": "#FFB6C1",
    "Light Salmon": "#FFA07A"
}

# Fonction pour ajouter un nouveau shift avec couleur
def add_shift(name, time, color):
    try:
        collection = db[shifts_collection]
        collection.insert_one({"name": name, "time": time, "color": color})
        st.success("Shift ajouté avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de l'ajout du shift: {e}")

# Fonction pour modifier un shift existant
def update_shift(shift_id, new_name, new_time, new_color):
    try:
        collection = db[shifts_collection]
        collection.update_one({"_id": shift_id}, {"$set": {"name": new_name, "time": new_time, "color": new_color}})
        st.success("Shift mis à jour avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la mise à jour du shift: {e}")

# Fonction pour supprimer un shift
def delete_shift(shift_id):
    try:
        collection = db[shifts_collection]
        collection.delete_one({"_id": shift_id})
        st.success("Shift supprimé avec succès !")
    except Exception as e:
        st.error(f"Erreur lors de la suppression du shift: {e}")

# Page pour ajouter des shifts
st.title("Shift Management")

# ---- AJOUTER UN NOUVEAU SHIFT ----
st.subheader("Add a New Shift")

# Input fields for creating a shift
shift_name = st.text_input("Nom du shift")
shift_time = st.text_input("Heure du shift (ex: 06:00 AM)")

# Liste déroulante pour choisir une couleur parmi les 10 options prédéfinies
selected_color = st.selectbox("Choisissez une couleur de fond pour ce shift", list(color_options.keys()))
shift_color = color_options[selected_color]  # Récupérer la couleur hexadécimale correspondante

# Bouton pour ajouter le shift
if st.button("Add Shift"):
    if shift_name and shift_time:
        add_shift(shift_name, shift_time, shift_color)
    else:
        st.error("Veuillez remplir tous les champs.")

# ---- AFFICHER ET GÉRER LES SHIFTS EXISTANTS ----
st.subheader("Update or delete an existing shift")

# Récupérer tous les shifts existants
shifts = list(db[shifts_collection].find({}))
df_shifts = pd.DataFrame(shifts)

if not df_shifts.empty:
    # Sélectionner un shift pour modifier ou supprimer
    selected_shift = st.selectbox(
        "Sélectionnez un shift à modifier ou supprimer",
        df_shifts["_id"],  # Utiliser l'ID en interne
        format_func=lambda x: df_shifts.loc[df_shifts["_id"] == x, "name"].values[0]  # Afficher le nom dans la liste
    )

    if selected_shift:
        # Récupérer les informations du shift sélectionné
        shift_to_edit = df_shifts[df_shifts["_id"] == selected_shift].iloc[0]
        
        # Modifier le shift sélectionné
        new_shift_name = st.text_input("Nouveau nom du shift", value=shift_to_edit["name"])
        new_shift_time = st.text_input("Nouvelle heure du shift", value=shift_to_edit["time"])
        new_shift_color_name = st.selectbox("Nouvelle couleur de fond", list(color_options.keys()), index=list(color_options.values()).index(shift_to_edit["color"]))
        new_shift_color = color_options[new_shift_color_name]

        # Bouton pour mettre à jour le shift
        if st.button("Update Shift"):
            update_shift(shift_to_edit["_id"], new_shift_name, new_shift_time, new_shift_color)

        # Bouton pour supprimer le shift
        if st.button("Delete Shift"):
            delete_shift(shift_to_edit["_id"])

else:
    st.write("Aucun shift trouvé. Ajoutez un shift pour commencer.")
