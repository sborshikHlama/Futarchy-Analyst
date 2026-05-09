"""
Sentiment analysis via HuggingFace Inference API.
No local model downloads — all inference is remote.

Models:
  social  → ElKulako/cryptobert         (Telegram, crypto social media)
  finance → StephanAkkerman/FinTwitBERT-sentiment  (financial tweets fallback)
  news    → ProsusAI/finbert            (news snippets from Apify)
  twitter → cardiffnlp/twitter-roberta-base-sentiment-latest  (Twitter fallback if no Grok)
"""

import os, time, logging, requests
from typing import Literal

log = logging.getLogger(__name__)

HF_TOKEN   = os.getenv("HF_TOKEN", "")
HF_API_URL = "https://api-inference.huggingface.co/models"

MODELS = {
    "social":   "ElKulako/cryptobert",
    "finance":  "StephanAkkerman/FinTwitBERT-sentiment",
    "news":     "ProsusAI/finbert",
    "twitter":  "cardiffnlp/twitter-roberta-base-sentiment-latest",
}

# Unified label map — covers all four models
LABEL_MAP = {
    # ElKulako/cryptobert + FinTwitBERT
    "Bullish": 1.0, "Neutral": 0.0, "Bearish": -1.0,
    "LABEL_2": 1.0, "LABEL_1": 0.0, "LABEL_0": -1.0,
    # ProsusAI/finbert
    "positive": 1.0, "neutral": 0.0, "negative": -1.0,
    # cardiffnlp/twitter-roberta
    "LABEL_2": 1.0, "LABEL_1": 0.0, "LABEL_0": -1.0,
}

MOCK_RESULTS = {
    "social":   {"score": 0.35,  "label": "bullish",  "confidence": 0.78},
    "finance":  {"score": 0.20,  "label": "bullish",  "confidence": 0.71},
    "news":     {"score": -0.10, "label": "neutral",  "confidence": 0.65},
    "twitter":  {"score": 0.15,  "label": "neutral",  "confidence": 0.68},
}


def _call_hf_api(model_id: str, texts: list[str]) -> list[dict]:
    """
    Call HuggingFace Inference API.
    Retries once on 503 (model loading).
    """
    if not HF_TOKEN:
        raise EnvironmentError("HF_TOKEN not set. Add it to .env")

    url  = f"{HF_API_URL}/{model_id}"
    hdrs = {"Authorization": f"Bearer {HF_TOKEN}"}
    body = {"inputs": texts, "options": {"wait_for_model": True}}

    r = requests.post(url, headers=hdrs, json=body, timeout=40)

    if r.status_code == 503:
        log.warning(f"HF model {model_id} loading, retrying in 20s...")
        time.sleep(20)
        r = requests.post(url, headers=hdrs, json=body, timeout=60)

    r.raise_for_status()
    return r.json()


def _parse_response(raw: list) -> list[dict]:
    """
    Normalize HF response — handles both formats:
      [[{label, score}, ...], ...]  ← multi-label per text
      [{label, score}, ...]         ← single label per text
    """
    flat = []
    for item in raw:
        if isinstance(item, list):
            flat.append(max(item, key=lambda x: x["score"]))
        elif isinstance(item, dict):
            flat.append(item)
    return flat


def analyze_batch(
    texts: list[str],
    source_type: Literal["social", "finance", "news", "twitter"] = "social",
) -> dict:
    """
    Run sentiment analysis on a batch of texts.

    Args:
        texts:       list of raw text strings (Telegram posts, news snippets, tweets)
        source_type: which model to use — "social" | "finance" | "news" | "twitter"

    Returns:
        {
          "score":       float  — [-1.0 bearish … +1.0 bullish]
          "label":       str    — "bullish" | "neutral" | "bearish"
          "confidence":  float  — avg model confidence [0, 1]
          "sample_size": int
          "model":       str    — model ID used
        }
    """
    if not texts:
        return {"score": 0.0, "label": "neutral", "confidence": 0.0,
                "sample_size": 0, "model": MODELS[source_type]}

    # Demo mode — return deterministic mock
    if os.getenv("UMIA_ENV", "demo") == "demo":
        mock = MOCK_RESULTS[source_type].copy()
        mock.update({"sample_size": len(texts), "model": MODELS[source_type]})
        return mock

    model_id = MODELS[source_type]
    log.info(f"HF sentiment [{source_type}] → {model_id} ({len(texts)} texts)")

    try:
        raw     = _call_hf_api(model_id, texts[:20])  # cap for speed
        parsed  = _parse_response(raw)

        weighted = [LABEL_MAP.get(r["label"], 0.0) * r["score"] for r in parsed]
        avg_score = sum(weighted) / len(weighted)
        avg_conf  = sum(r["score"] for r in parsed) / len(parsed)

        return {
            "score":       round(avg_score, 3),
            "label":       ("bullish" if avg_score > 0.15
                            else "bearish" if avg_score < -0.15
                            else "neutral"),
            "confidence":  round(avg_conf, 3),
            "sample_size": len(texts),
            "model":       model_id,
        }

    except Exception as e:
        log.error(f"HF sentiment failed ({model_id}): {e}. Returning neutral.")
        return {"score": 0.0, "label": "neutral", "confidence": 0.0,
                "sample_size": len(texts), "model": model_id, "error": str(e)}
