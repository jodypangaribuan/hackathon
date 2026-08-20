import type { AnalyzeHit, AnalyzeResult, AspectKey } from "./types";
import { ASPECT_LABEL } from "./format";

const POLARITY_TO_SENTIMENT = {
  positive: "positif",
  negative: "negatif",
  neutral: "netral",
} as const;

interface ModelPrediction {
  aspect: string;
  aspect_probability: number;
  polarity: keyof typeof POLARITY_TO_SENTIMENT;
  polarity_probability: number | null;
  severity: string | null;
}

interface ModelPredictResponse {
  model_version: string;
  aspect_model: string;
  polarity_version: string;
  text: string;
  predictions: ModelPrediction[];
}

/**
 * Panggil service inference FastAPI (`POST /predict-review`) lalu petakan
 * respons-nya ke bentuk `AnalyzeResult` yang dikonsumsi AnalyzerClient.
 */
export async function analyzeWithModel(
  text: string,
  baseUrl: string,
  signal?: AbortSignal,
): Promise<AnalyzeResult> {
  const started = Date.now();
  const response = await fetch(`${baseUrl}/predict-review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
    cache: "no-store",
    signal,
  });
  const latencyMs = Date.now() - started;

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`Inference service error ${response.status}: ${detail}`);
  }

  const payload = (await response.json()) as ModelPredictResponse;
  const hits: AnalyzeHit[] = payload.predictions
    .map((prediction) => {
      const aspect = prediction.aspect as AspectKey;
      return {
        aspect,
        label: ASPECT_LABEL[aspect] ?? prediction.aspect,
        sentiment: POLARITY_TO_SENTIMENT[prediction.polarity] ?? "netral",
        matchScore: prediction.aspect_probability,
        confidence: prediction.aspect_probability,
        snippets: [],
      };
    })
    .sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0));

  return {
    mode: "production",
    method: "tfidf_aspect_lexical_polarity",
    modelVersion: payload.aspect_model,
    scoreType: "model_confidence",
    text: payload.text,
    hits,
    latencyMs,
    note: "Model produksi: deteksi aspek TF-IDF + polarity leksikal. Severity tidak tersedia. Input tidak disimpan dan tidak mengubah prioritas destinasi.",
  };
}
