import streamlit as st
import qrcode
from PIL import Image
import io
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. Configuration de la page
st.set_page_config(page_title="Mon Application Pro", page_icon="💼", layout="wide")

# 2. Menu de navigation latéral
st.sidebar.title("🎛️ Navigation")
choix = st.sidebar.radio("Choisir un outil :", ["Dashboard de Projet (Gantt)", "Générateur de QR Code", "Compresseur d'Image"])

# -------------------------------------------------------------
# OUTIL PRO : DASHBOARD DE PROJET & DIAGRAMME DE GANTT
# -------------------------------------------------------------
if choix == "Dashboard de Projet (Gantt)":
    st.title("📊 Dashboard Professionnel de Suivi de Projet")
    st.write("Gérez vos projets, suivez vos indicateurs clés (KPI) et visualisez votre planning en temps réel.")

    # Simulation d'une base de données de projet (Données initiales pro)
    if "projets" not in st.session_state:
        st.session_state.projets = [
            {"Tâche": "Développement de l'API", "Début": "2026-05-01", "Fin": "2026-05-15", "Avancement": 100, "Budget (€)": 4500, "Responsable": "Hugo"},
            {"Tâche": "Design de l'interface web", "Début": "2026-05-10", "Fin": "2026-05-25", "Avancement": 70, "Budget (€)": 3000, "Responsable": "Léa"},
            {"Tâche": "Tests de sécurité (QA)", "Début": "2026-05-20", "Fin": "2026-06-05", "Avancement": 20, "Budget (€)": 2500, "Responsable": "Alex"},
            {"Tâche": "Campagne Marketing & Lancé", "Début": "2026-06-01", "Fin": "2026-06-20", "Avancement": 0, "Budget (€)": 6000, "Responsable": "Sarah"},
        ]

    # --- SECTION 1 : FORMULAIRE D'AJOUT ---
    st.subheader("➕ Ajouter une nouvelle tâche au projet")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nouvelle_tache = st.text_input("Nom de la tâche", "Création de la base de données")
        responsable = st.text_input("Responsable", "Hugo")
    with col2:
        date_debut = st.date_input("Date de début", datetime.now())
        date_fin = st.date_input("Date de fin", datetime.now() + timedelta(days=10))
    with col3:
        budget = st.number_input("Budget alloué (€)", min_value=0, value=1500)
        avancement = st.slider("Avancement actuel (%)", 0, 100, 0)

    if st.button("Ajouter la tâche au planning"):
        st.session_state.projets.append({
            "Tâche": nouvelle_tache,
            "Début": str(date_debut),
            "Fin": str(date_fin),
            "Avancement": avancement,
            "Budget (€)": budget,
            "Responsable": responsable
        })
        st.success(f"Tâche '{nouvelle_tache}' ajoutée !")
        st.rerun()

    # Conversion des données en DataFrame de la bibliothèque Pandas (Le standard pro)
    df = pd.DataFrame(st.session_state.projets)

    # --- SECTION 2 : AFFICHAGE DES KPI (Indicateurs clés) ---
    st.markdown("---")
    st.subheader("📈 Indicateurs de Performance Généraux (KPI)")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="Nombre total de tâches", value=len(df))
    with kpi2:
        budget_total = df["Budget (€)"].sum()
        st.metric(label="Budget Total du Projet", value=f"{budget_total:,} €".replace(",", " "))
    with kpi3:
        avancement_moyen = df["Avancement"].mean()
        st.metric(label="Progression Globale", value=f"{avancement_moyen:.1f} %")

    # --- SECTION 3 : LE DIAGRAMME DE GANTT (VISUEL PRO) ---
    st.subheader("📅 Planning Interactif (Diagramme de Gantt)")
    
    # Génération algorithmique du diagramme de Gantt avec Plotly
    fig = px.timeline(
        df, 
        x_start="Début", 
        x_end="Fin", 
        y="Tâche", 
        color="Avancement",
        hover_data=["Responsable", "Budget (€)"],
        title="Calendrier des livrables de l'entreprise",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    # Inverser l'axe Y pour avoir la première tâche en haut
    fig.update_yaxes(autorange="reversed") 
    
    # Affichage du graphique interactif sur le site
    st.plotly_chart(fig, use_container_width=True)

    # --- SECTION 4 : LE TABLEAU DE DONNÉES BRUTES ---
    st.subheader("📋 Tableau récapitulatif des données")
    st.dataframe(df, use_container_width=True)


# -------------------------------------------------------------
# OUTIL 2 : GÉNÉRATEUR DE QR CODE
# -------------------------------------------------------------
elif choix == "Générateur de QR Code":
    st.title("🔗 Générateur de QR Code")
    url = st.text_input("Collez votre URL ici (ex: https://...):", "")
    nom_fichier = st.text_input("Nom du fichier :", "mon_qr_code")

    if st.button("Générer") and url:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.image(byte_im, width=250)
        st.download_button(label="💾 Télécharger", data=byte_im, file_name=f"{nom_fichier}.png", mime="image/png")


# -------------------------------------------------------------
# OUTIL 3 : COMPRESSEUR D'IMAGE
# -------------------------------------------------------------
elif choix == "Compresseur d'Image":
    st.title("🖼️ Compresseur d'Image")
    fichier_image = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])

    if fichier_image is not None:
        img = Image.open(fichier_image)
        poids_origine = fichier_image.size / (1024 * 1024)
        st.write(f"📊 Poids original : **{poids_origine:.2f} Mo**")

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        max_taille = 2000
        if max_taille < img.width or max_taille < img.height:
            img.thumbnail((max_taille, max_taille), Image.Resampling.LANCZOS)

        qualite = st.slider("Qualité :", 10, 100, 75)

        if st.button("Compresser"):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=qualite, optimize=True)
            byte_im = buf.getvalue()
            poids_sortie = len(byte_im) / (1024 * 1024)
            gain = ((poids_origine - poids_sortie) / poids_origine) * 100

            st.success(f"🔥 Nouveau poids : **{poids_sortie:.2f} Mo** (-{gain:.1f}%)")
            st.download_button(label="💾 Télécharger l'image", data=byte_im, file_name=f"compressed_{fichier_image.name}", mime="image/jpeg")
