import cv2
import os
import time

def video_deja_traitee(video):
    nom_fichier_journal = "journal.txt" 
    if not os.path.exists(nom_fichier_journal):
        return False
    with open(nom_fichier_journal, "r") as fichier:
        for ligne in fichier:
            if video in ligne:
                return True
    return False

def ajuster_luminosite(image, valeur=30): #Augmente la luminosité de l'image en ajoutant une valeur constante à tous les pixels."
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    lim = 255 - valeur
    v[v > lim] = 255
    v[v <= lim] += valeur
    hsv_final = cv2.merge((h, s, v))
    image_finale = cv2.cvtColor(hsv_final, cv2.COLOR_HSV2BGR)
    return image_finale

def enregistrer_configuration_et_journal(video_traitee, intervalle): #Enregistre les détails des vidéos traitées dans un fichier journal pour éviter de les retraiter.
    nom_fichier_journal = "journal.txt"  
    with open(nom_fichier_journal, "a") as fichier:
        fichier.write(f"Vidéo traitée: {video_traitee}, Intervalle de capture: {intervalle} secondes, Date d'exécution: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

def extraire_images_dossier_videos(dossier_videos, dossier_images, intervalle=1):
    if not os.path.exists(dossier_images):
        os.makedirs(dossier_images)

    for fichier in os.listdir(dossier_videos):
        if fichier.endswith((".mp4", ".avi")) and not video_deja_traitee(fichier):
            chemin_video = os.path.join(dossier_videos, fichier)
            cap = cv2.VideoCapture(chemin_video)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = 0
            success = True
            
            while success:
                success, frame = cap.read()
                if not success or frame is None:
                    break
                
                if frame_count % (int(fps) * intervalle) == 0:
                    frame_eclaircie = ajuster_luminosite(frame)
                    nom_image = f"image_{time.strftime('%Y%m%d_%H%M%S')}_{frame_count}.jpg"
                    chemin_image = os.path.join(dossier_images, nom_image)
                    cv2.imwrite(chemin_image, frame_eclaircie)
                
                frame_count += 1
            
            cap.release()
            enregistrer_configuration_et_journal(fichier, intervalle)
    
    print("Extraction et éclaircissement terminés.")

dossier_videos = 'VDS'  # Corrigez le nom si nécessaire
dossier_images = 'dataset/Val/images'  # Le dossier où vous souhaitez sauvegarder les images extraites
extraire_images_dossier_videos(dossier_videos, dossier_images, intervalle=1)