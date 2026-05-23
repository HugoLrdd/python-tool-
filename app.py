import streamlit as st
import qrcode
from PIL import Image
import io

# 1. Configuration de la page du site
st.set_page_config(page_title="Mes Outils Python", page_icon="⚡", layout="centered")

# 2. Création du menu de navigation sur le côté
st.sidebar.title("🎛️ Navigation")
choix = st.sidebar.radio("Choisir un outil :", ["Générateur de QR Code", "Compresseur d'Image"])

# -------------------------------------------------------------
# OUTIL 1 : GÉNÉRATEUR DE QR CODE
# -------------------------------------------------------------
if choix == "Générateur de QR Code":
    st.title("🔗 Générateur de QR Code")
    st.write("Entrez une URL pour générer instantanément un QR Code téléchargeable.")

    # Formulaire visuel
    url = st.text_input("Collez votre URL ici (ex: https://...):", "")
    nom_fichier = st.text_input("Nom du fichier (sans extension):", "mon_qr_code")

    if st.button("Générer le QR Code") and url:
        # Algorithme du QR Code (le même que sur Colab)
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color="purple")
        
        # Sauvegarde en mémoire pour le téléchargement web
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # Affichage visuel sur le site
        st.image(byte_im, caption="Votre QR Code généré !", width=250)
        
        # Bouton de téléchargement du site
        st.download_button(
            label="💾 Télécharger le QR Code",
            data=byte_im,
            file_name=f"{nom_fichier}.png",
            mime="image/png"
        )

# -------------------------------------------------------------
# OUTIL 2 : COMPRESSEUR D'IMAGE
# -------------------------------------------------------------
elif choix == "Compresseur d'Image":
    st.title("🖼️ Compresseur d'Image Intelligent")
    st.write("Glissez une image lourde pour réduire son poids sans perdre en qualité.")

    # Zone de glisser-déposer visuelle
    fichier_image = st.file_uploader("Choisissez une image...", type=["jpg", "jpeg", "png"])

    if fichier_image is not None:
        # Ouvrir l'image
        img = Image.open(fichier_image)
        poids_origine = fichier_image.size / (1024 * 1024) # Conversion en Mo
        
        st.write(f"📊 Poids original : **{poids_origine:.2f} Mo**")

        # Algorithme de traitement (conversion RGB si PNG)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Redimensionnement si trop grande
        max_taille = 2000
        if max_taille < img.width or max_taille < img.height:
            img.thumbnail((max_taille, max_taille), Image.Resampling.LANCZOS)

        # Curseur pour choisir la qualité (option bonus stylée !)
        qualite = st.slider("Ajuster la qualité de compression (75 est recommandé) :", 10, 100, 75)

        if st.button("Compresser l'image"):
            # Compression en mémoire
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=qualite, optimize=True)
            byte_im = buf.getvalue()
            
            poids_sortie = len(byte_im) / (1024 * 1024)
            gain = ((poids_origine - poids_sortie) / poids_origine) * 100

            # Affichage des résultats avec des badges de couleur
            st.success(f"🔥 Compression terminée ! Nouveau poids : **{poids_sortie:.2f} Mo** (-{gain:.1f}%)")
            
            # Bouton de téléchargement
            st.download_button(
                label="💾 Télécharger l'image compressée",
                data=byte_im,
                file_name=f"compressed_{fichier_image.name}",
                mime="image/jpeg"
            )
