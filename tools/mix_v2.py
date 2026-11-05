import subprocess
L = 21.2
cuts = [2.29, 3.48, 7.0, 9.0, 11.14, 14.38, 15.38, 17.66]
flips = [14.38 + k * 1.0 / 6 for k in range(1, 6)]
ins = ['-i', 'vo_tight.wav', '-ss', '14.35', '-t', str(L), '-i', 'dl/music_dj.wav']
ins_vo = None
f = []; w = []; n = 2
for t in cuts + flips:
    big = t in cuts; d = 0.32 if big else 0.08
    ins += ['-f', 'lavfi', '-t', str(d), '-i', f'anoisesrc=c=pink:a={0.5 if big else 0.35}:d={d}']
    st = int(((t - 0.12) if big else t) * 1000)
    f.append(f"[{n}:a]highpass=f={700 if big else 2500},lowpass=f=7000,afade=t=in:d={d*0.35},afade=t=out:st={d*0.35}:d={d*0.65},"
             f"volume={0.35 if big else 0.25},adelay={st}|{st},aformat=channel_layouts=stereo:sample_rates=48000[x{n}]")
    w.append(f'[x{n}]'); n += 1
f.append("[0:a]aformat=channel_layouts=stereo:sample_rates=48000,highpass=f=90,acompressor=threshold=-18dB:ratio=3:attack=5:release=80,volume=1.3[vo]")
f.append(f"[1:a]aformat=channel_layouts=stereo:sample_rates=48000,volume='if(lt(t,20.25),0.2,0.2+min(1,(t-20.25)/0.25)*0.55)':eval=frame,"
         f"afade=t=in:d=0.15,afade=t=out:st={L-0.6}:d=0.6[mu]")
f.append("[vo][mu]" + ''.join(w) + f"amix=inputs={2+len(w)}:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(f), '-map', '[a]', '-ar', '48000', '-t', str(L), 'mix.wav'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'v2_silent.mp4', '-i', 'mix.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'Promo_Jeans_Baggy_v2.mp4'], check=True)
# TikTok version: voiceover + SFX only (trending song is attached in the app / via Repliz)
f2 = f[:-2] + ["[vo]" + ''.join(w) + f"amix=inputs={1+len(w)}:normalize=0:duration=longest,apad=whole_dur={L},loudnorm=I=-14:TP=-1.5:LRA=11[a]"]
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins + ['-filter_complex', ';'.join(f2), '-map', '[a]', '-ar', '48000', '-t', str(L), 'mix_vo.wav'], check=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'v2_silent.mp4', '-i', 'mix_vo.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', 'Promo_Jeans_Baggy_v2_tanpa_musik.mp4'], check=True)
