"""Offline voiceover for the cinematic news Shorts.

Voice: Piper "en-us-libritts-high" (LibriTTS, CC BY 4.0), run with onnxruntime. No espeak needed:
words are turned into IPA with CMUdict (data/cmudict.dict) + a small extra dictionary (EXTRA below).
The model files live in assets/voice/ (downloaded once from github.com/rhasspy/piper releases v0.0.2,
see get_voice()).  Unknown words raise an error so a script never gets mumbled: add them to EXTRA
(ARPAbet, like CMUdict) or rephrase.

    from tts import say
    wav, sr, words = say("Here's the news you missed.")   # float32 mono, 22050 Hz, [(word, t0, t1), ...]
"""
import glob, json, os, re, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
VDIR = os.path.join(HERE, "assets", "voice")
URL = "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz"
SPEAKER = int(os.environ.get("NOGGIN_SPEAKER", "49"))       # LibriTTS speaker 49: deep, clean recording (picked by pitch + noise scan)
LENGTH = 1.0                                                # 1 = natural pace (news6 Shorts must stay under 60 s)

V = {"AA": "ɑː", "AE": "æ", "AH": "ʌ", "AO": "ɔː", "AW": "aʊ", "AY": "aɪ", "EH": "ɛ", "ER": "ɜː", "EY": "eɪ", "IH": "ɪ",
     "IY": "iː", "OW": "oʊ", "OY": "ɔɪ", "UH": "ʊ", "UW": "uː"}
C = {"B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "F": "f", "G": "ɡ", "HH": "h", "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n",
     "NG": "ŋ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ", "T": "t", "TH": "θ", "V": "v", "W": "w", "Y": "j", "Z": "z", "ZH": "ʒ"}
EXTRA = {   # words CMUdict lacks or says oddly (ARPAbet)
    "noggin": "N AA1 G IH0 N", "antonelli": "AE2 N T AH0 N EH1 L IY0", "xreal": "EH1 K S R IY0 L", "teghaza": "T EH0 G AA1 Z AH0",
    "gstaad": "G SH T AA1 D", "zurich": "Z UH1 R IH0 K", "eth": "IY1 T IY1 EY1 CH", "snkrs": "S N IY1 K ER0 Z", "kobe": "K OW1 B IY0",
    "powerball": "P AW1 ER0 B AO2 L", "headcorn": "HH EH1 D K AO2 R N", "stearman": "S T IH1 R M AH0 N", "colby": "K OW1 L B IY0",
    "gemini": "JH EH1 M IH0 N AY2", "webb": "W EH1 B", "hubble": "HH AH1 B AH0 L", "vega": "V EY1 G AH0", "addams": "AE1 D AH0 M Z",
    "aerodrome": "EH1 R AH0 D R OW2 M", "selfie": "S EH1 L F IY0", "selfies": "S EH1 L F IY0 Z", "tiktok": "T IH1 K T AA2 K",
}

