import { API_URL } from "../config";
import PageHero from "../components/PageHero";
import diseaseHeroImg from "../assets/images/samp4.jpg";
import React, { useState } from "react";

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

const tabs = [
  { key: "details", label: "Details" },
  { key: "treatment", label: "Treatment" },
  { key: "prevention", label: "Prevention" },
] as const;

export default function CropDiseaseDetection() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<
    "details" | "treatment" | "prevention"
  >("details");
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
      formData.append("image", file);

      const response = await fetch(`${API_URL}/detector/detect`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to detect disease");
      }

      const dataFromBackend = await response.json();

      setResult({
        disease: dataFromBackend.disease,
        confidence: dataFromBackend.confidence,
        message: dataFromBackend.description,
        treatment: dataFromBackend.treatment,
        prevention: dataFromBackend.preventive_measures,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Error detecting disease");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHero
        image={diseaseHeroImg}
        imageStyle="texture"
        title="Disease Detection"
        subtitle="Upload a clear photo of a single leaf to identify likely diseases, with treatment and prevention advice."
      />
      <div className="page">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <form onSubmit={handleSubmit} className="card p-5">
              <label
                htmlFor="leaf-image"
                className="flex min-h-[16rem] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-stone-300 bg-stone-50 p-4 text-center transition-colors hover:border-primary/50"
              >
                {previewUrl ? (
                  <img
                    src={previewUrl}
                    alt="Uploaded preview"
                    className="max-h-72 rounded-md object-contain"
                  />
                ) : (
                  <>
                    <span className="text-sm font-medium text-stone-800">
                      Click to choose an image
                    </span>
                    <span className="muted mt-1">JPG or PNG</span>
                  </>
                )}
              </label>
              <input
                id="leaf-image"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="sr-only"
              />

              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <span className="muted truncate">
                  {file ? file.name : "No file selected"}
                </span>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary"
                >
                  {loading ? "Analysing…" : "Detect disease"}
                </button>
              </div>
              {error && <p className="alert-error mt-4">{error}</p>}
            </form>

            {result && (
              <div className="card">
                <div className="flex border-b border-stone-200 px-5">
                  {tabs.map((t) => (
                    <button
                      key={t.key}
                      onClick={() => setActiveTab(t.key)}
                      className={`-mb-px border-b-2 px-3 py-3 text-sm font-medium transition-colors ${
                        activeTab === t.key
                          ? "border-primary text-primary"
                          : "border-transparent text-stone-500 hover:text-stone-800"
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>

                <div className="p-5 text-sm leading-relaxed text-stone-700">
                  {activeTab === "details" && (
                    <>
                      <div className="flex flex-wrap items-baseline justify-between gap-2">
                        <h3 className="text-lg font-semibold text-stone-900">
                          {result.disease.replace(/_+/g, " ")}
                        </h3>
                        <span className="font-medium text-primary">
                          {(result.confidence * 100).toFixed(1)}% confidence
                        </span>
                      </div>
                      {result.message && (
                        <p className="mt-3">{result.message}</p>
                      )}
                    </>
                  )}
                  {activeTab === "treatment" && (
                    <>
                      <h3 className="font-semibold text-stone-900">
                        How to treat
                      </h3>
                      <p className="mt-2">
                        {result.treatment ||
                          "Treatment information not available."}
                      </p>
                    </>
                  )}
                  {activeTab === "prevention" && (
                    <>
                      <h3 className="font-semibold text-stone-900">
                        How to prevent
                      </h3>
                      <p className="mt-2">
                        {result.prevention ||
                          "Prevention information not available."}
                      </p>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>

          <aside className="card h-fit p-5">
            <h2 className="font-semibold text-stone-900">
              Common crop diseases
            </h2>
            <ul className="mt-3 divide-y divide-stone-100">
              {commonDiseases.map((disease) => {
                const open = expandedDisease === disease.name;
                return (
                  <li key={disease.name}>
                    <button
                      onClick={() =>
                        setExpandedDisease(open ? null : disease.name)
                      }
                      className="w-full py-3 text-left"
                      aria-expanded={open}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-sm font-medium text-stone-900">
                          {disease.name}
                        </span>
                        <span className="text-stone-400">
                          {open ? "−" : "+"}
                        </span>
                      </div>
                      <p className="mt-0.5 text-sm text-stone-500">
                        {disease.description}
                      </p>
                      {open && (
                        <p className="mt-2 text-sm text-stone-700">
                          {disease.more}
                        </p>
                      )}
                    </button>
                  </li>
                );
              })}
            </ul>
          </aside>
        </div>
      </div>
    </div>
  );
}
