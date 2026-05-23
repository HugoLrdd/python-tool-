import streamlit as st
import qrcode
from PIL import Image
import io
import pandas as pd
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="Mes Outils Connectés", page_icon="🏠", layout="wide")

# 2. Menu de navigation latéral (On regroupe TOUT ici)
st.sidebar.title("🎛️ Navigation")
choix = st.sidebar.radio("Choisir un outil :", [
    "🏆 Coupe du Monde 2026",
    "🏠 Maison & Énergie", 
    "🔗 Générateur de QR Code", 
    "🖼️ Compresseur d'Image"
])

# -------------------------------------------------------------
# OUTIL 1 : CALENDRIER COUPE DU MONDE (IMPORT CSV)
# -------------------------------------------------------------
if choix == "🏆 Coupe du Monde 2026":
    st.title("🏆 Calendrier de la Coupe du Monde 2026")
    st.write("Sélectionnez une date pour voir instantanément les matchs programmés, les horaires et les chaînes de télé.")

    try:
        # Lecture de ton fichier calendrier.csv sur GitHub
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
        st.error("❌ Erreur : Le fichier 'calendrier.csv' est introuvable sur GitHub. Merci de l'ajouter pour charger les matchs.")


# -------------------------------------------------------------
# OUTIL 2 : MAISON INTELLIGENTE & ÉNERGIE
# -------------------------------------------------------------
elif choix == "🏠 Maison & Énergie":
    st.title("🏠 Mon Tableau de Bord Smart Home & Énergie")
    st.write("Suivez la consommation de vos appareils, optimisez vos factures et simulez vos économies.")

    # Configuration des Tarifs
    st.sidebar.subheader("⚡ Configuration Tarifs")
    tarif_hp = st.sidebar.number_input("Tarif Heures Pleines (€/kWh)", value=0.25, step=0.01)
    tarif_hc = st.sidebar.number_input("Tarif Heures Creuses (€/kWh)", value=0.20, step=0.01)

    if "appareils" not in st.session_state:
        st.session_state.appareils = [
            {"Appareil": "Frigo / Congélateur", "Puissance (Watts)": 150, "Heures/Jour": 24, "Type Tarif": "Mixte (HP/HC)"},
            {"Appareil": "Ordinateur de Bureau (Gaming)", "Puissance (Watts)": 400, "Heures/Jour": 5, "Type Tarif": "Heures Pleines"},
            {"Appareil": "Chauffe-eau (Ballon)", "Puissance (Watts)": 2200, "Heures/Jour": 4, "Type Tarif": "Heures Creuses"},
            {"Appareil": "Lave-Linge", "Puissance (Watts)": 2000, "Heures/Jour": 1, "Type Tarif": "Heures Creuses"},
            {"Appareil": "Télévision + Box", "Puissance (Watts)": 120, "Heures/Jour": 6, "Type Tarif": "Heures Pleines"},
            {"Appareil": "Éclairage (Vieilles ampoules)", "Puissance (Watts)": 300, "Heures/Jour": 5, "Type Tarif": "Heures Pleines"},
        ]

    st.subheader("🔌 Connecter ou ajouter un nouvel appareil")
    with st.expander("➕ Cliquer pour ajouter un appareil personnalisé"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: nom_app = st.text_input("Nom de l'appareil", "Radiateur Chambre")
        with col2: puissance_app = st.number_input("Puissance (en Watts)", min_value=1, value=1000)
        with col3: heures_app = st.slider("Utilisation (Heures / Jour)", 0.0, 24.0, 3.0, step=0.5)
        with col4: tarif_app = st.selectbox("Type d'utilisation", ["Heures Pleines", "Heures Creuses", "Mixte (HP/HC)"])
        
        if st.button("Ajouter l'appareil au suivi"):
            st.session_state.appareils.append({
                "Appareil": nom_app, "Puissance (Watts)": puissance_app, "Heures/Jour": heures_app, "Type Tarif": tarif_app
            })
            st.success(f"L'appareil '{nom_app}' est maintenant suivi !")
            st.rerun()

    df_home = pd.DataFrame(st.session_state.appareils)
    df_home["kWh / Jour"] = (df_home["Puissance (Watts)"] * df_home["Heures/Jour"]) / 1000
    df_home["kWh / An"] = df_home["kWh / Jour"] * 365

    def calculer_cout_annuel(row):
        kwh_an = row["kWh / An"]
        if row["Type Tarif"] == "Heures Pleines": return kwh_an * tarif_hp
        elif row["Type Tarif"] == "Heures Creuses": return kwh_an * tarif_hc
        else: return (kwh_an * 0.60 * tarif_hp) + (kwh_an * 0.40 * tarif_hc)

    df_home["Coût Estimé / An (€)"] = df_home.apply(calculer_cout_annuel, axis=1)

    st.markdown("---")
    st.subheader("⚡ Statistiques Globales de Consommation")
    kpi1, kpi2, kpi3 = st.columns(3)
    total_kwh_an = df_home["kWh / An"].sum()
    facture_an = df_home["Coût Estimé / An (€)"].sum()
    
    kpi1.metric(label="Consommation Totale", value=f"{total_kwh_an:.1f} kWh / an")
    kpi2.metric(label="Facture Électricité Estimée", value=f"{facture_an:.2f} € / an", delta=f"{facture_an/12:.2f} € / mois", delta_color="inverse")
    kpi3.metric(label="Empreinte Carbone", value=f"{total_kwh_an * 0.05:.1f} kg CO2 / an")

    st.subheader("📋 Données détaillées des capteurs")
    st.dataframe(df_home.style.format({"kWh / Jour": "{:.2f}", "Coût Estimé / An (€)": "{:.2f} €"}), use_container_width=True)


# -------------------------------------------------------------
# OUTIL 3 : GÉNÉRATEUR DE QR CODE
# -------------------------------------------------------------
elif choix == "🔗 Générateur de QR Code":
    st.title("🔗 Générateur de QR Code")
    url = st.text_input("Collez votre URL ici :", "")
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
# OUTIL 4 : COMPRESSEUR D'IMAGE
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
            byte_im = buf.getvalue()
            poids_sortie = len(byte_im) / (1024 * 1024)
            gain = ((poids_origine - poids_sortie) / poids_origine) * 100

            st.success(f"🔥 Nouveau poids : **{poids_sortie:.2f} Mo** (-{gain:.1f}%)")
            st.download_button(label="💾 Télécharger l'image", data=byte_im, file_name=f"compressed_{fichier_image.name}", mime="image/jpeg")
