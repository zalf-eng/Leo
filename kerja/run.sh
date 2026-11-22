# run 1: bedah video ayam + uji suara + cari footage
set -x
mkdir -p kerja/out
cd kerja/out
curl -sSfL -o ayam_asli.mp4 "https://assets.vidiq.com/compositions/e1f917e8-8267-45ec-9489-b364712904cc/pbgsq1gdxd3ad2ysk4p9zgar.mp4"
curl -sSfL -o ayam_vo.mp3 "https://assets.vidiq.com/voiceovers/e1f917e8-8267-45ec-9489-b364712904cc/9f2347bd-ae61-48bc-b3c3-619a68abba24.mp3"
pip install -q edge-tts faster-whisper
edge-tts --list-voices | grep -i id-ID > voices.txt
edge-tts --voice id-ID-ArdiNeural --rate=+10% --text "Telur cokelat lebih bergizi dari telur putih? Ternyata jawabannya bikin kaget." --write-media tes_ardi.mp3
edge-tts --voice id-ID-GadisNeural --rate=+10% --text "Telur cokelat lebih bergizi dari telur putih? Ternyata jawabannya bikin kaget." --write-media tes_gadis.mp3
python - <<'PY'
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe("ayam_vo.mp3", language="id")
with open("transkrip.txt", "w") as f:
    for s in segs:
        f.write(f"{s.start:6.2f}-{s.end:6.2f} {s.text.strip()}\n")
PY
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
for q in chicken hen egg eggs rooster farm; do curl -sL -A "$UA" "https://mixkit.co/free-stock-video/$q/" -o mixkit_$q.html; done
curl -sL -A "$UA" -o pexels_search.html -w "%{http_code}\n" "https://www.pexels.com/search/videos/chicken/" > pexels_code.txt
curl -s "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=chicken%20filetype:video&srnamespace=6&format=json&srlimit=50" -o commons_chicken.json
curl -s "https://commons.wikimedia.org/w/api.php?action=query&list=search&srsearch=egg%20filetype:video&srnamespace=6&format=json&srlimit=50" -o commons_egg.json
ls -la
