import streamlit as st
import pandas as pd
from datetime import datetime

# Obtenir la date actuelle
current_date = datetime.now().strftime("%Y-%m-%d")

# URL de la Google Sheet publiée au format CSV
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTN_TY54FgOENRgPn5SPsn0GWVCUovoQt5yZhhvJjZW8WtEIseWNeotcqRTfVIcFoZgYHFA4qlcYVyD/pub?gid=1218607264&single=true&output=csv"

# Lire les données CSV depuis la ligne 4 (index 10)
df = pd.read_csv(sheet_url, header=11)

# Afficher le titre de l'application avec le jour actuel
st.title(f"VTRL - {current_date}")

# Sélectionner seulement les colonnes 'NAME', 'SHIFT', et 'CONFIRM'
columns_to_display = ['NAME', 'SHIFT', 'CONFIRM']

# Filtrer les colonnes qui existent dans le DataFrame
existing_columns = [col for col in columns_to_display if col in df.columns]

# Si des colonnes sont manquantes, les afficher dans une erreur
missing_columns = [col for col in columns_to_display if col not in df.columns]
if missing_columns:
    st.error(f"Colonnes manquantes : {missing_columns}")

# Nettoyer la colonne 'SHIFT' et 'CONFIRM' en enlevant les espaces avant et après
df['SHIFT'] = df['SHIFT'].fillna('').str.strip()

# Vérifier si la colonne 'CONFIRM' existe, sinon créer une colonne vide pour éviter les erreurs
if 'CONFIRM' not in df.columns:
    df['CONFIRM'] = ''  # Ajouter la colonne vide si elle n'existe pas

# Assurez-vous que chaque DataFrame filtré contient bien la colonne 'CONFIRM'
def ensure_confirm_column(df):
    if 'CONFIRM' not in df.columns:
        df['CONFIRM'] = ''
    return df

# Fonction pour colorer les lignes en fonction des conditions
def color_row(row):
    # Si CONFIRM == "TO CANCEL", toujours jaune
    if row['CONFIRM'] == 'TO CANCEL':
        return ['background-color: yellow'] * len(row)
    
    # Si SHIFT == "CUT", toujours rouge
    if row['SHIFT'] == 'CUT':
        return ['background-color: lightcoral'] * len(row)
    
    # Si SHIFT == "CALL-OFF", toujours orange
    if row['SHIFT'] == 'CALL-OFF':
        return ['background-color: orange'] * len(row)

    # Appliquer les couleurs seulement si CONFIRM == "CONFIRMED"
    if row['CONFIRM'] == 'CONFIRMED':
        if 'Cycle 1 (W1)' in row['SHIFT']:
            return ['background-color: lightgreen'] * len(row)  # Vert pour Cycle 1 (W1)
        elif 'Cycle 1 (W2)' in row['SHIFT']:
            return ['background-color: lightblue'] * len(row)  # Bleu pour Cycle 1 (W2)
        elif 'Cycle 0' in row['SHIFT']:
            return ['background-color: lightcyan'] * len(row)  # Cyan pour Cycle 0
        elif 'Flex' in row['SHIFT']:
            return ['background-color: pink'] * len(row)  # Rose pour Flex
        elif 'Crashsort' in row['SHIFT']:
            return ['background-color: deepskyblue'] * len(row)  # Bleu foncé pour Crashsort
        elif 'STANDBY' in row['SHIFT']:
            return ['background-color: lightyellow'] * len(row)  # Jaune clair pour STANDBY
        elif 'Dispatch (Jour)' in row['SHIFT']:
            return ['background-color: orange'] * len(row)  # Orange pour Dispatch (Jour)
        elif 'Dispatch (Soir)' in row['SHIFT']:
            return ['background-color: purple'] * len(row)  # Violet pour Dispatch (Soir)
        elif 'Entretien' in row['SHIFT']:
            return ['background-color: lightpink'] * len(row)  # Rose clair pour Entretien
    
    # Sinon, appliquer du gris si CONFIRM n'est pas "CONFIRMED"
    return ['background-color: lightgrey'] * len(row)

