from collections import Counter
from math import log, sqrt

class Tfidf:
    def fit(self, docs: list[list[str]]):
        n = len(docs)
        df = Counter()
        for d in docs:
            df.update(set(d))
        self.idf = {t: log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        return self

    def vec(self, tokens: list[str]) -> dict:
        tf = Counter(tokens)
        w = {t: (1 + log(c)) * self.idf[t] for t, c in tf.items() if t in self.idf}
        norm = sqrt(sum(x * x for x in w.values())) or 1.0
        return {t: x / norm for t, x in w.items()}   # đã chuẩn hóa: dot = cosine

def cosine(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())
