# run 4: uji kejelasan suara tiruan (transkrip otomatis)
set -x
cd kerja
pip install -q faster-whisper
python - <<'PY'
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in ["cek.mp3"]:
    segs, _ = m.transcribe(f, language="id")
    with open("cek_transkrip.txt", "w") as o:
        for s in segs:
            o.write(f"{s.start:6.2f}-{s.end:6.2f} {s.text.strip()}\n")
PY
