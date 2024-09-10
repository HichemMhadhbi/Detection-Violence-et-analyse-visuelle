import streamlit as st
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

# Configuration SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587 # Example de port
SMTP_USER = "Your_mail@gmail.com" #pour recoit l'alerte
SMTP_PASSWORD = "wokn bmny vcqb" #example Mot de passe 

# Créer le dossier principal s'il n'existe pas
main_folder = 'CaptureStreamlit'
if not os.path.exists(main_folder):
    os.makedirs(main_folder)

def send_alert_email(image_path, timestamp):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "hiichem.mhadhbi@gmail.com"
    msg['Subject'] = f"Violence detected at {timestamp}!"
    body = f"Attention: Violence was detected on {timestamp}. Please verify the situation immediately. See attached image for reference."
    msg.attach(MIMEText(body, 'plain'))
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read(), name=os.path.basename(image_path))
        msg.attach(img)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

MODEL_WEIGHTS_PATH = os.path.join('yolov5', 'runs', 'train', 'exp13', 'weights', 'last.pt')
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_WEIGHTS_PATH, force_reload=True)

st.title('Violence Detection Application')
video_file_buffer = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "asf", "m4v"])
stframe = st.empty()

if video_file_buffer is not None:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(main_folder, timestamp)
    os.makedirs(video_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
        tfile.write(video_file_buffer.read())
        tfile.flush()

        # Gérer le traitement vidéo dans un bloc séparé
        cap = cv2.VideoCapture(tfile.name)
        frame_number = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            confidences = results.xyxy[0][:, 4].cpu().numpy()
            labels = results.xyxy[0][:, -1].cpu().numpy()
            
            frame_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if 1 in labels and any(confidences[labels == 1] >= 0.8):
                frame = np.squeeze(results.render())
                img_name = f"frame_{frame_number}_{frame_time}.jpg"
                img_path = os.path.join(video_path, img_name)
                cv2.imwrite(img_path, frame)  # Sauvegarder l'image avec violence détectée
                send_alert_email(img_path, frame_time)  # Envoyer un email avec l'horodatage

            stframe.image(frame, channels="BGR", use_column_width=True)
            frame_number += 1

        cap.release()

    # Supprimer le fichier temporaire après avoir fermé le flux de capture
    os.unlink(tfile.name)



"""Grand % Violence : 3 Images"""
"""
import streamlit as st
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

# Configuration SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "hichemmhichemmh@gmail.com"
SMTP_PASSWORD = "wokn bmny vcqb rcsy"

# Créer le dossier principal s'il n'existe pas
main_folder = 'CaptureStreamlit'
if not os.path.exists(main_folder):
    os.makedirs(main_folder)

def send_alert_email(image_path, timestamp):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "hiichem.mhadhbi@gmail.com"
    msg['Subject'] = f"Violence detected at {timestamp}!"
    body = f"Attention: Violence was detected on {timestamp}. Please verify the situation immediately. See attached image for reference."
    msg.attach(MIMEText(body, 'plain'))
    with open(image_path, 'rb') as file:
        img = MIMEImage(file.read(), name=os.path.basename(image_path))
        msg.attach(img)
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.send_message(msg)
    server.quit()

MODEL_WEIGHTS_PATH = os.path.join('yolov5', 'runs', 'train', 'exp10', 'weights', 'last.pt')
model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_WEIGHTS_PATH, force_reload=True)

st.title('Violence Detection Application')
video_file_buffer = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "asf", "m4v"])
stframe = st.empty()

if video_file_buffer is not None:
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(main_folder, timestamp)
    os.makedirs(video_path)

    # Utilisation d'un gestionnaire de contexte pour s'assurer que le fichier est fermé
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tfile:
        tfile.write(video_file_buffer.read())
        tfile_name = tfile.name  # Sauvegarder le nom du fichier pour utilisation ultérieure

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

        frame_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if 1 in labels:
            indices = np.where(labels == 1)[0]
            high_conf_indices = [i for i in indices if confidences[i] >= 0.8]
            for i in high_conf_indices:
                frame = np.squeeze(results.render())
                img_name = f"frame_{frame_number}_{frame_time}.jpg"
                img_path = os.path.join(video_path, img_name)
                cv2.imwrite(img_path, frame)  # Sauvegarder l'image avec violence détectée
                detected_images.append((img_path, confidences[i]))

        stframe.image(frame, channels="BGR", use_column_width=True)
        frame_number += 1

    cap.release()

    # Trier les images par confiance et envoyer les trois premières
    detected_images.sort(key=lambda x: x[1], reverse=True)
    for img_path, _ in detected_images[:3]:
        send_alert_email(img_path, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    if os.path.exists(tfile_name):
        os.unlink(tfile_name)  # Supprimer le fichier temporaire
        """