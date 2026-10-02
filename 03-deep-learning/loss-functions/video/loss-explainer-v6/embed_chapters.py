"""Add native MP4 chapter markers without re-encoding this newly rendered video."""
import argparse,json,os,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');a=p.parse_args();D=json.loads((B/'timeline.json').read_text())
meta=[';FFMETADATA1','title=换把评分尺，模型就换答案']
for i,s in enumerate(D['scenes']):
    meta.extend(['[CHAPTER]','TIMEBASE=1/1000',f'START={round(s["start"]*1000)}',f'END={round(s["end"]*1000)}',f'title={i+1:02} · {s["title"]}'])
f=B/'chapters.ffmetadata';f.write_text('\n'.join(meta)+'\n')
video=B/'renders/loss-functions-v6.mp4';temp=video.with_name('loss-functions-v6-chapters.mp4')
subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(video),'-i',str(f),'-map','0','-map_metadata','1','-map_chapters','1','-c','copy','-movflags','+faststart',str(temp)],check=True)
os.replace(temp,video);print(f'Embedded {len(D["scenes"])} MP4 chapter markers')
