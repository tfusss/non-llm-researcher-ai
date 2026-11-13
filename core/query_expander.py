from datetime import date

ASPECTS = ["thực trạng", "nguyên nhân", "giải pháp", "số liệu thống kê",
           "so sánh", "xu hướng", "tác động"]

def expand(question: str, n: int = 4) -> list[str]:
    qs = [question] + [f"{question} {a}" for a in ASPECTS[: max(n - 1, 0)]]
    qs.append(f"{question} {date.today().year}")   # ưu tiên thông tin mới
    return list(dict.fromkeys(qs))[: n + 1]