# Séparer les tableaux selon les différents SHIFTs et assurer que chaque DataFrame contient bien la colonne 'CONFIRM'
cycle_0_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Cycle 0", na=False)])
cycle_1_w1_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Cycle 1 \(W1\)", na=False)])
cycle_1_w2_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Cycle 1 \(W2\)", na=False)])
flex_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Flex", na=False)])
crashsort_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Crashsort", na=False)])
standby_df = ensure_confirm_column(df[df['SHIFT'].str.contains("STANDBY", na=False)])
cut_df = ensure_confirm_column(df[df['SHIFT'].str.contains("CUT", na=False)])
dispatch_jour_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Dispatch \(Jour\)", na=False)])
dispatch_soir_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Dispatch \(Soir\)", na=False)])
call_off_df = ensure_confirm_column(df[df['SHIFT'].str.contains("CALL-OFF", na=False)])
entretien_df = ensure_confirm_column(df[df['SHIFT'].str.contains("Entretien", na=False)])

# Afficher chaque tableau séparément avec des titres, les nombres de noms et des couleurs conditionnelles

# Fonction pour afficher un tableau avec le nombre de noms
def display_table_with_count(df, title):
    count = df['NAME'].nunique()  # Nombre unique de noms
    st.subheader(f"{title} ({count} DAs)")
    st.dataframe(df[existing_columns].style.apply(color_row, axis=1))

# Tableau Cycle 0 (affiché en premier)
if not cycle_0_df.empty:
    display_table_with_count(cycle_0_df, "Cycle 0")
else:
    st.subheader("Cycle 0")
    st.write("Aucune donnée trouvée pour Cycle 0")

# Tableau Cycle 1 (W1)
if not cycle_1_w1_df.empty:
    display_table_with_count(cycle_1_w1_df, "Cycle 1 (W1)")
else:
    st.subheader("Cycle 1 (W1)")
    st.write("Aucune donnée trouvée pour Cycle 1 (W1)")

# Tableau Cycle 1 (W2)
if not cycle_1_w2_df.empty:
    display_table_with_count(cycle_1_w2_df, "Cycle 1 (W2)")
else:
    st.subheader("Cycle 1 (W2)")
    st.write("Aucune donnée trouvée pour Cycle 1 (W2)")

# Tableau Flex
if not flex_df.empty:
    display_table_with_count(flex_df, "Flex")
else:
    st.subheader("Flex")
    st.write("Aucune donnée trouvée pour Flex")

# Tableau Crashsort
if not crashsort_df.empty:
    display_table_with_count(crashsort_df, "Crashsort")
else:
    st.subheader("Crashsort")
    st.write("Aucune donnée trouvée pour Crashsort")

# Tableau STANDBY
if not standby_df.empty:
    display_table_with_count(standby_df, "STANDBY")
else:
    st.subheader("STANDBY")
    st.write("Aucune donnée trouvée pour STANDBY")

# Tableau CUT
if not cut_df.empty:
    display_table_with_count(cut_df, "CUT")
else:
    st.subheader("CUT")
    st.write("Aucune donnée trouvée pour CUT")

# Tableau Dispatch (Jour)
if not dispatch_jour_df.empty:
    display_table_with_count(dispatch_jour_df, "Dispatch (Jour)")
else:
    st.subheader("Dispatch (Jour)")
    st.write("Aucune donnée trouvée pour Dispatch (Jour)")

# Tableau Dispatch (Soir)
if not dispatch_soir_df.empty:
    display_table_with_count(dispatch_soir_df, "Dispatch (Soir)")
else:
    st.subheader("Dispatch (Soir)")
    st.write("Aucune donnée trouvée pour Dispatch (Soir)")

# Tableau CALL-OFF
if not call_off_df.empty:
    display_table_with_count(call_off_df, "CALL-OFF")
else:
    st.subheader("CALL-OFF")
    st.write("Aucune donnée trouvée pour CALL-OFF")

# Tableau Entretien
if not entretien_df.empty:
    display_table_with_count(entretien_df, "Entretien")
else:
    st.subheader("Entretien")
    st.write("Aucune donnée trouvée pour Entretien")
