from .vectorizer import cosine

def mmr(rel: list[float], vecs: list[dict], k: int, lam: float) -> list[int]:
    chosen, cand = [], list(range(len(rel)))
    while cand and len(chosen) < k:
        def score(i):
            red = max((cosine(vecs[i], vecs[j]) for j in chosen), default=0.0)
            return lam * rel[i] - (1 - lam) * red
        best = max(cand, key=score)
        chosen.append(best)
        cand.remove(best)
    return chosen
