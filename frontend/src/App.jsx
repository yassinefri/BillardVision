import { useState, useRef } from "react";
import Webcam from "react-webcam";

export default function App() {
  const [image, setImage] = useState(null);
  const webcamRef = useRef(null);

  // Fonction pour capturer une photo depuis la webcam
  const capturePhoto = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    setImage(imageSrc);
  };

  // Fonction pour uploader une image depuis le stockage
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
    }
  };

  // Fonction pour supprimer l’image
  const handleDeleteImage = () => {
    setImage(null);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-4xl font-bold text-blue-500 mb-4">YOLO Ball Detection</h1>

      <div className="flex gap-4 mb-4">
        <button onClick={capturePhoto} className="bg-blue-500 px-4 py-2 rounded-md text-white hover:bg-blue-600 transition">
          📸 Prendre une photo
        </button>

        <label className="bg-green-500 px-4 py-2 rounded-md text-white hover:bg-green-600 transition cursor-pointer">
          📂 Uploader une image
          <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
        </label>

        <button onClick={handleDeleteImage} className="bg-red-500 px-4 py-2 rounded-md text-white hover:bg-red-600 transition">
          🗑️ Supprimer l’image
        </button>

        <button className="bg-yellow-500 px-4 py-2 rounded-md text-white hover:bg-yellow-600 transition">
          ✅ Valider
        </button>
      </div>

      {/* Webcam */}
      {!image && (
        <Webcam
          ref={webcamRef}
          screenshotFormat="image/png"
          className="rounded-lg shadow-lg"
        />
      )}

      {/* Image capturée ou uploadée */}
      {image && (
        <div className="mt-4">
          <img src={image} alt="Captured" className="max-w-full max-h-[400px] rounded-lg shadow-lg" />
        </div>
      )}
    </div>
  );
}