_cmu = None
def cmu():
    global _cmu
    if _cmu is None:
        _cmu = {}
        for line in open(os.path.join(HERE, "data", "cmudict.dict"), encoding="utf-8"):
            p = line.split("#")[0].split()
            if p and "(" not in p[0]: _cmu.setdefault(p[0].lower(), " ".join(p[1:]))
        _cmu.update(EXTRA)
    return _cmu

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()
def num(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n//10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n//100] + " hundred" + ("" if n % 100 == 0 else " and " + num(n % 100))
    for v, w in ((10**9, "billion"), (10**6, "million"), (1000, "thousand")):
        if n >= v: return num(n//v) + " " + w + ("" if n % v == 0 else (" and " if n % v < 100 else " ") + num(n % v))
def year(n):
    n = int(n)
    if 2000 <= n < 2010: return "two thousand" + ("" if n == 2000 else " " + num(n - 2000))
    return num(n//100) + " " + ("hundred" if n % 100 == 0 else ("oh " + num(n % 100) if n % 100 < 10 else num(n % 100)))

def normalize(t):
    """Spell out numbers, money and units the way a newsreader says them."""
    t = t.replace("’", "'").replace("—", ", ").replace("–", " to ").replace("&", " and ")
    t = re.sub(r"\$(\d[\d,]*(?:\.\d+)?)\s*(million|billion|thousand)", lambda m: m.group(1) + " " + m.group(2) + " dollars", t)
    t = re.sub(r"\$(\d[\d,]*)", lambda m: m.group(1) + " dollars", t)
    t = re.sub(r"(\d+)\s*%", r"\1 percent", t)
    t = re.sub(r"(\d+)\s*mph\b", r"\1 miles per hour", t); t = re.sub(r"(\d+)\s*ft\b", r"\1 feet", t)
    t = re.sub(r"(\d+)\s*km\b", r"\1 kilometres", t); t = re.sub(r"(\d+)\s*kg\b", r"\1 kilos", t)
    t = re.sub(r"\b(1[5-9]\d0|20[0-9]0)s\b", lambda m: year(m.group(1)).replace("ty", "ties") if m.group(1).endswith("0") else m.group(0), t)
    t = re.sub(r"\b(1[89]\d\d|20\d\d)\b", lambda m: year(m.group(1)), t)
    t = re.sub(r"(\d+)\.(\d+)", lambda m: num(m.group(1)) + " point " + " ".join(ONES[int(c)] for c in m.group(2)), t)
    t = re.sub(r"\d[\d,]*", lambda m: num(m.group(0).replace(",", "")), t)
    return t

def words_to_ipa(text):
    """-> list of (display word or None, ipa string). Punctuation becomes its own token (pause)."""
    out = []; d = cmu()
    for tok in re.findall(r"[A-Za-z][A-Za-z'\-]*|[.,!?;:]", normalize(text)):
        if tok in ".,!?;:": out.append((None, tok)); continue
        parts = [p for p in tok.lower().replace("-", " ").split() if p]
        ipa = []
        for p in parts:
            key = p if p in d else p.strip("'")
            if key.endswith("'s") and key not in d and key[:-2] in d: arp = d[key[:-2]] + " Z"
            elif key in d: arp = d[key]
            else: raise KeyError(f"tts: no pronunciation for '{p}' (add it to tts.EXTRA or rephrase)")
            s = ""; phs = arp.split()
            for i, ph in enumerate(phs):
                base, st = re.match(r"([A-Z]+)(\d?)", ph).groups()
                if base in V:
                    ip = V[base]
                    if base == "AH" and st == "0": ip = "ə"
                    elif base == "ER" and st == "0": ip = "ɚ"
                    elif base == "IY" and st == "0": ip = "i"
                    elif base == "IH" and st == "0": ip = "ɪ"
                    nxt = phs[i + 1] if i + 1 < len(phs) else ""
                    if nxt == "R" and base == "AO": ip = "oː"
                    elif nxt == "R" and base == "IY": ip = "ɪ"
                    if p == "a" and len(phs) == 1: ip = "ɐ"
                    s += {"1": "ˈ", "2": "ˌ"}.get(st, "") + ip
                elif base == "T" and 0 < i < len(phs) - 1 and phs[i - 1][:2] in V and phs[i + 1][-1:] == "0" and phs[i + 1][:2] in V:
                    s += "ɾ"                                   # American flap: "better", "water"
                else: s += C[base]
            ipa.append(s)
        out.append((tok, " ".join(ipa)))
    return out

_sess = None
def get_voice():
    onnx = glob.glob(os.path.join(VDIR, "*.onnx"))
    if not onnx:
        os.makedirs(VDIR, exist_ok=True); tgz = os.path.join(VDIR, "v.tgz")
        subprocess.run(["curl", "-sL", "-m", "600", "-o", tgz, URL], check=True)
        subprocess.run(["tar", "xzf", tgz, "-C", VDIR], check=True); os.remove(tgz)
        onnx = glob.glob(os.path.join(VDIR, "*.onnx"))
    return onnx[0], json.load(open(onnx[0] + ".json"))

def session():
    global _sess
    if _sess is None:
        import onnxruntime as ort
        path, cfg = get_voice(); o = ort.SessionOptions(); o.intra_op_num_threads = os.cpu_count() or 4
        _sess = (ort.InferenceSession(path, o, providers=["CPUExecutionProvider"]), cfg)
    return _sess

def say(text, speaker=None, length=None, seed=0):
    """Synthesize one sentence. Returns (audio float32, sample_rate, word_times) where word_times are
    estimated from phoneme counts (good enough to time captions phrase by phrase)."""
    sess, cfg = session(); m = cfg["phoneme_id_map"]; pad, bos, eos = m["_"][0], m["^"][0], m["$"][0]
    toks = words_to_ipa(text); ids = [bos, pad]; spans = []
    for k, (w, ipa) in enumerate(toks):
        if k and w is not None: ids += [m[" "][0], pad]
        a = len(ids)
        for ch in ipa:
            if ch in m: ids += [m[ch][0], pad]
        if w is not None: spans.append((w, a, len(ids)))
    ids.append(eos)
    np.random.seed(seed)
    inp = {"input": np.array([ids], dtype=np.int64), "input_lengths": np.array([len(ids)], dtype=np.int64),
           "scales": np.array([0.5, length or LENGTH, 0.7], dtype=np.float32)}
    if cfg.get("num_speakers", 1) > 1: inp["sid"] = np.array([SPEAKER if speaker is None else speaker], dtype=np.int64)
    audio = sess.run(None, inp)[0].squeeze().astype(np.float32)
    sr = cfg["audio"]["sample_rate"]
    # trim leading/trailing silence
    env = np.abs(audio) > 0.01*np.abs(audio).max(); nz = np.nonzero(env)[0]
    if len(nz): audio = audio[max(0, nz[0] - int(0.03*sr)): nz[-1] + int(0.08*sr)]
    dur = len(audio)/sr; n = len(ids); wt = [(w, dur*a/n, dur*b/n) for w, a, b in spans]
    return audio/max(1e-6, np.abs(audio).max())*0.9, sr, wt


# ================================================================ British voice (Kokoro-82M, Apache 2.0)
# Model + voices: github.com/thewh1teagle/kokoro-onnx releases "model-files-v1.0" (kokoro-v1.0.int8.onnx, voices-v1.0.bin),
# kept in assets/voice/kokoro/ (not in git; get_kokoro() downloads them). Vocab below = kokoro-onnx config.json.
# British voices: bf_alice, bf_emma, bf_isabella, bf_lily (female), bm_daniel, bm_fable, bm_george, bm_lewis (male).
KDIR = os.path.join(VDIR, "kokoro")
KURL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
KVOICE = os.environ.get("NOGGIN_VOICE", "bf_emma")
KSPEED = 0.9                                                  # a touch slower: smooth, unhurried read
KVOCAB = {c: i for c, i in zip(';:,.!?—…"()“” ', [1, 2, 3, 4, 5, 6, 9, 10, 11, 12, 13, 14, 15, 16])}
KVOCAB.update({"̃": 17, "ʣ": 18, "ʥ": 19, "ʦ": 20, "ʨ": 21, "ᵝ": 22, "ꭧ": 23, "A": 24, "I": 25, "O": 31, "Q": 33, "S": 35,
    "T": 36, "W": 39, "Y": 41, "ᵊ": 42, "a": 43, "b": 44, "c": 45, "d": 46, "e": 47, "f": 48, "h": 50, "i": 51, "j": 52, "k": 53,
    "l": 54, "m": 55, "n": 56, "o": 57, "p": 58, "q": 59, "r": 60, "s": 61, "t": 62, "u": 63, "v": 64, "w": 65, "x": 66, "y": 67,
    "z": 68, "ɑ": 69, "ɐ": 70, "ɒ": 71, "æ": 72, "β": 75, "ɔ": 76, "ɕ": 77, "ç": 78, "ɖ": 80, "ð": 81, "ʤ": 82, "ə": 83, "ɚ": 85,
    "ɛ": 86, "ɜ": 87, "ɟ": 90, "ɡ": 92, "ɥ": 99, "ɨ": 101, "ɪ": 102, "ʝ": 103, "ɯ": 110, "ɰ": 111, "ŋ": 112, "ɳ": 113, "ɲ": 114,
    "ɴ": 115, "ø": 116, "ɸ": 118, "θ": 119, "œ": 120, "ɹ": 123, "ɾ": 125, "ɻ": 126, "ʁ": 128, "ɽ": 129, "ʂ": 130, "ʃ": 131, "ʈ": 132,
    "ʧ": 133, "ʊ": 135, "ʋ": 136, "ʌ": 138, "ɣ": 139, "ɤ": 140, "χ": 142, "ʎ": 143, "ʒ": 147, "ʔ": 148, "ˈ": 156, "ˌ": 157, "ː": 158,
    "ʰ": 162, "ʲ": 164, "↓": 169, "→": 171, "↗": 172, "↘": 173, "ᵻ": 177})
# Southern British (RP-ish) vowels, misaki style: A=eɪ I=aɪ W=aʊ Y=ɔɪ Q=əʊ
GBV = {"AA": "ɒ", "AE": "æ", "AH": "ʌ", "AO": "ɔː", "AW": "W", "AY": "I", "EH": "ɛ", "ER": "ɜː", "EY": "A", "IH": "ɪ",
       "IY": "iː", "OW": "Q", "OY": "Y", "UH": "ʊ", "UW": "uː"}
GBC = dict(C, CH="ʧ", JH="ʤ")
BATH = set("after last class glass past fast ask asked can't half dance plant chance answer path bath laugh grass castle example "
           "rather master father calm palm drama banana pasta last-minute vast pass passed".split())

YOD = set("new news newest newer newly tuesday tune tunes due duty during student students tube produce produced introduce "
          "introduced reduce reduced numerous avenue nuclear assume".split())

def gb_ipa(text):
    """British pronunciation (non-rhotic, BATH vowel, əʊ) for the Kokoro voices. Same tokens as words_to_ipa."""
    out = []; d = cmu()
    for tok in re.findall(r"[A-Za-z][A-Za-z'\-]*|[.,!?;:]", normalize(text)):
        if tok in ".,!?;:": out.append((None, tok)); continue
        ipa = []
        for p in [p for p in tok.lower().replace("-", " ").split() if p]:
            key = p if p in d else p.strip("'")
            if key.endswith("'s") and key not in d and key[:-2] in d: arp = d[key[:-2]] + " Z"
            elif key in d: arp = d[key]
            else: raise KeyError(f"tts: no pronunciation for '{p}' (add it to tts.EXTRA or rephrase)")
            phs = arp.split(); s = ""
            for i, ph in enumerate(phs):
                base, st = re.match(r"([A-Z]+)(\d?)", ph).groups(); nxt = phs[i + 1] if i + 1 < len(phs) else ""
                nxtv = nxt[:2] in GBV
                if base in GBV:
                    ip = GBV[base]
                    if base == "AH" and st == "0": ip = "ə"
                    elif base == "ER" and st == "0": ip = "ə"
                    elif base == "IY" and st == "0": ip = "i"
                    elif base == "AA" and (nxt == "R" or key in BATH): ip = "ɑː"
                    elif base == "AE" and key in BATH: ip = "ɑː"
                    elif base == "EH" and nxt == "R" and not (i + 2 < len(phs) and phs[i + 2][:2] in GBV): ip = "ɛː"
                    elif base in ("IH", "IY") and nxt == "R" and not (i + 2 < len(phs) and phs[i + 2][:2] in GBV): ip = "ɪə"
                    elif base == "UH" and nxt == "R": ip = "ʊə"
                    if p == "a" and len(phs) == 1: ip = "ɐ"
                    if base == "UW" and key in YOD and i and phs[i - 1] in ("N", "T", "D", "S"): ip = "j" + ip
                    s += {"1": "ˈ", "2": "ˌ"}.get(st, "") + ip
                elif base == "R":
                    if nxtv: s += "ɹ"                          # non-rhotic: r only before a vowel
                else: s += GBC[base]
            ipa.append(s)
        out.append((tok, " ".join(ipa)))
    return out

_ks = None
def get_kokoro():
    global _ks
    if _ks is None:
        import onnxruntime as ort
        os.makedirs(KDIR, exist_ok=True)
        for f in ("kokoro-v1.0.int8.onnx", "voices-v1.0.bin"):
            if not os.path.exists(os.path.join(KDIR, f)): subprocess.run(["curl", "-sL", "-m", "900", "-o", os.path.join(KDIR, f), KURL + f], check=True)
        o = ort.SessionOptions(); o.intra_op_num_threads = os.cpu_count() or 4
        _ks = (ort.InferenceSession(os.path.join(KDIR, "kokoro-v1.0.int8.onnx"), o, providers=["CPUExecutionProvider"]),
               np.load(os.path.join(KDIR, "voices-v1.0.bin")))
    return _ks

def say_gb(text, voice=None, speed=None):
    """British female voice (default bf_emma). Returns (audio float32, 24000, word_times)."""
    sess, voices = get_kokoro(); toks = gb_ipa(text); ph = ""; spans = []
    for k, (w, ipa) in enumerate(toks):
        if k and w is not None: ph += " "
        a = len(ph); ph += ipa
        if w is not None: spans.append((w, a, len(ph)))
    ids = [KVOCAB[c] for c in ph if c in KVOCAB][:510]
    style = voices[voice or KVOICE][len(ids)]
    audio = sess.run(None, {"tokens": np.array([[0] + ids + [0]], dtype=np.int64), "style": style.astype(np.float32),
                            "speed": np.array([speed or KSPEED], dtype=np.float32)})[0].squeeze().astype(np.float32)
    sr = 24000; env = np.abs(audio) > 0.01*np.abs(audio).max(); nz = np.nonzero(env)[0]
    if len(nz): audio = audio[max(0, nz[0] - int(0.03*sr)): nz[-1] + int(0.1*sr)]
    dur = len(audio)/sr; n = max(1, len(ph)); wt = [(w, dur*a/n, dur*b/n) for w, a, b in spans]
    return audio/max(1e-6, np.abs(audio).max())*0.9, sr, wt
