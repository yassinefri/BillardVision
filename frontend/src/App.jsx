import { useState, useRef } from "react";
import ResultsPage from "./ResultsPage";

export default function App() {
  const [image, setImage] = useState(null);
  const [predictedImage, setPredictedImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [viewResults, setViewResults] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // 📷 Capture une photo depuis la webcam
  const capturePhoto = () => {

    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      const file = new File([blob], "photo.jpg", { type: "image/jpeg" });
      setImage(file);
    }, "image/jpeg");
  };

  // 📂 Gestion de l'upload de fichier
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) setImage(file);
  };

  // 🗑️ Suppression de l'image
  const handleDeleteImage = () => {
    setImage(null);
    setPredictedImage(null);
    setViewResults(false);
  };

  // 🔥 Envoi de l'image au backend
  const handleSubmit = async () => {
    if (!image) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("file", image);

    try {
      const response = await fetch("http://35.180.199.30:8000/detect", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Erreur lors de la prédiction");

      const data = await response.json();
      setPredictedImage(`data:image/jpeg;base64,${data.image}`);
      setViewResults(true);
    } catch (error) {
      console.error("Erreur :", error);
    } finally {
      setLoading(false);
    }
  };

  // 🎯 Vérifier si on doit afficher la page des résultats
  if (viewResults && predictedImage) {
    return <ResultsPage image={predictedImage} onBack={() => setViewResults(false)} />;
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <h1 className="text-4xl font-bold text-blue-500">YOLO Ball Detection</h1>

      <div className="flex gap-4 mb-4">
        {/* 📸 Prendre une photo */}
        <button onClick={capturePhoto} className="bg-blue-500 px-4 py-2 rounded-md text-white hover:bg-blue-600 transition">
          📸 Prendre une photo
        </button>

        {/* 📂 Uploader une image */}
        <label className="bg-green-500 px-4 py-2 rounded-md text-white hover:bg-green-600 transition cursor-pointer">
          📂 Uploader une image
          <input type="file" className="hidden" accept="image/*" onChange={handleImageUpload} />
        </label>

        {/* 🗑️ Supprimer l’image */}
        <button onClick={handleDeleteImage} className="bg-red-500 px-4 py-2 rounded-md text-white hover:bg-red-600 transition">
          🗑️ Supprimer l’image
        </button>

        {/* ✅ Valider */}
        <button
          onClick={handleSubmit}
          className={`px-4 py-2 rounded-md text-white transition ${
            loading ? "bg-gray-500 cursor-not-allowed" : "bg-yellow-500 hover:bg-yellow-600"
          }`}
          disabled={loading}
        >
          {loading ? "⏳ Analyse en cours..." : "✅ Valider"}
        </button>
      </div>

      {/* 📷 Webcam */}
      <video ref={videoRef} autoPlay playsInline className="hidden" />
      <canvas ref={canvasRef} className="hidden" />

      {/* 🖼️ Afficher l’image sélectionnée */}
      {image && (
        <div className="mt-4">
          <img src={URL.createObjectURL(image)} alt="Preview" className="max-w-full max-h-[400px] rounded-lg shadow-lg" />
        </div>
      )}
    </div>
  );
}
