# run 3: cek resolusi lebih tinggi Mixkit + cari video vertikal
set -x
mkdir -p kerja/ayam3 && cd kerja/ayam3
for id in 46582 17202 11225 47314 46052 14384 45543 49043 49044 43011 47106 45326 47368 45102 47107; do
  for r in 2160 1080; do
    c=$(curl -s -o /dev/null -w "%{http_code}" -I "https://assets.mixkit.co/videos/$id/$id-$r.mp4"); echo "$id $r $c" >> probe.txt
    if [ "$c" = "200" ]; then curl -sSfL -o clip_${id}_$r.mp4 "https://assets.mixkit.co/videos/$id/$id-$r.mp4"; break; fi
  done
done
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
for q in chicken egg hen rooster; do curl -sL -A "$UA" "https://mixkit.co/free-stock-video/vertical/?q=$q" -o vert_$q.html; curl -sL -A "$UA" "https://mixkit.co/free-stock-video/discover/$q/?orientation=vertical" -o vert2_$q.html; done
ls -la
