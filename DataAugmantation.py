import cv2
import numpy as np
import os

# Chemins des dossiers pour les images et les annotations
images_path = 'data/images'
labels_path = 'data/labels'
aug_images_path = 'dataset/images'
aug_labels_path = 'dataset/labels'
os.makedirs(aug_images_path, exist_ok=True)
os.makedirs(aug_labels_path, exist_ok=True)

# Ajustement des labels avec une perturbation
def perturb_labels(labels_path, delta=0.01):
    with open(labels_path, 'r') as file:
        lines = file.readlines()
    
    new_lines = []
    for line in lines:
        parts = line.strip().split()
        class_id = parts[0]  # Garder l'identifiant de classe intact
        x_center, y_center, width, height = map(float, parts[1:])
        # Ajouter une petite perturbation aux coordonnées x, y, width, height
        x_center += np.random.uniform(-delta, delta)
        y_center += np.random.uniform(-delta, delta)
        width += np.random.uniform(-delta, delta)
        height += np.random.uniform(-delta, delta)
        # Assurez-vous que les coordonnées restent entre 0 et 1
        x_center = np.clip(x_center, 0, 1)
        y_center = np.clip(y_center, 0, 1)
        width = np.clip(width, 0, 1)
        height = np.clip(height, 0, 1)
        new_line = f"{class_id} {x_center} {y_center} {width} {height}\n"
        new_lines.append(new_line)
    
    return new_lines

# Traitement de chaque fichier image
for image_file in os.listdir(images_path):
    if image_file.endswith('.jpg'):
        # Image et chemin d'annotation
        image_path = os.path.join(images_path, image_file)
        label_path = os.path.join(labels_path, image_file.replace('.jpg', '.txt'))
        
        # Lecture de l'image et ajustement de couleur
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertit de BGR en RGB
        image = cv2.convertScaleAbs(image, alpha=1, beta=-50)  # Réduit la luminosité
        image = cv2.GaussianBlur(image, (5, 5), 0)  # Applique un flou

        # Sauvegarde de l'image transformée
        new_image_path = os.path.join(aug_images_path, f"aug_{image_file}")
        cv2.imwrite(new_image_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))  # Convertit de RGB en BGR pour la sauvegarde
        
        # Ajustement des labels
        new_labels = perturb_labels(label_path, delta=0.01)
        new_label_path = os.path.join(aug_labels_path, f"aug_{image_file.replace('.jpg', '.txt')}")
        with open(new_label_path, 'w') as file:
            file.writelines(new_labels)
