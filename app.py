import streamlit as st
import qrcode
from PIL import Image
import io
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. Configuration de la page
st.set_page_config(page_title="Mon Application Pro & Maison", page_icon="🏠", layout="wide")

# 2. Menu de navigation latéral
st.sidebar.title("🎛️ Navigation")
choix = st.sidebar.radio("Choisir un outil :", [
    "🏠 Maison Intelligente & Énergie", 
    "📊 Dashboard de Projet (Gantt)", 
    "🔗 Générateur de QR Code", 
    "🖼️ Compresseur d'Image"
])

# -------------------------------------------------------------
# OUTIL MAISON INTELLIGENTE : SUIVI ÉLECTRICITÉ & COÛTS
# -------------------------------------------------------------
if choix == "🏠 Maison Intelligente & Énergie":
    st.title("🏠 Mon Tableau de Bord Smart Home & Énergie")
    st.write("Suivez la consommation de vos appareils, optimisez vos factures et simulez vos économies.")

    # 1. Configuration des Tarifs de l'Électricité en France
    st.sidebar.subheader("⚡ Configuration Tarifs")
    tarif_hp = st.sidebar.number_input("Tarif Heures Pleines (€/kWh)", value=0.25, step=0.01)
    tarif_hc = st.sidebar.number_input("Tarif Heures Creuses (€/kWh)", value=0.20, step=0.01)

    # 2. Base de données des appareils de la maison (Valeurs par défaut réalistes)
    if "appareils" not in st.session_state:
        st.session_state.appareils = [
            {"Appareil": "Frigo / Congélateur", "Puissance (Watts)": 150, "Heures/Jour": 24, "Type Tarif": "Mixte (HP/HC)"},
            {"Appareil": "Ordinateur de Bureau (Gaming)", "Puissance (Watts)": 400, "Heures/Jour": 5, "Type Tarif": "Heures Pleines"},
            {"Appareil": "Chauffe-eau (Ballon)", "Puissance (Watts)": 2200, "Heures/Jour": 4, "Type Tarif": "Heures Creuses"},
            {"Appareil": "Lave-Linge", "Puissance (Watts)": 2000, "Heures/Jour": 1, "Type Tarif": "Heures Creuses"},
            {"Appareil": "Télévision + Box", "Puissance (Watts)": 120, "Heures/Jour": 6, "Type Tarif": "Heures Pleines"},
            {"Appareil": "Éclairage (Vieilles ampoules)", "Puissance (Watts)": 300, "Heures/Jour": 5, "Type Tarif": "Heures Pleines"},
        ]

    # --- SECTION 1 : AJOUTER UN APPAREIL ---
    st.subheader("🔌 Connecter ou ajouter un nouvel appareil")
    with st.expander("➕ Cliquer pour ajouter un appareil personnalisé"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nom_app = st.text_input("Nom de l'appareil", "Radiateur Chambre")
        with col2:
            puissance_app = st.number_input("Puissance de l'appareil (en Watts)", min_value=1, value=1000)
        with col3:
            heures_app = st.slider("Utilisation estimée (Heures / Jour)", 0.0, 24.0, 3.0, step=0.5)
        with col4:
            tarif_app = st.selectbox("Type d'utilisation", ["Heures Pleines", "Heures Creuses", "Mixte (HP/HC)"])
        
        if st.button("Ajouter l'appareil au suivi"):
            st.session_state.appareils.append({
                "Appareil": nom_app,
                "Puissance (Watts)": puissance_app,
                "Heures/Jour": heures_app,
                "Type Tarif": tarif_app
            })
            st.success(f"L'appareil '{nom_app}' est maintenant suivi par le système !")
            st.rerun()

    # --- ALGORITHME DE CALCUL ÉNERGÉTIQUE ---
    df_home = pd.DataFrame(st.session_state.appareils)
    
    # Calcul de la consommation journalière en kWh : (Watts * Heures) / 1000
    df_home["kWh / Jour"] = (df_home["Puissance (Watts)"] * df_home["Heures/Jour"]) / 1000
    df_home["kWh / Mois"] = df_home["kWh / Jour"] * 30
    df_home["kWh / An"] = df_home["kWh / Jour"] * 365

    # Calcul du coût financier selon le type de tarif configuré
    def calculer_cout_annuel(row):
        kwh_an = row["kWh / An"]
        if row["Type Tarif"] == "Heures Pleines":
            return kwh_an * tarif_hp
        elif row["Type Tarif"] == "Heures Creuses":
            return kwh_an * tarif_hc
        else: # Mixte : On considère 60% HP et 40% HC sur un frigo par exemple
            return (kwh_an * 0.60 * tarif_hp) + (kwh_an * 0.40 * tarif_hc)

    df_home["Coût Estimé / An (€)"] = df_home.apply(calculer_cout_annuel, axis=1)

    # --- SECTION 2 : LES KPI (INDICATEURS CLÉS DE LA MAISON) ---
    st.markdown("---")
    st.subheader("⚡ Statistiques Globales de Consommation")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        total_kwh_an = df_home["kWh / An"].sum()
        st.metric(label="Consommation Totale", value=f"{total_kwh_an:.1f} kWh / an")
    with kpi2:
        facture_an = df_home["Coût Estimé / An (€)"].sum()
        st.metric(label="Facture Électricité Estimée", value=f"{facture_an:.2f} € / an", delta=f"{facture_an/12:.2f} € / mois", delta_color="inverse")
    with kpi3:
        # Impact carbone moyen en France : env. 0.05 kg CO2 par kWh
        co2_an = total_kwh_an * 0.05
        st.metric(label="Empreinte Carbone de la Maison", value=f"{co2_an:.1f} kg CO2 / an")

    # --- SECTION 3 : LES GRAPHICHES ET ANALYSES ---
    st.markdown("---")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("📊 Répartition financière par appareil")
        fig_pie = px.pie(df_home, values="Coût Estimé / An (€)", names="Appareil", hole=0.4, title="Qui consomme le plus ?")
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g2:
        st.subheader("💡 Module d'Optimisation Intelligent")
        st.write("**Conseil Automatique du Système :**")
        
        # Algorithme de recommandation dynamique
        vieux_eclairage = df_home[df_home["Appareil"].str.contains("ampoules|Éclairage|Luminaire", case=False)]
        if not vieux_eclairage.empty:
            st.info("💡 **Opportunité détectée :** Vous utilisez de vieilles ampoules gourmandes. En les remplaçant par des LED (passant de 300W à 30W), vous économiserez environ **" + f"{vieux_eclairage['Coût Estimé / An (€)'].sum() * 0.9:.2f} €** par an !")
        
        gros_consommateurs = df_home[df_home["Type Tarif"] == "Heures Pleines"].sort_values(by="kWh / Jour", ascending=False)
        if not gros_consommateurs.empty:
            pire_appareil = gros_consommateurs.iloc[0]["Appareil"]
            st.warning(f"⏳ **Optimisation Tarifaire :** Votre appareil **{pire_appareil}** tourne en Heures Pleines. Essayez de programmer son utilisation pendant vos Heures Creuses.")

    # --- SECTION 4 : LE TABLEAU DE BORD TECHNIQUE ---
    st.subheader("📋 Données détaillées des capteurs virtuels")
    st.dataframe(df_home.style.format({"kWh / Jour": "{:.2f}", "Coût Estimé / An (€)": "{:.2f} €"}), use_container_width=True)


# -------------------------------------------------------------
# OUTIL : DASHBOARD DE PROJET (GANTT)
# -------------------------------------------------------------
elif choix == "📊 Dashboard de Projet (Gantt)":
    st.title("📊 Dashboard Professionnel de Suivi de Projet")
    # ... (Garde exactement le même code pour le projet Gantt que précédemment) ...
    st.write("Code du projet fonctionnel ici...")

# -------------------------------------------------------------
# OUTIL : GÉNÉRATEUR DE QR CODE
# -------------------------------------------------------------
elif choix == "🔗 Générateur de QR Code":
    st.title("🔗 Générateur de QR Code")
    url = st.text_input("Collez votre URL ici :", "")
    if st.button("Générer") and url:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), width=250)

# -------------------------------------------------------------
# OUTIL : COMPRESSEUR D'IMAGE
# -------------------------------------------------------------
elif choix == "🖼️ Compresseur d'Image":
    st.title("🖼️ Compresseur d'Image")
    # ... (Garde exactement le même code pour le compresseur d'image que précédemment) ...
    st.write("Code du compresseur fonctionnel ici...")
