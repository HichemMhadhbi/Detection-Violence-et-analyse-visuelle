import streamlit as st
from sqlalchemy import create_engine, text
import cv2
import torch
import tempfile
import os
import numpy as np
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# Configuration pour la connexion à la base de données MySQL
engine = create_engine("mysql+pymysql://root:@localhost:3306/streamlit_db")

# Fonction pour vérifier les identifiants de l'utilisateur
def check_user(adminName, password):
    with engine.connect() as conn:
        query = text("SELECT * FROM admin WHERE adminName = :adminName AND password = :password")
        result = conn.execute(query, {'adminName': adminName, 'password': password})
        data = result.fetchone()
        return data is not None

# Page de connexion
def login_page():
    st.title("Login Upload Et Analyse Video")
    adminName = st.text_input("Admin", "", key="adminName", placeholder="A d m i n")
    password = st.text_input("Password", "", key="password", type="password", placeholder="Password")
    if st.button("Login"):
        if check_user(adminName, password):
            st.session_state['logged_in'] = True
            st.success("Connexion réussie!")
        else:
            st.error("Nom ou mot de passe erroné")

# Configuration SMTP pour l'envoi d'emails
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # Example de port
SMTP_USER = "Your_mail@gmail.com" #pour recoit l'alerte
SMTP_PASSWORD = "wokn bmny vcqb" #example Mot de passe 

# Fonction pour envoyer un email d'alerte
def send_alert_email(image_path, timestamp):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "hiichem.mhadhbi@gmail.com" 
    msg['Subject'] = f"Haute violence détectée à {timestamp}!"
    body = f"Attention: La violence a été détectée le {timestamp}. Veuillez vérifier la situation immédiatement. Voir l’image ci-jointe à titre de référence."
    msg.attach(MIMEText(body, 'plain'))
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read(), name=os.path.basename(image_path))
        msg.attach(img)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()


# Fonction de détection de violence
def det_violence_page(video_file_buffer):
    # Chemin du modèle YOLOv5
    MODEL_WEIGHTS_PATH = os.path.join('yolov5', 'runs', 'train', 'exp13', 'weights', 'last.pt')
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_WEIGHTS_PATH, force_reload=True)

    st.title('Violence Detection Videos')
    stframe = st.empty()

    if video_file_buffer is not None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join('CaptureStreamlit', timestamp)
        os.makedirs(video_path, exist_ok=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
            tfile.write(video_file_buffer.read())
            tfile_name = tfile.name

        cap = cv2.VideoCapture(tfile_name)
        frame_number = 0
        detected_images = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            confidences = results.xyxy[0][:, 4].cpu().numpy()
            labels = results.xyxy[0][:, -1].cpu().numpy()

            if 1 in labels:
                indices = np.where(labels == 1)[0]
                high_conf_indices = [i for i in indices if confidences[i] >= 0.8]
                for i in high_conf_indices:
                    frame = np.squeeze(results.render())
                    img_name = f"{timestamp}_frame_{frame_number}.jpg"
                    img_path = os.path.join(video_path, img_name)
                    cv2.imwrite(img_path, frame)
                    detected_images.append((img_path, confidences[i]))

            stframe.image(frame, channels="BGR", use_column_width=True)
            frame_number += 1

        cap.release()
        os.unlink(tfile_name)

        for img_path, _ in detected_images[:3]:
            send_alert_email(img_path, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

# Fonction pour charger le CSS
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Fonction pour afficher les dossiers téléchargés dans la barre latérale
def show_uploaded_folders():
    st.sidebar.title('Dossiers téléchargés')
    
    # Parcourir les dossiers dans le répertoire CaptureStreamlit
    base_dir = "CaptureStreamlit"
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    
    if folders:
        selected_folder = st.sidebar.selectbox("Sélectionnez un dossier pour afficher le contenu", folders)
        if st.sidebar.button("Afficher les images"):
            folder_path = os.path.join(base_dir, selected_folder)
            show_images_in_folder(folder_path)

# Fonction pour afficher les images dans le dossier sélectionné
def show_images_in_folder(folder_path):
    st.title(f"Images dans le dossier: {folder_path}")

    images = [os.path.join(folder_path, img) for img in os.listdir(folder_path) if img.endswith(('.jpg', '.jpeg', '.png'))]
    for img_path in images:
        st.image(img_path, caption=os.path.basename(img_path), use_column_width=True)

def main():
    load_css()  # Charger le CSS
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        video_file_buffer = st.file_uploader("Télécharger une vidéo", type=["mp4", "mov", "avi", "asf", "m4v"])
        det_violence_page(video_file_buffer)
        show_uploaded_folders()  # Afficher les dossiers dans la barre latérale
    else:
        login_page()  # Sinon, afficher la page de connexion

if __name__ == "__main__":
    main()
