# Violence Detection Application

## Description

Ce projet est une application de détection de violence utilisant un modèle YOLOv5 personnalisé. L'application utilise une webcam pour capturer des flux vidéo en direct et détecte les actes de violence. Lorsqu'un acte de violence est détecté, l'application envoie une alerte par email avec les images capturées.

## Fonctionnalités

- Détection de violence en temps réel à partir de la webcam.
- Envoi d'alertes par email lorsqu'une violence est détectée.
- Interface utilisateur avec Streamlit pour l'upload de vidéos et la visualisation des résultats.
- Gestion des utilisateurs avec un système de connexion sécurisé.

## Prérequis

- Python 3.x
- MySQL
- Les bibliothèques Python suivantes :
  - streamlit
  - sqlalchemy
  - hashlib
  - opencv-python
  - torch
  - smtplib
  - email
  - numpy
  - tempfile

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/HichemMhadhbi/Detection-Violence-et-analyse-visuelle.git
cd Detection-Violence-et-analyse-visuelle

2. Installer les dépendances
Utilisez pip pour installer les dépendances nécessaires :
pip install -r requirements.txt

3. Configurer la base de données MySQL
Créez une base de données MySQL et exécutez le script SQL suivant pour créer la table admin :

CREATE DATABASE streamlit_db;
USE streamlit_db;

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    adminName VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

4. Ajouter un utilisateur administrateur
Ajoutez un utilisateur administrateur dans la table admin avec un mot de passe haché (par exemple avec SHA256) :
import hashlib

admin_name = 'admin'
password = 'your_password'
hashed_password = hashlib.sha256(password.encode()).hexdigest()
query = f"INSERT INTO admin (adminName, password) VALUES ('{admin_name}', '{hashed_password}')"
# Exécutez cette requête dans votre base de données

5. Configurer les informations d'email
Modifiez les informations d'email dans votre fichier principal (app.py ou LoginViolence.py) :

python
Copy code
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_email_password"

6. Charger le modèle YOLOv5
Assurez-vous que le modèle YOLOv5 est disponible à l'emplacement spécifié dans votre code. Vous pouvez télécharger un modèle pré-entraîné ou utiliser votre propre modèle entraîné :

python
Copy code
MODEL_WEIGHTS_PATH = os.path.join('yolov5', 'runs', 'train', 'exp13', 'weights', 'last.pt')

# Utilisation
1. Démarrer l'application
Exécutez le script principal pour démarrer l'application Streamlit :
streamlit run LoginViolence.py

2. Connexion
Accédez à l'interface de connexion et entrez vos informations d'identification administrateur pour accéder à l'application.

3. Détection de violence
Téléchargez une vidéo ou utilisez la webcam pour démarrer la détection de violence.
Les images capturées seront stockées dans le dossier CaptureStreamlit et une alerte par email sera envoyée si de la violence est détectée.

4. Visualisation des images
Utilisez la barre latérale pour accéder aux dossiers contenant les images capturées.
Cliquez sur un dossier pour voir les images capturées lors des détections de violence.
Contribuer
Les contributions sont les bienvenues ! Veuillez ouvrir une issue ou soumettre une pull request pour discuter des modifications que vous souhaitez apporter.


Contact
Pour toute question ou suggestion, veuillez contacter 

Linkedin: https://www.linkedin.com/in/mhadhbi-hichem-684a00235/
Facebook: https://www.facebook.com/hichem.mhadhbi.5/
Mail: hiichem.mhadhbi@gmail.com.