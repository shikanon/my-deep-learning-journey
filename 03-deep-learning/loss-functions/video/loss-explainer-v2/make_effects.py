"""Quiet original pencil strokes and rounded pops, synchronized to explanation beats."""
import argparse,array,json,math,subprocess,wave
from pathlib import Path
B=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');a=p.parse_args()
D=json.loads((B/'storyboard.json').read_text());sr=24000;samples=array.array('h',[0])*math.ceil(D['duration']*sr);count=0
for s in D['scenes']:
    for j,b in enumerate(s['beats']):
        start=round(b['start']*sr);n=round((.20 if b['action'] else .11)*sr);state=18347+j*1291;freq=410+j*47
        for i in range(n):
            state=(1664525*state+1013904223)&0xffffffff;noise=(state/4294967296*2-1)
            envelope=math.sin(math.pi*i/n)**2
            v=(math.sin(2*math.pi*(freq+180*i/n)*i/sr)*.018+noise*.0025)*envelope
            if start+i<len(samples):samples[start+i]=max(-32767,min(32767,samples[start+i]+round(v*32767)))
        count+=1
w=B/'audio/effects.wav'
with wave.open(str(w),'wb') as out:out.setnchannels(1);out.setsampwidth(2);out.setframerate(sr);out.writeframes(samples.tobytes())
subprocess.run([a.ffmpeg,'-loglevel','error','-y','-i',str(w),'-c:a','aac','-b:a','96k',str(B/'audio/effects.m4a')],check=True)
print(count,'original quiet accents')
