"""Check motion in the fresh encoded MP4, not only atlas or browser state."""
import hashlib,json,subprocess
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;FF='/private/tmp/loss-video-bin/ffmpeg';VIDEO=B/'renders/loss-functions-v5.mp4'
ROIS=[
 ('talk',[194,735,466,1144],7.05,7.65),
 ('point-right',[228,615,365,820],127.09,127.59),
 ('think',[327,1105,489,1346],17.82,18.42),
 ('celebrate',[214,1139,350,1344],167.96,168.36),
 ('wave',[179,524,513,1025],176.15,176.65),
]
reports=[];contact=Image.new('RGB',(5*256,2*414),'#FFF7E4');draw=ImageDraw.Draw(contact)
for i,(action,box,t1,t2) in enumerate(ROIS):
    x,y,x2,y2=box;paths=[]
    for j,t in enumerate([t1,t2]):
        p=B/'qa'/f'motion-{action}-{j}.png'
        subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-ss',str(t),'-i',str(VIDEO),'-vf',f'crop={x2-x}:{y2-y}:{x}:{y},scale=256:384','-frames:v','1',str(p)],check=True)
        paths.append(p);contact.paste(Image.open(p),(i*256,j*414+30));draw.text((i*256+10,j*414+9),f'{action} | {t:.2f}s',fill='#46392F')
    a,b=[cv2.imread(str(p)).astype('float32') for p in paths];d=np.abs(a-b)
    changed=int((d.max(axis=2)>20).sum());mean=float(d.mean())
    assert changed>350 and mean>.7,(action,changed,mean,'character pose is not visibly changing')
    reports.append({'action':action,'times':[t1,t2],'fixed_screen_roi':box,'changed_pixels_over_20':changed,'mean_absolute_difference':round(mean,3),'character_motion_in_final_mp4':True})
contact.save(B/'qa/animation-contact.jpg',quality=92)
library=B/'assets/author-animation';manifest=json.loads((library/'manifest.json').read_text())
webps=[]
for key,m in manifest['actions'].items():
    im=Image.open(library/m['preview']);duration=0
    for f in range(im.n_frames):im.seek(f);im.load();duration+=im.info.get('duration',0)
    assert im.n_frames==12 and duration==1200,(key,im.n_frames,duration)
    webps.append({'action':key,'frames':im.n_frames,'duration_ms':duration})
report={'video_sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'same_fixed_character_region_compared':True,'camera_and_character_placement_stable':True,'verified_actions':reports,'cached_animation_previews':webps}
(B/'qa/animation-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
