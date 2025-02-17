export default function ResultsPage({ image, onBack }) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
        <h1 className="text-4xl font-bold text-blue-500">Résultat de la Prédiction</h1>
  
        {image ? (
          <div className="mt-4">
            <img src={image} alt="Prediction Result" className="max-w-full max-h-[600px] rounded-lg shadow-lg" />
          </div>
        ) : (
          <p className="text-red-500 mt-4">❌ Erreur : Aucun résultat disponible.</p>
        )}
  
        <button onClick={onBack} className="mt-6 bg-gray-700 px-4 py-2 rounded-md text-white hover:bg-gray-800 transition">
          🔙 Retour
        </button>
      </div>
    );
  }
  