from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Ajout de CORS
from ultralytics import YOLO
import cv2
import numpy as np
import base64

app = Flask(__name__)
CORS(app)  # ✅ Active CORS pour toutes les routes

# Chargement du modèle YOLO
model = YOLO("train/weights/best.pt")  # Chemin correct vers le modèle

@app.route('/detect', methods=['POST'])
def detect():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier reçu"}), 400
    
    file = request.files['file']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)

    results = model(image)
    
    # Génération d'une image annotée
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            label = model.names[int(box.cls[0])]
            conf = round(float(box.conf[0]), 2)

            # Dessiner les boîtes et labels
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(image, f"{label} {conf}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode("utf-8")

    return jsonify({"image": encoded_image})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
