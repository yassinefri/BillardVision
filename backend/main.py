from ultralytics import YOLO
import cv2
import os
import math

# Charger le modèle YOLO (remplace par ton propre modèle)
model = YOLO('train/weights/best.pt')

# Chemin de test (remplace par une vraie image)
image_path = "../train/model/test/images/3_jpg.rf.6f56e99727a35aa708be9de09466337a.jpg"

# Vérifier si l'image existe
if not os.path.exists(image_path):
    print(f"⚠️ Erreur : L'image '{image_path}' n'existe pas.")
    exit()

# Charger l'image avec OpenCV
image = cv2.imread(image_path)

# Appliquer YOLO pour la détection des objets
results = model(image)

# Vérifier les résultats bruts
print("✅ Résultats YOLO obtenus :")
print(results)

# Extraire les annotations
annotations = []
for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordonnées bbox
        conf = float(box.conf[0])  # Confiance
        cls = int(box.cls[0])  # Classe détectée
        class_name = model.names[cls]  # Nom de la classe

        # Stocker les données
        annotation = {
            "class_id": cls,
            "class_name": class_name,
            "confidence": conf,
            "bounding_box": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        }
        annotations.append(annotation)

        # Afficher dans le terminal
        print(f"📌 Détection : {class_name} ({conf:.2f}) - BBox: [{x1}, {y1}, {x2}, {y2}]")

# Vérifier si des objets ont été détectés
if not annotations:
    print("❌ Aucune détection trouvée.")

# Dessiner les bounding boxes sur l'image
for ann in annotations:
    x1, y1, x2, y2 = ann["bounding_box"].values()
    class_name = ann["class_name"]
    conf = ann["confidence"]

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(image, f"{class_name} {conf:.2f}", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Sauvegarder l'image annotée
cv2.imwrite("output.jpg", image)

print("✅ Image annotée sauvegardée sous 'output.jpg'")





# Récupérer les coordonnées des objets
bille_blanche = None
billards = []
poches = []

for ann in annotations:
    if ann["class_name"] == "mom":  # Bille blanche
        bille_blanche = ann["bounding_box"]
    elif ann["class_name"] == "son":  # Autres billes
        billards.append(ann["bounding_box"])
    elif ann["class_name"] == "pockw":  # Poches
        poches.append(ann["bounding_box"])

# Fonction pour calculer la distance entre deux points
def distance(p1, p2):
    return math.sqrt((p1["x1"] - p2["x1"]) ** 2 + (p1["y1"] - p2["y1"]) ** 2)

# Vérifier si un chemin est dégagé (naïf, à améliorer avec des intersections)
def is_path_clear(start, end, obstacles):
    for obs in obstacles:
        if obs["x1"] > min(start["x1"], end["x1"]) and obs["x1"] < max(start["x1"], end["x1"]):
            if obs["y1"] > min(start["y1"], end["y1"]) and obs["y1"] < max(start["y1"], end["y1"]):
                return False  # Un obstacle bloque le chemin
    return True

# Trouver la meilleure bille à jouer
meilleur_coup = None
meilleure_distance = float("inf")

for bille in billards:
    dist_blanche = distance(bille_blanche, bille)
    
    # Vérifier si une poche est accessible depuis cette bille
    for poche in poches:
        if is_path_clear(bille, poche, billards):
            dist_poche = distance(bille, poche)
            score = dist_blanche + dist_poche  # Distance totale à parcourir
            
            if score < meilleure_distance:
                meilleure_distance = score
                meilleur_coup = {
                    "bille_a_taper": bille,
                    "poche_cible": poche,
                    "distance_totale": score
                }

# Afficher la recommandation
if meilleur_coup:
    print("\n✅ Meilleure bille à jouer :")
    print(f"🎯 Bille à viser : {meilleur_coup['bille_a_taper']}")
    print(f"🕳️ Poche cible : {meilleur_coup['poche_cible']}")
    print(f"📏 Distance totale estimée : {meilleur_coup['distance_totale']:.2f}")
else:
    print("❌ Aucun coup optimal trouvé.")


import cv2

# Charger l'image annotée
image = cv2.imread("output.jpg")

# Convertir les coordonnées en tuples pour OpenCV
def get_center(bbox):
    """Renvoie le centre d'une bbox"""
    return ((bbox['x1'] + bbox['x2']) // 2, (bbox['y1'] + bbox['y2']) // 2)

def to_tuple(bbox):
    return (bbox['x1'], bbox['y1']), (bbox['x2'], bbox['y2'])

# Dessiner la bille blanche en bleu 🔵
cv2.rectangle(image, *to_tuple(bille_blanche), (255, 0, 0), 2)

# Dessiner la meilleure bille à jouer en jaune 🟡
cv2.rectangle(image, *to_tuple(meilleur_coup['bille_a_taper']), (0, 255, 255), 3)

# Dessiner la poche cible en rouge 🔴
cv2.rectangle(image, *to_tuple(meilleur_coup['poche_cible']), (0, 0, 255), 3)

# Récupérer les centres des objets détectés
centre_blanche = get_center(bille_blanche)
centre_bille = get_center(meilleur_coup['bille_a_taper'])
centre_poche = get_center(meilleur_coup['poche_cible'])

# Tracer une ligne entre le centre de la bille blanche et le centre de la bille cible
cv2.line(image, centre_blanche, centre_bille, (255, 255, 255), 2)

# Tracer une ligne entre le centre de la bille cible et le centre de la poche
cv2.line(image, centre_bille, centre_poche, (255, 255, 255), 2)

# Sauvegarder l'image annotée finale
cv2.imwrite("final_output.jpg", image)
print("✅ Image finale annotée sauvegardée sous 'final_output.jpg'")

