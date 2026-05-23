import streamlit as st
import qrcode
from PIL import Image
import io
import pandas as pd
from datetime import datetime

# 1. Configuration de la page
st.set_page_config(page_title="Coupe du Monde 2026", page_icon="⚽", layout="centered")

# 2. Menu latéral
st.sidebar.title("🎛️ Navigation")
choix = st.sidebar.radio("Choisir un outil :", ["🏆 Calendrier Coupe du Monde", "🔗 Générateur de QR Code", "🖼️ Compresseur d'Image"])

# -------------------------------------------------------------
# OUTIL : CALENDRIER COUPE DU MONDE SIMPLIFIÉ (IMPORT CSV)
# -------------------------------------------------------------
if choix == "🏆 Calendrier Coupe du Monde":
    st.title("🏆 Calendrier de la Coupe du Monde 2026")
    st.write("Sélectionnez une date pour voir instantanément les matchs programmés, les horaires et les chaînes de télé.")

    # Algorithme d'importation automatique du fichier CSV
    try:
        df_matchs = pd.read_csv("calendrier.csv")
        # On force Python à comprendre que la colonne 'Date' contient des vraies dates
        df_matchs["Date"] = df_matchs["Date"].astype(str).str.strip()
        
        # --- FILTRE PAR JOUR ---
        st.markdown("---")
        date_recherche = st.date_input("📅 Choisissez un jour :", datetime(2026, 6, 11))
        date_str = str(date_recherche)

        # Recherche algorithmique dans le fichier importé
        matchs_du_jour = df_matchs[df_matchs["Date"] == date_str]

        if not matchs_du_jour.empty:
            st.success(f"⚽ {len(matchs_du_jour)} match(s) le {date_recherche.strftime('%d/%m/%Y')} :")
            
            # Affichage propre des matchs trouvés
            for index, row in matchs_du_jour.iterrows():
                with st.container():
                    col_h, col_m, col_d = st.columns([1, 3, 2])
                    col_h.markdown(f"### ⏰ {row['Heure']}")
                    col_m.markdown(f"### {row['Match']}")
                    col_d.markdown(f"🏟️ *{row['Stade']}*\n\n📺 **{row['Diffusion']}**")
                    st.markdown("---")
        else:
            st.info("ℹ️ Aucun match de prévu pour cette journée.")

        # Affichage du bloc complet au cas où
        with st.expander("👀 Voir la liste complète des matchs importés"):
            st.dataframe(df_matchs, use_container_width=True)

    except FileNotFoundError:
        st.error("❌ Erreur : Le fichier 'calendrier.csv' est introuvable sur GitHub. Merci de l'ajouter pour charger les matchs.")


# -------------------------------------------------------------
# LES AUTRES OUTILS (Inchangés)
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
            st.success(f"🔥 Compression terminée !")
            st.download_button(label="💾 Télécharger", data=buf.getvalue(), file_name=f"compressed_{fichier_image.name}", mime="image/jpeg")
