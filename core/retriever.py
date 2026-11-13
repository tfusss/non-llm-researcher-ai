from collections import Counter
from math import log

class BM25:
    def __init__(self, docs: list[list[str]], k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.len = [len(d) for d in docs]
        self.avg = (sum(self.len) / len(docs)) if docs else 1.0
        n_docs = len(docs)
        df = Counter()
        for c in self.tf:
            df.update(c.keys())
        self.idf = {t: log((n_docs - n + 0.5) / (n + 0.5) + 1) for t, n in df.items()}

    def score(self, query: list[str]) -> list[float]:
        q = set(query)
        out = []
        for tf, ln in zip(self.tf, self.len):
            s = 0.0
            for t in q:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (
                        f + self.k1 * (1 - self.b + self.b * ln / self.avg))
            out.append(s)
        return out
