import re, unicodedata

from pyvi import ViTokenizer

STOP = set("""và của là có các những một được cho trong với này đó khi để từ đã sẽ
cũng như không còn nhưng hay hoặc thì mà tại theo về ra vào bị rất lại nên đến
the a an of to in and is are for on with""".split())
# Viết tắt: chỉ khớp khi đứng độc lập (không nằm cuối từ khác như GDP., IQ.)
ABBR_RE = re.compile(r"(?<!\w)(TS|ThS|PGS|GS|TP|Q|P|Mr|Dr|vs)\.|(?<!\w)v\.v\.")
DANGLING = ("nó ", "họ ", "chúng ", "điều này", "việc này", "đó là", "tuy nhiên",
            "vì vậy", "do đó", "ngoài ra", "bên cạnh đó")

_TONE = "\u0300\u0301\u0303\u0309\u0323"
_CONS = "bcdđghklmnpqrstvxBCDĐGHKLMNPQRSTVX"
_OLD1 = re.compile(rf"(?<=[{_CONS}])([oO])([{_TONE}])([aAeE])")   # hòa -> hoà, khỏe -> khoẻ
_OLD2 = re.compile(rf"(?<=[{_CONS}])([uU])([{_TONE}])([yY])")     # thủy -> thuỷ

def unify_tone(text: str) -> str:
    d = unicodedata.normalize("NFD", text)
    d = _OLD1.sub(r"\1\3\2", d)
    d = _OLD2.sub(r"\1\3\2", d)
    return unicodedata.normalize("NFC", d)

def normalize(text: str) -> str:
    import html
    text = html.unescape(text)                                # &amp; -> &
    text = unicodedata.normalize("NFC", text)
    text = unify_tone(text)                                   # thống nhất vị trí dấu thanh
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"https?://\S+|\S+@\S+\.\S+", "", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n", text).strip()

def split_sentences(text: str) -> list[str]:
    out = []
    for para in text.split("\n"):
        para = ABBR_RE.sub(lambda m: m.group(0).replace(".", "§"), para)
        first = True                                          # không nối câu qua ranh giới đoạn
        for p in re.split(r"(?<=[.!?…])\s+", para):
            p = p.replace("§", ".").strip()
            if not p:
                continue
            if (not first) and out and not (p[0].isupper() or p[0].isdigit() or p[0] in "\"“(["):
                out[-1] += " " + p
            else:
                out.append(p)
            first = False
    return out

def is_standalone(sentence: str) -> bool:
    return not sentence.lower().startswith(DANGLING)

def _keep(t: str) -> bool:
    return t not in STOP and (len(t) > 1 or t.isdigit() or not t.isascii())  # giữ "ô", bỏ "a"

def tokenize(text: str, bigrams: bool = False) -> list[str]:
    text = text.lower()
    if ViTokenizer is not None:       # tách từ: "chuyển đổi số" -> "chuyển_đổi_số"
        text = ViTokenizer.tokenize(text)
        bigrams = False               # đã có từ ghép, không cần bigram
    raw = re.findall(r"\w+", text)   # \w giữ được dấu "_"
    toks = [t for t in raw if _keep(t)]
    if bigrams:                       # chỉ dùng khi chưa cài pyvi
        toks += [a + "_" + b for a, b in zip(raw, raw[1:]) if _keep(a) and _keep(b)]
    return toks