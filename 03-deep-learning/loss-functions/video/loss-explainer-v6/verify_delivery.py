"""Verify the new final MP4 and extract one real frame from every section."""
import hashlib,json,os,re,shutil,subprocess
from pathlib import Path
import cv2
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;F=os.environ.get('VIDEO_FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
probe=os.environ.get('VIDEO_FFPROBE') or shutil.which('ffprobe') or 'ffprobe'
(B/'qa').mkdir(exist_ok=True)
D=json.loads((B/'timeline.json').read_text());S=json.loads((B/'storyboard.json').read_text())
video=B/'renders/loss-functions-v6.mp4'
P=json.loads(subprocess.check_output([probe,'-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(video)],text=True))
(B/'qa/ffprobe-final.json').write_text(json.dumps(P,ensure_ascii=False,indent=2))
v=next(s for s in P['streams'] if s['codec_type']=='video');a=next(s for s in P['streams'] if s['codec_type']=='audio')
assert [v['width'],v['height']]==[1080,1920]
assert v['codec_name']=='h264' and a['codec_name']=='aac'
assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==round(D['duration']*30)
assert len(P['chapters'])==len(D['scenes'])==17
assert abs(float(P['format']['duration'])-D['duration'])<.04
decode=subprocess.run([F,'-hide_banner','-loglevel','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
(B/'qa/decode-final.log').write_text(decode.stderr)
assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
source=(B/'index.html').read_text()
assert 'github-project-qr' not in source and '扫码' not in source and 'data-action="qr"' not in source
assert '点亮 Star，一起学习' in source and '我的深度学习之路' in source
frames=[]
for s in D['scenes']:
 p=B/'qa'/f'frame-{s["id"]}.png';t=s['end']-.4
 subprocess.run([F,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=270:-1',str(p)],check=True)
 frames.append((s,p,t))
contact=Image.new('RGB',(1080,5*516),'#FFF7E4');draw=ImageDraw.Draw(contact)
for i,(s,p,t) in enumerate(frames):
 x=(i%4)*270;y=(i//4)*516;contact.paste(Image.open(p),(x,y+28));draw.text((x+10,y+8),f'{s["id"]} | {t:.2f}s',fill='#46392F')
contact.save(B/'qa/contact-final.jpg',quality=92)
for name,t in [('hook-final',6),('first-frame',0)]:
 subprocess.run([F,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1',str(B/'qa'/f'{name}.png')],check=True)
# Decode the tail through EOF and overwrite the same PNG for each output frame.
# The resulting image is the literal last frame, without float-seek rounding.
subprocess.run([F,'-hide_banner','-loglevel','error','-y','-sseof','-0.2','-i',str(video),'-fps_mode','passthrough','-update','1',str(B/'qa/project-final.png')],check=True)
detector=cv2.QRCodeDetector()
control=B/'qa/previous-project-qr.png'
if control.exists():
 assert detector.detectAndDecode(cv2.imread(str(control)))[0]==D['project_url'],'QR detector positive control failed'
# Inspect the whole ending at 10 fps and the literal last frame at full resolution.
ending=D['scenes'][-1]
raw=subprocess.check_output([F,'-hide_banner','-loglevel','error','-ss',str(ending['start']),'-i',str(video),'-vf','fps=10,scale=540:960','-f','rawvideo','-pix_fmt','bgr24','pipe:1'])
import numpy as np
ending_frames=np.frombuffer(raw,np.uint8).reshape((-1,960,540,3))
for i,frame in enumerate(ending_frames):
 assert not detector.detectAndDecodeMulti(frame)[0],('unexpected QR in ending',i)
last=cv2.imread(str(B/'qa/project-final.png'))
assert not detector.detectAndDecodeMulti(last)[0],'unexpected QR in final full-resolution frame'
Image.open(B/'qa/project-final.png').resize((540,960)).save(B/'assets/ending-no-qr.jpg',quality=93)
prov=json.loads((B/'qa/reference-provenance.json').read_text())
assert hashlib.sha256((B/'assets/author-handdraw.png').read_bytes()).hexdigest()==prov['character_sha256']
assert hashlib.sha256((B/'audio/author-reference-original.m4a').read_bytes()).hexdigest()==prov['voice_sha256']
requests=json.loads((B/'audio/generation-requests.json').read_text())
audio_provenance=json.loads((B/'audio-provenance.json').read_text())
for item in audio_provenance['files'].values():
 assert hashlib.sha256((B/item['path']).read_bytes()).hexdigest()==item['sha256'],item['path']
assert len(requests)==4 and all(len(r['references'])==1 and Path(r['references'][0]['audio_path']).name=='author-reference.wav' for r in requests)
assert [x['request_id'] for x in D['audio_audit']]==audio_provenance['original_seed_request_ids']
historical_narration_matches=hashlib.sha256((B/'audio/narration.m4a').read_bytes()).hexdigest()==audio_provenance['files']['narration']['sha256']
rate=json.loads((B/'qa/speech-rate.json').read_text());assert rate['measured_cpm']==320
report={'version':'v6','revision':'no-qr-ending','width':v['width'],'height':v['height'],'fps':v['avg_frame_rate'],'frames':int(v['nb_frames']),'duration':float(P['format']['duration']),'codecs':[v['codec_name'],a['codec_name']],'bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'chapters':len(P['chapters']),'captions':len(D['captions']),'explanation_beats':sum(len(s['beats']) for s in S['scenes']),'full_decode_errors':0,'qr_absent_from_ending':True,'ending_frames_checked':len(ending_frames),'literal_last_frame_checked':True,'qr_detector_positive_control':control.exists(),'author_source_sha256_verified':True,'voice_source_sha256_verified':True,'all_four_requests_use_author_reference':True,'original_v3_seed_jobs_complete':len(D['audio_audit']),'new_audio_generation_calls':0,'narration_reused_from_v3':historical_narration_matches,'measured_han_cpm':rate['measured_cpm'],'content_shares':[c['share'] for c in D['chapters']],'cta_excluded_from_content_shares':True,'contact_frames':len(frames)}
(B/'qa/delivery-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
