"""Render the revised visual track, then mux the accepted AAC without processing it."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

B=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--ffmpeg',default=os.getenv('VIDEO_FFMPEG','ffmpeg'))
p.add_argument('--node',default=os.getenv('VIDEO_NODE','node'))
p.add_argument('--hyperframes-cli',default=os.getenv('VIDEO_HYPERFRAMES_CLI'))
p.add_argument('--workers',type=int,default=4)
p.add_argument('--mux-only',action='store_true')
p.add_argument('--output',type=Path,default=B/'renders/backpropagation-v2.mp4')
a=p.parse_args()
D=json.loads((B/'timeline.json').read_text())
audio=B/'audio/narration.m4a'
if not audio.exists():
    raise FileNotFoundError('Missing retained audio/narration.m4a; restore its accepted AAC stream from the published final MP4. See production-notes.md.')
assert hashlib.sha256(audio.read_bytes()).hexdigest()==json.loads((B/'audio-provenance.json').read_text())['reused_aac_file_sha256']
if not a.mux_only:
    cli=[a.node,a.hyperframes_cli] if a.hyperframes_cli else ['npx','--yes','hyperframes@0.8.78']
    subprocess.run(cli+['render','--output','renders/backpropagation-v2-visual.mp4','--quality','high','--fps','30','--workers',str(a.workers),'--gpu','--skill','knowledge-video-production'],cwd=B,check=True)
meta=[';FFMETADATA1','title=反向传播与自动微分 · 过程优化版']
for i,s in enumerate(D['scenes']):
    meta += ['[CHAPTER]','TIMEBASE=1/1000',f'START={round(s["start"]*1000)}',f'END={round(s["end"]*1000)}',f'title={i+1:02} · {s["title"]}']
(B/'chapters.ffmetadata').write_text('\n'.join(meta)+'\n')
output=(B/a.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(B/'renders/backpropagation-v2-visual.mp4'),'-i',str(audio),'-i',str(B/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(output)],check=True)
print(json.dumps(dict(final=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),audio_reencoded=False)))
