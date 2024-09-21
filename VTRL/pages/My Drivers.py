import streamlit as st
import pandas as pd
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient("mongodb+srv://wafid:wafid@ouafid.aihn5iq.mongodb.net")
db = client["Employees"]
collection_name = "employes"

# Fonction pour récupérer tous les employés dans MongoDB
def get_all_employees():
    collection = db[collection_name]
    employees = list(collection.find({}, {'_id': 0}))  # Exclude the '_id' field
    return employees

# Page title
st.title("Liste des employés")

# Fetch and display employees
employees = get_all_employees()

if employees:
    # Convert to DataFrame
    df = pd.DataFrame(employees)

    # Display the employees list
    st.dataframe(df, height=600, width=1100)
else:
    st.write("Aucun employé trouvé dans la base de données.")
