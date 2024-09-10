import streamlit as st
import cv2
import torch
import os
import numpy as np
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import uuid
import time
from PIL import Image
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration SMTP pour l'envoi des e-mails
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # Example de port
SMTP_USER = "Your_mail@gmail.com" #pour recoit l'alerte
SMTP_PASSWORD = "wokn bmny vcqb" #example Mot de passe 

# Database connection
DATABASE_URL = "mysql+pymysql://root:@localhost:3306/streamlit_db"
Base = declarative_base()

class Alert(Base):
    __tablename__ = 'alert'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    images = Column(String(255))

# Create the database engine
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def send_alert_email(images, timestamp):
    # Save the alert to the database
    image_paths = ','.join([os.path.basename(image[0]) for image in images])
    new_alert = Alert(timestamp=timestamp, images=image_paths)
    session.add(new_alert)
    session.commit()

    # Send email alert
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "hiichem.mhadhbi@gmail.com"
    msg['Subject'] = f"Haute violence détectée à {timestamp}!"
    body = f"Attention: La violence a été détectée le {timestamp}. Veuillez vérifier la situation immédiatement. Voir l’image ci-jointe à titre de référence."
    msg.attach(MIMEText(body, 'plain'))

    for image_path, confidence in images:
        with open(image_path, 'rb') as file:
            img = MIMEImage(file.read())
            img.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
            msg.attach(img)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

# Fonction pour afficher les images dans un dossier spécifié
def show_images_in_folder(folder_path):
    image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]
    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        image = Image.open(image_path)
        st.image(image, caption=image_file, use_column_width=True)

# Fonction pour créer un dossier pour stocker les captures
def create_capture_folder():
    base_dir = "CaptureStreamlit"
    os.makedirs(base_dir, exist_ok=True)
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    capture_folder = os.path.join(base_dir, f'captures_{run_id}')
    os.makedirs(capture_folder, exist_ok=True)
    return capture_folder

# Fonction pour obtenir les images de violence avec la plus haute confiance
def get_top_violence_images(folder_path, num_images=3):
    images = []
    for file in os.listdir(folder_path):
        if file.endswith('.jpg') and 'violence' in file:
            confidence = float(file.split('_')[2][:-4])
            images.append((os.path.join(folder_path, file), confidence))
    images.sort(key=lambda x: x[1], reverse=True)
    return images[:num_images]  # Retourner seulement les chemins et les confiances

# Fonction principale de l'application de détection de violence
def violence_detection_app():
    st.title('Violence Detection Application')
    start_camera = st.button("Démarrer la caméra")
    stop_camera = st.button("Arrêter la caméra")

    if start_camera:
        MODEL_WEIGHTS_PATH = os.path.join('yolov5', 'runs', 'train', 'exp13', 'weights', 'last.pt')
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_WEIGHTS_PATH, force_reload=True)
        capture_folder = create_capture_folder()
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Impossible d’ouvrir la caméra.")
            return

        stframe = st.empty()
        last_checked_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("Impossible de lire l’image de la caméra.")
                break

            results = model(frame)
            detections = results.xyxy[0].cpu().numpy()

            for detection in detections:
                x1, y1, x2, y2, confidence, class_id = detection
                if class_id == 1 and confidence > 0.9:
                    # Modification de la couleur du cadre à rouge
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
                    cv2.putText(frame, f"Violence {confidence:.2f}", (int(x1), int(y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    img_name = f"violence_{confidence:.2f}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    img_path = os.path.join(capture_folder, img_name)
                    cv2.imwrite(img_path, frame)

            stframe.image(frame, channels="BGR", use_column_width=True)

            # Vérification toutes les 2 minutes
            current_time = time.time()
            if current_time - last_checked_time >= 120:  # 2 minutes
                top_images = get_top_violence_images(capture_folder)
                if top_images:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    send_alert_email(top_images, timestamp)
                last_checked_time = current_time
                capture_folder = create_capture_folder()  # Créer un nouveau dossier pour les nouvelles captures
    
    if stop_camera:
        run_detection = False
        
    # Sélection du dossier à afficher
    base_dir = "CaptureStreamlit"
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    if folders:
        selected_folder = st.sidebar.selectbox("Sélectionnez un dossier pour afficher le contenu", folders)
        if st.sidebar.button("Afficher les images"):
            folder_path = os.path.join(base_dir, selected_folder)
            show_images_in_folder(folder_path)

# Lien vers le fichier CSS
css = open("style.css").read()

# Affichage du CSS
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Exécution de l'application
if __name__ == "__main__":
    violence_detection_app()
