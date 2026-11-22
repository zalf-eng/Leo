# run 2: suara narasi (edge-tts, per kalimat) + footage Mixkit
set -x
mkdir -p kerja/ayam2
cd kerja/ayam2
pip install -q edge-tts
i=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  i=$((i+1)); n=$(printf "%02d" $i)
  for v in id-ID-ArdiNeural; do
    for try in 1 2 3 4; do
      edge-tts --voice $v --rate=+8% --text "$line" --write-media vo_$n.mp3 && [ -s vo_$n.mp3 ] && break
      sleep 5
    done
  done
done <<'TXT'
Telur cokelat lebih bergizi dari telur putih? Jawabannya ternyata bisa kamu tebak dari telinga ayamnya.
Warna kulit telur ditentukan oleh jenis ayam yang bertelur.
Pada dasarnya, semua cangkang telur berwarna putih, karena terbuat dari kalsium karbonat, alias kapur.
Pada ayam petelur cokelat, beberapa jam sebelum telur keluar, cangkangnya dilapisi pigmen cokelat bernama protoporfirin.
Lalu, apa hubungannya dengan telinga? Ayam yang cuping telinganya putih, biasanya bertelur putih.
Sedangkan ayam yang cuping telinganya merah, biasanya bertelur cokelat. Tapi ingat, ini cuma petunjuk, bukan aturan pasti.
Terus, mana yang lebih bergizi? Jawabannya, hampir sama persis.
Yang menentukan gizi telur adalah pakan dan umur ayamnya, bukan warna cangkangnya.
Lalu, kenapa di Indonesia telur cokelat paling banyak? Karena peternak kita kebanyakan memelihara ayam ras petelur cokelat.
Sekarang kamu sudah tahu, kan? Tulis di komentar, fakta ayam apa lagi yang mau kamu ketahui!
TXT
for id in 3795 17202 43011 46582 45326 47368 47314 46052 46054 49044 49043 45543 47106 47107 45542 45102 42906 101157 14384 11225 47108; do
  curl -sSfL -o clip_$id.mp4 "https://assets.mixkit.co/videos/$id/$id-1080.mp4" || curl -sSfL -o clip_$id.mp4 "https://assets.mixkit.co/videos/$id/$id-720.mp4" || true
done
ls -la
