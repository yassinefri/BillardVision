from flask import Flask, request, jsonify
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import base64
import math

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes cross-origin (React, etc.)

# Charger le modèle YOLO entraîné.
# Assure-toi que "train/weights/best.pt" pointe vers le chemin correct
model = YOLO("train/weights/best.pt")

def get_center(x1, y1, x2, y2):
    """
    Calcule le centre (cx, cy) d'une bounding box donnée (x1, y1, x2, y2).
    """
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return (cx, cy)

def distance(p1, p2):
    """
    Distance euclidienne entre deux points p1=(x, y) et p2=(x, y).
    """
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

@app.route('/detect', methods=['POST'])
def detect():
    """
    Endpoint /detect : Reçoit une image, détecte mom (bille blanche),
    son (autres billes) et pockw (poches), calcule la meilleure
    bille et poche à viser, annote l'image et la renvoie en base64.
    """
    # Vérifier qu'un fichier a bien été envoyé
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400
    
    # Lire l'image depuis la requête
    file = request.files['file']
    raw_data = file.read()
    image = cv2.imdecode(np.frombuffer(raw_data, np.uint8), cv2.IMREAD_COLOR)

    # Lancer YOLO
    results = model(image)

    # Variables pour stocker les centres et bounding boxes
    mom_center = None
    mom_bbox = None

    son_centers = []
    son_bboxes = []

    pockw_centers = []
    pockw_bboxes = []

    # 1) Parcourir toutes les détections
    for r in results:
        for box in r.boxes:
            # Récupérer coordonnées (x1, y1, x2, y2)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            label = model.names[cls_id]
            conf = float(box.conf[0])

            # Dessiner la bbox par défaut (en vert)
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image, f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (0, 255, 0), 2
            )

            # Calculer le centre de la bbox
            cx, cy = get_center(x1, y1, x2, y2)

            # Classer selon le label
            if label == "mom":
                mom_center = (cx, cy)
                mom_bbox = (x1, y1, x2, y2)
            elif label == "son":
                son_centers.append((cx, cy))
                son_bboxes.append((x1, y1, x2, y2))
            elif label == "pockw":
                pockw_centers.append((cx, cy))
                pockw_bboxes.append((x1, y1, x2, y2))

    # 2) Calcul de la meilleure combinaison (bille son + poche)
    best_score = float('inf')
    best_son_index = None
    best_pockw_index = None

    # On ne calcule que si la bille blanche (mom) est trouvée
    if mom_center is not None:
        for i, son_c in enumerate(son_centers):
            for j, pock_c in enumerate(pockw_centers):
                dist_blanche_son = distance(mom_center, son_c)
                dist_son_poche = distance(son_c, pock_c)
                score = dist_blanche_son + dist_son_poche

                if score < best_score:
                    best_score = score
                    best_son_index = i
                    best_pockw_index = j

    # 3) Annoter la meilleure bille + poche
    if best_son_index is not None and best_pockw_index is not None:
        # Bille blanche en bleu (si détectée)
        if mom_bbox:
            x1_m, y1_m, x2_m, y2_m = mom_bbox
            cv2.rectangle(image, (x1_m, y1_m), (x2_m, y2_m), (255, 0, 0), 2)

        # Bille cible en jaune
        x1_s, y1_s, x2_s, y2_s = son_bboxes[best_son_index]
        cv2.rectangle(image, (x1_s, y1_s), (x2_s, y2_s), (0, 255, 255), 2)

        # Poche en rouge
        x1_p, y1_p, x2_p, y2_p = pockw_bboxes[best_pockw_index]
        cv2.rectangle(image, (x1_p, y1_p), (x2_p, y2_p), (0, 0, 255), 2)

        # Tracer les lignes blanches (blanche→bille, bille→poche)
        chosen_son_center = son_centers[best_son_index]
        chosen_pock_center = pockw_centers[best_pockw_index]
        
        # Ligne : mom_center -> chosen_son_center
        if mom_center is not None:
            cv2.line(image, mom_center, chosen_son_center, (255, 255, 255), 2)
        # Ligne : chosen_son_center -> chosen_pock_center
        cv2.line(image, chosen_son_center, chosen_pock_center, (255, 255, 255), 2)

    # 4) Convertir l’image annotée en base64
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    # 5) Retour JSON avec l'image encodée
    return jsonify({"image": encoded_image})

if __name__ == '__main__':
    # Écoute sur toutes les IP, port 8000 (configurable)
    app.run(host="0.0.0.0", port=8000, debug=True)
