from typing import List, Tuple
from loguru import logger


class SentimentAnalyzer:
    """
    Lightweight sentiment analyzer using keyword heuristics.
    Falls back gracefully if transformers is unavailable.
    For production: swap with HuggingFace pipeline.
    """

    POSITIVE_WORDS = {
        "excellent", "great", "amazing", "good", "best", "love", "perfect",
        "fantastic", "awesome", "superb", "outstanding", "wonderful", "happy",
        "satisfied", "recommend", "quality", "fast", "reliable", "durable",
    }
    NEGATIVE_WORDS = {
        "bad", "poor", "terrible", "worst", "hate", "broken", "defective",
        "slow", "cheap", "fake", "disappointed", "useless", "waste", "return",
        "refund", "damaged", "horrible", "awful", "pathetic", "fraud",
    }

    def analyze(self, text: str) -> Tuple[str, float]:
        """Returns (sentiment, confidence) where sentiment is positive/negative/neutral."""
        words = text.lower().split()
        pos = sum(1 for w in words if w in self.POSITIVE_WORDS)
        neg = sum(1 for w in words if w in self.NEGATIVE_WORDS)

        if pos > neg:
            confidence = min(0.5 + (pos - neg) * 0.1, 0.99)
            return "positive", round(confidence, 2)
        elif neg > pos:
            confidence = min(0.5 + (neg - pos) * 0.1, 0.99)
            return "negative", round(confidence, 2)
        return "neutral", 0.5

    def extract_keywords(self, texts: List[str], sentiment: str) -> List[str]:
        """Extract most common sentiment-aligned keywords."""
        word_set = self.POSITIVE_WORDS if sentiment == "positive" else self.NEGATIVE_WORDS
        freq: dict = {}
        for text in texts:
            for word in text.lower().split():
                if word in word_set:
                    freq[word] = freq.get(word, 0) + 1
        return [w for w, _ in sorted(freq.items(), key=lambda x: -x[1])[:5]]


# Lazy-load HuggingFace — USE_HF=True only if transformers is installed.
# Actual model is loaded on first use, not at startup.
try:
    from importlib.util import find_spec
    USE_HF = find_spec("transformers") is not None
except Exception:
    USE_HF = False

_hf_sentiment = None


def _get_hf_pipeline():
    global _hf_sentiment
    if _hf_sentiment is None:
        try:
            from transformers import pipeline as hf_pipeline
            _hf_sentiment = hf_pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                top_k=1,
            )
            logger.info("HuggingFace sentiment model loaded")
        except Exception as e:
            logger.warning(f"HuggingFace load failed, using keyword analyzer: {e}")
            _hf_sentiment = None
    return _hf_sentiment


def _hf_analyze(text: str) -> Tuple[str, float]:
    pipe = _get_hf_pipeline()
    if pipe is None:
        return SentimentAnalyzer().analyze(text)
    result = pipe(text[:512])[0][0]
    label = result["label"].lower()
    if "pos" in label:
        return "positive", result["score"]
    elif "neg" in label:
        return "negative", result["score"]
    return "neutral", result["score"]
