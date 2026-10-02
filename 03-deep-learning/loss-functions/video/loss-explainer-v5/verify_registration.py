"""Measure stable anatomical regions in delivered PNGs, including action switches."""
from pathlib import Path
from PIL import Image,ImageDraw
import cv2,numpy as np,json,hashlib
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
OLD=ROOT/'assets/手绘形象/shikanon-animation-v1';NEW=ROOT/'assets/手绘形象/shikanon-animation-v2'
M=json.loads((NEW/'manifest.json').read_text());base=np.array(Image.open(NEW/'frames/talk/000.png'))
ROIS={'hair':[59,91,287,212],'shirt':[151,379,229,415],'feet':[80,477,275,551]}
def crop(a,r):x,y,x2,y2=r;return a[y:y2,x:x2]
def gray(a):
 rgb=a[:,:,:3].astype(np.float32);alpha=a[:,:,3:4]/255
 return np.uint8(np.clip(rgb*alpha+255*(1-alpha),0,255))
rows=[]
for ac,m in M['actions'].items():
 frames=[np.array(Image.open(NEW/f['file'])) for f in m['frames']]
 assert all(tuple(a.shape)==(576,384,4) for a in frames)
 for i,a in enumerate(frames):
  measures={}
  for name,r in ROIS.items():
   ref=crop(base,r);patch=crop(a,r);d=np.abs(ref.astype(int)-patch.astype(int));mae=float(d.mean())
   # Translation search uses image pixels, not the declared anchors.
   x,y,x2,y2=r;region=gray(a[max(0,y-12):min(576,y2+12),max(0,x-12):min(384,x2+12)])
   template=gray(ref);corr=cv2.matchTemplate(region,template,cv2.TM_SQDIFF_NORMED);_,_,at,_=cv2.minMaxLoc(corr)
   drift=[at[0]-min(12,x),at[1]-min(12,y)]
   assert drift==[0,0],(ac,i,name,drift)
   assert mae<.06,(ac,i,name,mae)
   measures[name]={'pixel_mae':round(mae,6),'measured_translation_px':drift}
  assert not (a[:2,:,3]>50).any() and not (a[-2:,:,3]>50).any() and not (a[:,:2,3]>50).any() and not (a[:,-2:,3]>50).any(),(ac,i,'canvas-edge-clipping')
  rows.append({'action':ac,'frame':i,'fixed_regions':measures})
# Exact seam: all five base actions start/end from the same transparent image.
neutral_hashes={hashlib.sha256((NEW/f'frames/{ac}/{i:03}.png').read_bytes()).hexdigest() for ac in ['talk','point-right','think','celebrate','wave'] for i in [0,11]}
assert len(neutral_hashes)==1
# Diagnose old head movement using original independent feature registration.
reg=json.loads((NEW/'registration/parameters.json').read_text());before=[]
for ac in ['talk','point-right','think','celebrate','wave']:
 rr=[r for r in reg if r['action']==ac];pts=[np.array(r['head_registration'])@np.array([174,171,1]) for r in rr]
 span=np.ptp(pts,axis=0);scales=[float(np.sqrt(abs(np.linalg.det(np.array(r['head_registration'])[:,:2])))) for r in rr]
 before.append({'action':ac,'head_position_span_px':[round(float(x),3) for x in span],'head_scale_range':[round(min(scales),4),round(max(scales),4)]})
# Before/after native animation: same frame number, unchanged stage and scale.
font='/System/Library/Fonts/Supplemental/Arial.ttf';from PIL import ImageFont
f=ImageFont.truetype(font,18);anims=[]
for i in range(12):
 stage=Image.new('RGB',(5*256,424),(246,239,220));draw=ImageDraw.Draw(stage)
 for j,ac in enumerate(['talk','point-right','think','celebrate','wave']):
  draw.text((j*256+8,6),ac,fill='#46392f',font=f)
  for col,L in enumerate([OLD,NEW]):
   im=Image.open(L/f'frames/{ac}/{i:03}.png').resize((128,192));stage.paste(im,(j*256+col*128,36),im)
   draw.text((j*256+col*128+15,240),'BEFORE' if col==0 else 'AFTER',fill='#46392f',font=f)
  new=Image.open(NEW/f'frames/{ac}/{i:03}.png').resize((104,156));stage.paste(new,(j*256+76,268),new)
 anims.append(stage)
anims[0].save(B/'qa/registration-before-after.webp',save_all=True,append_images=anims[1:],duration=100,loop=0,quality=85,method=5)
copy=B/'assets/author-animation';files=list(p for p in NEW.rglob('*') if p.is_file())
assert all((copy/p.relative_to(NEW)).exists() and p.read_bytes()==(copy/p.relative_to(NEW)).read_bytes() for p in files)
report={'source_version':1,'repaired_version':2,'actions':len(M['actions']),'frames':len(rows),'neutral_pose_identical_between_all_base_actions':True,'stable_regions':ROIS,'max_measured_translation_px':0,'max_stable_region_pixel_mae':max(v['pixel_mae'] for r in rows for v in r['fixed_regions'].values()),'before_head_movement':before,'frame_measurements':rows,'cache_copy_files':len(files),'copies_byte_identical':True,'new_image_generation_calls':0,'canvas_edge_clipping':0}
(B/'qa/registration-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='frame_measurements'},ensure_ascii=False,indent=2))
