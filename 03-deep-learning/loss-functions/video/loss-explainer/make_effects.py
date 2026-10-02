"""Original quiet sine accents: mark causal changes without masking speech."""
import argparse,array,json,math,subprocess,wave
from pathlib import Path
B=Path(__file__).resolve().parent
P=argparse.ArgumentParser();P.add_argument('--ffmpeg',default='ffmpeg');a=P.parse_args()
D=json.loads((B/'timeline.json').read_text());sr=24000
samples=array.array('h',[0])*math.ceil(D['duration']*sr)
events=[]
for s in D['scenes']:
    t=s['start']+.2
    events.append((t,450 if s['id'] in ['history','timeline','frontier'] else 620))
    if s['id'] in ['mse','outlier','smoothing','contrast']:
        events.append((s['start']+(s['end']-s['start'])*.55,760))
for t,freq in events:
    start=round(t*sr);n=round(.16*sr)
    for i in range(n):
        v=(math.sin(2*math.pi*freq*i/sr)+.25*math.sin(2*math.pi*freq*.5*i/sr))*math.sin(math.pi*i/n)**2*.026
        if start+i<len(samples):samples[start+i]=max(-32767,min(32767,samples[start+i]+round(v*32767)))
wav=B/'audio/effects.wav'
with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(samples.tobytes())
subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error','-i',str(wav),'-c:a','aac','-b:a','96k','-y',str(B/'audio/effects.m4a')],check=True)
print(f'{len(events)} original subtle accents')
