"""TF-IDF + cosine-similarity ranking over PoshanGuide records."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _text(r):
    return " ".join(str(r.get(k, "")) for k in ("guideline_title", "key_advice", "number_limit", "target_group"))


class SmartSearch:
    def __init__(self, records):
        self.records = records
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vec.fit_transform([_text(r) for r in records])

    def rank(self, query, top_k=5):
        if not query.strip():
            return []
        scores = cosine_similarity(self.vec.transform([query]), self.matrix).ravel()
        order = scores.argsort()[::-1][:top_k]
        return [{**self.records[i], "score": round(float(scores[i]), 4)} for i in order if scores[i] > 0]
