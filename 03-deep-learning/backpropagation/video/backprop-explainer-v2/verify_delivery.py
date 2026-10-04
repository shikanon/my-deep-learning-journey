"""Validate the real encoded export, its audio identity and PNG actor fidelity."""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen
import cv2
import numpy as np
from PIL import Image, ImageDraw

B=Path(__file__).resolve().parent;ROOT=B.parents[3]
p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default=os.getenv('VIDEO_FFMPEG','ffmpeg'));p.add_argument('--ffprobe',default=os.getenv('VIDEO_FFPROBE','ffprobe'));args=p.parse_args()
video=B/'renders/backpropagation-v2.mp4';reference=B/'audio/narration.m4a'
accepted=json.loads((B/'audio-provenance.json').read_text())
D=json.loads((B/'timeline.json').read_text());fps=D['fps']
def run(cmd):return subprocess.run(cmd,capture_output=True,text=True,check=True)
probe=json.loads(run([args.ffprobe,'-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(video)]).stdout)
(B/'qa/ffprobe.json').write_text(json.dumps(probe,ensure_ascii=False,indent=2)+'\n')
vs=next(s for s in probe['streams'] if s['codec_type']=='video');aas=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (vs['width'],vs['height'],vs['codec_name'],vs['pix_fmt'])==(1080,1920,'h264','yuv420p')
assert vs['r_frame_rate']=='30/1' and int(vs['nb_frames'])==7206 and aas['codec_name']=='aac'
assert abs(float(probe['format']['duration'])-D['duration'])<.05
assert len(probe['chapters'])==len(D['scenes'])==16
decode=run([args.ffmpeg,'-hide_banner','-v','error','-i',str(video),'-f','null','-'])
(B/'qa/decode-final.log').write_text(decode.stderr)
assert not decode.stderr.strip()
def audio_hash(file,copy):
    command=[args.ffmpeg,'-hide_banner','-v','error','-i',str(file),'-map','0:a:0','-c:a','copy' if copy else 'pcm_s16le','-f','hash','-hash','sha256','-']
    return run(command).stdout.strip().split('=')[-1]
audio=dict(old_packet_hash=accepted['accepted_audio_packet_sha256'],new_packet_hash=audio_hash(video,True),old_pcm_hash=accepted['accepted_audio_pcm_sha256'],new_pcm_hash=audio_hash(video,False),local_reference_packet_hash=audio_hash(reference,True),local_reference_pcm_hash=audio_hash(reference,False))
assert audio['old_packet_hash']==audio['new_packet_hash']
assert audio['old_pcm_hash']==audio['new_pcm_hash']
assert audio['local_reference_packet_hash']==audio['new_packet_hash']
assert audio['local_reference_pcm_hash']==audio['new_pcm_hash']
(B/'qa/audio-identity.json').write_text(json.dumps(audio,indent=2)+'\n')
loud=run([args.ffmpeg,'-hide_banner','-nostats','-i',str(video),'-map','0:a:0','-af','ebur128=peak=true','-f','null','-'])
(B/'qa/loudness.log').write_text(loud.stderr)
LUFS=float(re.findall(r'I:\s+(-?\d+\.\d+)\s+LUFS',loud.stderr)[-1])
cap=cv2.VideoCapture(str(video));assert cap.isOpened()
def frame(time):
    f=max(0,min(7205,round(time*fps)));cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,im=cap.read();assert ok,(time,f)
    return f,cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
contact=Image.new('RGB',(1080,1920),'#FFF9EC')
for i,s in enumerate(D['scenes']):
    f,rgb=frame(s['end']-.15);image=Image.fromarray(rgb);image.save(B/f'qa/encoded-{s["id"]}.png');contact.paste(image.resize((270,480)),(i%4*270,i//4*480))
contact.save(B/'qa/encoded-contact.jpg',quality=95)
for name,time in [('first-frame',0),('last-frame',240.166667),('poster',96)]:
    f,rgb=frame(time);im=Image.fromarray(rgb);im.save(B/f'qa/{name}.png')
    if name=='poster':im.save(B/'assets/poster.jpg',quality=95)
    if name=='last-frame':im.save(B/'assets/ending-no-qr.jpg',quality=95)

# Keep before / middle / after frames from the final MP4 for the changed mechanisms.
mechanisms=[('s02','prediction'),('s02','loss'),('s03','small'),('s03','local'),('s05','residual'),('s06','prediction'),('s06','bias'),('s06','weight'),('s07','parameters'),('s07','loss'),('s08','square'),('s08','identity'),('s08','sum'),('s10','reverse'),('s11','accumulate'),('s11','clear'),('s11','scale'),('s13','checkpoint'),('s13','recompute'),('s14','compiler'),('s15','error')]
sheet=Image.new('RGB',(810,len(mechanisms)*500),'#FFF9EC');draw=ImageDraw.Draw(sheet);samples=[]
for row,(sid,key) in enumerate(mechanisms):
    scene=next(s for s in D['scenes'] if s['id']==sid);step=next(st for st in scene['steps'] if st['id']==key)
    times=[step['start']-.06,step['start']+step['duration']/2,min(scene['end']-.04,step['start']+step['duration']+.04)]
    for col,time in enumerate(times):
        f,rgb=frame(time);name=f'mechanism-{sid}-{key}-{col}.png';im=Image.fromarray(rgb);im.save(B/'qa'/name);sheet.paste(im.resize((270,480)),(col*270,row*500+20));samples.append(dict(scene=sid,step=key,position=['before','middle','after'][col],frame=f,time=f/fps,file='qa/'+name))
    draw.text((8,row*500+4),sid+' / '+key,fill='#403B35')
sheet.save(B/'qa/mechanism-contact.jpg',quality=94)
(B/'qa/encoded-mechanisms.json').write_text(json.dumps(samples,indent=2)+'\n')

# Reconstruct the exact source frames on the fixed transformed actor canvas.
# This checks reuse fidelity; it does not claim rigid facial consistency for hand-drawn poses.
scene=next(s for s in D['scenes'] if s['id']=='s06');st=next(st for st in scene['steps'] if st['id']=='weight')['start'];pack=ROOT/'assets/手绘形象/博士服教棍-v1'
manifest=json.loads((pack/'manifest.json').read_text());fidelity=[]
for i,file in enumerate(manifest['frames']):
    f,rgb=frame(st+(i+.5)/manifest['fps']);time=f/fps;index=math.floor((time-st)*manifest['fps']);assert index==i
    source=Image.open(pack/file).convert('RGBA');resized=source.resize((265,265),Image.Resampling.BILINEAR);expected=Image.new('RGBA',(265,265),'#FFF9EC');expected.alpha_composite(resized);expected=np.asarray(expected.convert('RGB')).astype(float)
    encoded=rgb[1400:1665,60:325].astype(float);mae=float(np.abs(expected-encoded).mean());assert mae<6,(i,mae)
    bbox=source.getbbox();visible=[60+bbox[0]*265/512,1400+bbox[1]*265/512,60+bbox[2]*265/512,1400+bbox[3]*265/512];assert visible[2]<355 and visible[3]<1690
    fidelity.append(dict(frame=f,source=file,index=i,mean_absolute_rgb_error=mae,visible_bounds=visible))
cap.release();(B/'qa/actor-fidelity.json').write_text(json.dumps(dict(purpose='encoded pixels versus original doctor PNG sequence after placement',face_scope='faithful reuse of the original hand-drawn poses, not V3 rigid-head certification',frames=fidelity),ensure_ascii=False,indent=2)+'\n')
url='http://127.0.0.1:8773/03-deep-learning/backpropagation/video/backprop-explainer-v2/renders/backpropagation-v2.mp4'
with urlopen(Request(url,method='HEAD')) as r:head=r.status;assert head==200
with urlopen(Request(url,headers={'Range':'bytes=0-1023'})) as r:status=r.status;assert status==206 and len(r.read())==1024
with urlopen(url) as r:download=r.read()
sha=hashlib.sha256(video.read_bytes()).hexdigest();assert hashlib.sha256(download).hexdigest()==sha
report=dict(status='passed',file='renders/backpropagation-v2.mp4',sha256=sha,bytes=video.stat().st_size,width=1080,height=1920,fps=30,frame_count=7206,duration=float(probe['format']['duration']),video_codec=vs['codec_name'],audio_codec=aas['codec_name'],chapters=16,full_decode_errors=0,audio_identical_to_v1=True,integrated_lufs=LUFS,encoded_scene_samples=16,encoded_mechanism_samples=len(samples),actor_frames_compared=len(fidelity),actor_max_mean_rgb_error=max(x['mean_absolute_rgb_error'] for x in fidelity),http_head=head,http_range=status,download_hash_matches=True)
(B/'qa/delivery-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
