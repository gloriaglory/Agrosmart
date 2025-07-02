import React, { useState } from "react";
import { Info, Bug, ShieldCheck } from "lucide-react";

type DetectionResponse = {
  disease: string;
  confidence: number;
  message?: string;
  treatment?: string;
  prevention?: string;
};

const commonDiseases = [
  {
    name: "Late Blight",
    description: "Caused by water mold, affects potatoes and tomatoes.",
    more: "Late blight is a devastating disease caused by Phytophthora infestans. It thrives in wet, cool climates.",
  },
  {
    name: "Leaf Spot",
    description: "Fungal or bacterial disease forming spots on leaves.",
    more: "Leaf spot diseases are common in humid regions and can reduce photosynthesis by damaging leaf tissue.",
  },
  {
    name: "Powdery Mildew",
    description: "White powder-like coating on leaves.",
    more: "Caused by fungi, this disease spreads quickly in dry climates with poor air circulation.",
  },
];

export default function CropDiseaseDetection() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"details" | "treatment" | "prevention">("details");
  const [expandedDisease, setExpandedDisease] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setResult(null);
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      setPreviewUrl(URL.createObjectURL(selectedFile));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  if (!file) {
    setError("Please upload an image.");
    return;
  }

  setLoading(true);
  setError(null);
  setResult(null);
  setActiveTab("details");

  try {
    const formData = new FormData();
    formData.append("image", file);  // key changed from 'file' to 'image'

    const response = await fetch("http://localhost:8000/detector/detect", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to detect disease");
    }

    const dataFromBackend = await response.json();

    const data: DetectionResponse = {
      disease: dataFromBackend.disease,
      confidence: dataFromBackend.confidence,
      message: dataFromBackend.description,
      treatment: dataFromBackend.treatment,
      prevention: dataFromBackend.preventive_measures,
    };

    setResult(data);
  } catch (err: unknown) {
    if (err instanceof Error) {
      setError(err.message);
    } else {
      setError("Error detecting disease");
    }
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="container mx-auto p-6">
      {/* Full width top header */}
      <div className="bg-green-100 rounded-lg p-6 mb-8 text-center shadow">
        <h1 className="text-3xl font-extrabold mb-2 text-green-900">Crop Disease Detector</h1>
        <p className="text-green-800">
          Upload a picture of your crop and let our AI detect possible diseases.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8 items-stretch">
        {/* Left side: Upload + Results */}
        <div className="lg:w-2/3">
          <form onSubmit={handleSubmit} className="mb-6">
            <input type="file" accept="image/*" onChange={handleFileChange} className="mb-4" />

            {previewUrl ? (
              <img
                src={previewUrl}
                alt="Uploaded Preview"
                className="mb-4 rounded border shadow-sm max-h-64"
              />
            ) : (
              <div className="mb-4 rounded border border-dashed border-gray-400 p-10 text-center text-gray-500">
                No image uploaded yet
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? "Detecting..." : "Detect Disease"}
            </button>
          </form>

          {error && <p className="text-red-600 mb-4">{error}</p>}

          {result && (
            <div className="bg-white rounded-lg shadow-md border p-4">
              <div className="flex space-x-4 border-b mb-4">
                <button
                  className={`px-4 py-2 ${
                    activeTab === "details" ? "border-b-2 border-green-600 font-semibold" : ""
                  }`}
                  onClick={() => setActiveTab("details")}
                >
                  <Info className="inline w-4 h-4 mr-1" /> Details
                </button>
                <button
                  className={`px-4 py-2 ${
                    activeTab === "treatment" ? "border-b-2 border-green-600 font-semibold" : ""
                  }`}
                  onClick={() => setActiveTab("treatment")}
                >
                  <Bug className="inline w-4 h-4 mr-1" /> Treatment
                </button>
                <button
                  className={`px-4 py-2 ${
                    activeTab === "prevention" ? "border-b-2 border-green-600 font-semibold" : ""
                  }`}
                  onClick={() => setActiveTab("prevention")}
                >
                  <ShieldCheck className="inline w-4 h-4 mr-1" /> Prevention
                </button>
              </div>

              <div>
                {activeTab === "details" && (
                  <div>
                    <h3 className="text-xl font-bold mb-2">{result.disease}</h3>
                    <p>
                      <strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%
                    </p>
                    {result.message && <p className="mt-2">{result.message}</p>}
                  </div>
                )}
                {activeTab === "treatment" && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">How to Handle / Cure</h3>
                    <p>{result.treatment || "Treatment information not available."}</p>
                  </div>
                )}
                {activeTab === "prevention" && (
                  <div>
                    <h3 className="text-lg font-semibold mb-2">How to Prevent</h3>
                    <p>{result.prevention || "Prevention information not available."}</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right side*/}
        <div className="lg:w-1/3 bg-gray-50 border rounded-lg shadow p-4 h-full overflow-auto">
          <h3 className="text-xl font-bold mb-4 text-green-800">Common Crop Diseases</h3>
          <ul className="space-y-4">
            {commonDiseases.map((disease) => (
              <li
                key={disease.name}
                className="cursor-pointer hover:bg-green-50 p-2 rounded border"
                onClick={() =>
                  setExpandedDisease(expandedDisease === disease.name ? null : disease.name)
                }
              >
                <p className="font-semibold text-green-700">{disease.name}</p>
                <p className="text-sm text-gray-600">{disease.description}</p>
                {expandedDisease === disease.name && (
                  <p className="mt-2 text-sm text-gray-700">{disease.more}</p>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
