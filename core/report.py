def build(question: str, picked: list[tuple], docs: list[dict]) -> str:
    """picked: [(doc_idx, sent_idx, sentence)] theo thứ tự MMR."""
    order = list(dict.fromkeys(d for d, _, _ in picked))
    num = {d: i + 1 for i, d in enumerate(order)}
    lines = [f"# {question}", "", "## Nội dung chính", ""]
    for d, s, text in sorted(picked, key=lambda x: (num[x[0]], x[1])):
        lines.append(f"- {text} [{num[d]}]")
    lines += ["", "## Tài liệu tham khảo", ""]
    for d in order:
        x = docs[d]
        meta = f" ({x['date']})" if x["date"] else ""
        lines.append(f"[{num[d]}] {x['title']}{meta} - {x['url']}")
    return "\n".join(lines) + "\n"
