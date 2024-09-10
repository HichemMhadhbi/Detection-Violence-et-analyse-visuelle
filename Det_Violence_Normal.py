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

def send_alert_email(image_path):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "hiichem.mhadhbi@gmail.com"
    msg['Subject'] = "Violence detected!"
    body = "Violence was detected. See attached image."
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
    video_folder = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_path = os.path.join(main_folder, video_folder)
    os.makedirs(video_path, exist_ok=True)

    fd, tfile_name = tempfile.mkstemp(suffix=".mp4")
    with os.fdopen(fd, 'wb') as tfile:
        tfile.write(video_file_buffer.read())

    cap = cv2.VideoCapture(tfile_name)
    detected_images = []

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model(frame)
            confidences = results.xyxy[0][:, 4].cpu().numpy()
            labels = results.xyxy[0][:, -1].cpu().numpy()

            frame = np.squeeze(results.render())
            img_name = f"frame_{int(cap.get(cv2.CAP_PROP_POS_FRAMES))}.jpg"
            img_path = os.path.join(video_path, img_name)
            cv2.imwrite(img_path, frame)

            if 1 in labels:
                high_confidence_indices = [i for i, label in enumerate(labels) if label == 1 and confidences[i] >= 0.8]
                for i in high_confidence_indices:
                    detected_images.append((img_path, confidences[i]))

            stframe.image(frame, channels="BGR", use_column_width=True)

        detected_images.sort(key=lambda x: x[1], reverse=True)
        for img_path, _ in detected_images[:3]:
            send_alert_email(img_path)

    finally:
        cap.release()  # Important: libérer la capture vidéo
        os.unlink(tfile_name)  # Nettoyer le fichier temporaire
