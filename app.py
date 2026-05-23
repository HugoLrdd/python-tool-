import streamlit as st
import qrcode
from PIL import Image
import io
import pandas as pd
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="Mon Super Hub d'Outils", page_icon="🎓", layout="wide")

# 2. Menu de navigation latéral (Mis à jour avec les Flashcards)
st.sidebar.title("🎛️ Navigation")
choix = st.sidebar.radio("Choisir un outil :", [
    "📚 Flashcards Interactives",
    "🏆 Coupe du Monde 2026",
    "🏠 Maison & Énergie", 
    "🔗 Générateur de QR Code", 
    "🖼️ Compresseur d'Image"
])

# -------------------------------------------------------------
# OUTIL 1 : GÉNÉRATEUR DE FLASHCARDS INTERACTIF
# -------------------------------------------------------------
if choix == "📚 Flashcards Interactives":
    st.title("📚 Générateur Automatique de Flashcards")
    st.write("Collez vos définitions ou votre cours, et révisez activement avec le système de cartes Recto-Verso.")

    # Zone de saisie du cours
    st.subheader("📝 1. Collez votre cours ci-dessous")
    st.caption("Format requis : une définition par ligne avec un '=' ou un ':'. Exemple :\nAPI = Interface permettant à deux logiciels de communiquer\nHTML : Langage de balisage pour créer des pages web")
    
    texte_cours = st.text_area("Entrez vos notions à réviser :", value="Python = Un langage de programmation puissant et facile à apprendre\nStreamlit = Une bibliothèque pour créer des applications web en Python\nGitHub = Une plateforme de stockage et de partage de code source")

    # Algorithme d'analyse de texte pour créer les cartes
    liste_cartes = []
    if texte_cours:
        lignes = texte_cours.split("\n")
        for ligne in lignes:
            if "=" in ligne:
                q, r = ligne.split("=", 1)
                liste_cartes.append({"Question": q.strip(), "Réponse": r.strip()})
            elif ":" in ligne:
                q, r = ligne.split(":", 1)
                liste_cartes.append({"Question": q.strip(), "Réponse": r.strip()})

    # Gestion de la session de révision
    if len(liste_cartes) > 0:
        st.markdown("---")
        st.subheader(f"🧠 2. Session de Révision ({len(liste_cartes)} cartes générées)")

        # Initialisation des variables d'état de Streamlit
        if "index_carte" not in st.session_state:
            st.session_state.index_carte = 0
        if "carte_retournee" not in st.session_state:
            st.session_state.carte_retournee = False

        # Sécurité si l'utilisateur modifie le texte en cours de route
        if st.session_state.index_carte >= len(liste_cartes):
            st.session_state.index_carte = 0

        # Récupération de la carte actuelle
        carte_actuelle = liste_cartes[st.session_state.index_carte]

        # --- DESIGN DE LA FLASHCARD ---
        st.write("")
        # Conteneur stylisé pour faire "effet carte"
        with st.container(border=True):
            st.write(f"**Carte {st.session_state.index_carte + 1} / {len(liste_cartes)}**")
            
            if not st.session_state.carte_retournee:
                st.markdown(f"### ❓ RECTO (Question) :\n## {carte_actuelle['Question']}")
                st.write("")
                if st.button("🔄 Retourner la carte"):
                    st.session_state.carte_retournee = True
                    st.rerun()
            else:
                st.markdown(f"### ❓ RECTO (Question) :\n{carte_actuelle['Question']}")
                st.markdown("---")
                st.markdown(f"### ✨ VERSO (Réponse) :\n## {carte_actuelle['Réponse']}")
                st.write("")
                if st.button("❓ Revoir la question"):
                    st.session_state.carte_retournee = False
                    st.rerun()

        # --- NAVIGATION ENTRE LES CARTES ---
        st.write("")
        col_gauche, col_droite = st.columns(2)
        
        with col_gauche:
            if st.button("⬅️ Carte précédente") and st.session_state.index_carte > 0:
                st.session_state.index_carte -= 1
                st.session_state.carte_retournee = False
                st.rerun()
                
        with col_droite:
            if st.button("➡️ Carte suivante") and st.session_state.index_carte < len(liste_cartes) - 1:
                st.session_state.index_carte += 1
                st.session_state.carte_retournee = False
                st.rerun()
                
        # Bouton de réinitialisation
        if st.button("🔁 Recommencer du début"):
            st.session_state.index_carte = 0
            st.session_state.carte_retournee = False
            st.rerun()
    else:
        st.info("Ajoutez des lignes avec '=' ou ':' dans la zone de texte pour générer vos cartes.")


# -------------------------------------------------------------
# OUTIL 2 : CALENDRIER COUPE DU MONDE
# -------------------------------------------------------------
elif choix == "🏆 Coupe du Monde 2026":
    st.title("🏆 Calendrier de la Coupe du Monde 2026")
    st.write("Sélectionnez une date pour voir instantanément les matchs programmés, les horaires et les chaînes de télé.")
    try:
        df_matchs = pd.read_csv("calendrier.csv")
        df_matchs["Date"] = df_matchs["Date"].astype(str).str.strip()
        st.markdown("---")
        date_recherche = st.date_input("📅 Choisissez un jour :", datetime(2026, 6, 11))
        date_str = str(date_recherche)
        matchs_du_jour = df_matchs[df_matchs["Date"] == date_str]
        if not matchs_du_jour.empty:
            st.success(f"⚽ {len(matchs_du_jour)} match(s) le {date_recherche.strftime('%d/%m/%Y')} :")
            for index, row in matchs_du_jour.iterrows():
                with st.container():
                    col_h, col_m, col_d = st.columns([1, 3, 2])
                    col_h.markdown(f"### ⏰ {row['Heure']}")
                    col_m.markdown(f"### {row['Match']}")
                    col_d.markdown(f"🏟️ *{row['Stade']}*\n\n📺 **{row['Diffusion']}**")
                    st.markdown("---")
        else:
            st.info("ℹ️ Aucun match de prévu pour cette journée.")
        with st.expander("👀 Voir la liste complète des matchs (Données brutes)"):
            st.dataframe(df_matchs, use_container_width=True)
    except FileNotFoundError:
        st.error("❌ Erreur : Le fichier 'calendrier.csv' est introuvable sur GitHub.")


# -------------------------------------------------------------
# OUTIL 3 : MAISON INTELLIGENTE & ÉNERGIE
# -------------------------------------------------------------
elif choix == "🏠 Maison & Énergie":
    st.title("🏠 Mon Tableau de Bord Smart Home & Énergie")
    st.sidebar.subheader("⚡ Configuration Tarifs")
    tarif_hp = st.sidebar.number_input("Tarif Heures Pleines (€/kWh)", value=0.25, step=0.01)
    tarif_hc = st.sidebar.number_input("Tarif Heures Creuses (€/kWh)", value=0.20, step=0.01)
    if "appareils" not in st.session_state:
        st.session_state.appareils = [
            {"Appareil": "Frigo / Congélateur", "Puissance (Watts)": 150, "Heures/Jour": 24, "Type Tarif": "Mixte (HP/HC)"},
            {"Appareil": "Ordinateur (Gaming)", "Puissance (Watts)": 400, "Heures/Jour": 5, "Type Tarif": "Heures Pleines"},
            {"Appareil": "Chauffe-eau", "Puissance (Watts)": 2200, "Heures/Jour": 4, "Type Tarif": "Heures Creuses"}
        ]
    df_home = pd.DataFrame(st.session_state.appareils)
    df_home["kWh / Jour"] = (df_home["Puissance (Watts)"] * df_home["Heures/Jour"]) / 1000
    df_home["kWh / An"] = df_home["kWh / Jour"] * 365
    df_home["Coût Estimé / An (€)"] = df_home["kWh / An"] * tarif_hp # version simplifiée
    st.subheader("⚡ Statistiques Globales de Consommation")
    st.dataframe(df_home, use_container_width=True)


# -------------------------------------------------------------
# OUTIL 4 : GÉNÉRATEUR DE QR CODE
# -------------------------------------------------------------
elif choix == "🔗 Générateur de QR Code":
    st.title("🔗 Générateur de QR Code")
    url = st.text_input("Collez votre URL ici :")
    if st.button("Générer") and url:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color="red ")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), width=250)


# -------------------------------------------------------------
# OUTIL 5 : COMPRESSEUR D'IMAGE
# -------------------------------------------------------------
elif choix == "🖼️ Compresseur d'Image":
    st.title("🖼️ Compresseur d'Image")
    fichier_image = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])
    if fichier_image is not None:
        img = Image.open(fichier_image)
        poids_origine = fichier_image.size / (1024 * 1024)
        st.write(f"📊 Poids original : **{poids_origine:.2f} Mo**")
        if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
        max_taille = 2000
        if max_taille < img.width or max_taille < img.height:
            img.thumbnail((max_taille, max_taille), Image.Resampling.LANCZOS)
        qualite = st.slider("Qualité :", 10, 100, 75)
        if st.button("Compresser"):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=qualite, optimize=True)
            st.success("🔥 Compression terminée !")
            st.download_button(label="💾 Télécharger", data=buf.getvalue(), file_name=f"compressed_{fichier_image.name}", mime="image/jpeg")
