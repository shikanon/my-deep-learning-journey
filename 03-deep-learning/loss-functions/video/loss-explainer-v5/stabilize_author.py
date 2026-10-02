"""Register existing painted poses to one anatomical reference, then bake clips.

This is deterministic frame registration/compositing of the existing illustration,
not a new generative redraw. Stable body textures remain byte-identical between
poses; generated mouth/eyes/arms retain the authored gestures.
"""
from pathlib import Path
import json,hashlib,shutil,subprocess,math
import cv2,numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;ROOT=B.parents[3]
OLD=ROOT/'assets/手绘形象/shikanon-animation-v1'
LIB=ROOT/'assets/手绘形象/shikanon-animation-v2'
FF='/private/tmp/loss-video-bin/ffmpeg'
W,H=384,576
ACTIONS=['talk','point-right','think','celebrate','wave']
Y,X=np.mgrid[:H,:W]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gray(a):
 alpha=a[:,:,3:4].astype(np.float32)/255
 rgb=a[:,:,:3].astype(np.float32)/255
 return cv2.cvtColor(rgb*alpha+1-alpha,cv2.COLOR_RGB2GRAY)
def ellipse(cx,cy,rx,ry):return (((X-cx)/rx)**2+((Y-cy)/ry)**2<=1)
def feather(mask,r=2):return cv2.GaussianBlur(mask.astype(np.float32),(0,0),r)
def mix(a,b,m):
 # All masks represent complete foreground replacements (including transparent
 # pixels), so a returning arm cannot leave ghosts behind.
 return a*(1-m[:,:,None])+b*m[:,:,None]
def premul(a):
 a=a.astype(np.float32)/255;a[:,:,:3]*=a[:,:,3:4];return a
def unpremul(a):
 b=a.copy();b[:,:,:3]/=np.maximum(b[:,:,3:4],1e-8)
 return np.uint8(np.clip(b*255+.5,0,255))
def warp(a,M):
 return cv2.warpAffine(premul(a),M,(W,H),flags=cv2.INTER_CUBIC|cv2.WARP_INVERSE_MAP)
def fit(base,src,mask):
 bg=gray(base);g=gray(src);m=np.uint8(mask)*255
 sift=cv2.SIFT_create();kp0,d0=sift.detectAndCompute(np.uint8(bg*255),m)
 kp,d=sift.detectAndCompute(np.uint8(g*255),m)
 if d0 is not None and d is not None:
  pairs=cv2.BFMatcher().knnMatch(d0,d,k=2)
  good=[u for u,v in pairs if u.distance<.78*v.distance]
 else:good=[]
 M=np.eye(2,3,dtype=np.float32)
 if len(good)>=4:
  p=np.float32([kp0[u.queryIdx].pt for u in good]);q=np.float32([kp[u.trainIdx].pt for u in good])
  result,_=cv2.estimateAffinePartial2D(p,q,method=cv2.RANSAC,ransacReprojThreshold=2.3,maxIters=4000)
  if result is not None:M=result.astype(np.float32)
 try:score,M=cv2.findTransformECC(bg,g,M,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,150,1e-5),m,5)
 except cv2.error:score=0
 return M,float(score)
def poly(points):
 m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[np.int32(points)],1);return m.astype(np.float32)

def waist(a):
 rgb=a[:,:,:3].astype(int)
 m=(rgb.max(2)<155)&(np.abs(rgb[:,:,0]-rgb[:,:,2])<28)&(a[:,:,3]>150)&(Y>420)&(Y<520)&(X>110)&(X<280)
 wy=int(np.where(m.sum(1)>85)[0].min());ys,xs=np.where(m&(Y>=wy)&(Y<wy+10));lo,hi=np.percentile(xs,[5,95])
 return (float((lo+hi)/2),float(wy),float(hi-lo))

def body_matrix(base,src,head_matrix):
 bx,by,bw=waist(base);sx,sy,sw=waist(src)
 neck_y=float(head_matrix[1]@np.array([174,330,1]))
 xscale=sw/bw;yscale=(sy-neck_y)/(by-330)
 assert .7<xscale<1.3 and .7<yscale<1.4,(xscale,yscale)
 return np.float32([[xscale,0,sx-bx*xscale],[0,yscale,neck_y-330*yscale]])

def bake(action,frames,metadata):
 folder=LIB/'frames'/action;folder.mkdir(parents=True,exist_ok=True)
 fs=[]
 for i,a in enumerate(frames):
  p=folder/f'{i:03}.png';Image.fromarray(a).save(p)
  fs.append({'index':i,'file':str(p.relative_to(LIB)),'sha256':sha(p),'atlas_rect':[i%4*W,i//4*H,W,H],'anchor':[192,548],'head_anchor':[174,241],'waist_anchor':[178,445],'feet_anchor':[192,548],**metadata[i]})
 atlas=Image.new('RGBA',(W*4,H*3))
 for i,a in enumerate(frames):atlas.paste(Image.fromarray(a),(i%4*W,i//4*H))
 ap=LIB/'atlases'/f'{action}.png';atlas.save(ap)
 preview=LIB/'previews'/f'{action}.webp'
 pil=[Image.fromarray(a) for a in frames]
 pil[0].save(preview,save_all=True,append_images=pil[1:],duration=100,loop=0,lossless=True,method=6)
 return {'name':action,'fps':10,'loop':True,'frame_count':12,'columns':4,'rows':3,'atlas':str(ap.relative_to(LIB)),'atlas_size':[W*4,H*3],'atlas_sha256':sha(ap),'preview':str(preview.relative_to(LIB)),'frames':fs,'alpha_background':True,'assembly_note':'Fixed reference head contour, shirt core and legs; registered mouth, eyes and original moving arms. All actions use the same neutral pose and anatomical anchors.'}
for p in ['frames','atlases','previews','props','registration']:(LIB/p).mkdir(parents=True,exist_ok=True)
base=np.array(Image.open(OLD/'frames/talk/000.png'))
# Remove detached near-transparent generation specks, keeping antialiased edges
# belonging to the main subject. The illustration itself is unchanged.
n,labels,stats,_=cv2.connectedComponentsWithStats(np.uint8(base[:,:,3]>16),8)
main=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);support=cv2.dilate(np.uint8(labels==main),np.ones((3,3),np.uint8))
base[:,:,3]*=support
Image.fromarray(base).save(LIB/'registration/reference-neutral.png')
shutil.copy2(OLD/'reference.png',LIB/'reference.png')
fixed=premul(base)
headmask=ellipse(174,176,116,90)
bodymask=(X>123)&(X<233)&(Y>383)&(Y<522)
# Stable full head/ears/hair and trousers. Only a small face interior can change.
facemask=feather(ellipse(175,284,29,18),1.4)
eye_mask=feather(ellipse(131,250,16,8)|ellipse(207,245,16,8),1.0)
blink_source=np.array(Image.open(OLD/'frames/talk/005.png'))
blink_matrix,_=fit(base,blink_source,headmask)
blink=warp(blink_source,blink_matrix)
headweight=(1-np.clip((Y-317)/24,0,1))*((X<282)|(Y<230))
core=feather(poly([(138,335),(220,335),(240,368),(237,442),(117,442),(117,380)]),1.6)
legs=np.clip((Y-445)/6,0,1)*(((X>105)&(X<249))|(Y>471))
# Keep shoulder joins exact, with a narrow feathered overlap into the sleeve.
headweight=np.maximum(headweight,facemask*0)
manifest={'schema':'shikanon-sprite-library/v2','version':2,'character':'shikanon','style':'children-colored-pencil','source_image':'reference.png','source_sha256':sha(LIB/'reference.png'),'frame_size':[W,H],'anchor':[192,548],'anatomical_anchors':{'head':[174,241],'waist':[178,445],'feet':[192,548]},'generator':'Existing built-in image_gen poses, repaired by deterministic OpenCV anatomical registration and native SVG props','repair_source':'../shikanon-animation-v1/manifest.json','actions':{}}
registered={};audit=[]
for action in ACTIONS:
 frames=[];meta=[]
 for i in range(12):
  src=np.array(Image.open(OLD/f'frames/{action}/{i:03}.png'))
  hm,hs=fit(base,src,headmask);bm=body_matrix(base,src,hm);bs=0
  head=warp(src,hm);body=warp(src,bm)
  # Start with the aligned arms, then pin immutable contours/core/legs.
  repaired=mix(body,fixed,core)
  repaired=mix(repaired,fixed,legs)
  if action in ['talk','point-right','wave']:
   repaired=mix(repaired,fixed,feather((X<118)&(Y>333)&(Y<471),1.3))
  if action=='think':
   repaired=mix(repaired,fixed,feather((X>237)&(Y>333)&(Y<471),1.3))
  repaired=mix(repaired,fixed,headweight)
  repaired=mix(repaired,head,facemask)
  if i==5 or (action in ['celebrate','wave'] and i==6):repaired=mix(repaired,blink,eye_mask)
  # Foreground thinking hand passes in front of the fixed chin. Keep only the
  # original registered foreground hand, never a second face or hair boundary.
  if action=='think' and i in range(2,10):
   handmask=feather(poly([(105,345),(117,315),(145,295),(178,296),(181,340),(169,363),(125,372)]),1.3)
   # Below the chin all pixels are sleeve/hand; above it the skin-color gate
   # prevents copying the source's glasses or facial outlines.
   handmask*=np.clip((Y-302)/12,0,1)
   repaired=mix(repaired,head,handmask)
  if action=='celebrate' and i in range(2,10):
   handmask=feather(np.maximum(poly([(60,348),(70,309),(99,299),(127,315),(125,355),(108,380),(65,376)]),poly([(230,311),(257,298),(286,313),(298,353),(286,380),(246,371)])),1.2)
   repaired=mix(repaired,body,handmask)
  # One exact neutral pose closes each action, avoiding identity/scale pops at
  # action changes. Frame 0 and 11 use the same reference across every action.
  if i in [0,11]:repaired=fixed.copy()
  out=unpremul(repaired);frames.append(out)
  m={'source_action':action,'source_frame':i,'head_registration':hm.tolist(),'body_registration':bm.tolist(),'head_ecc':round(hs,6),'body_registration_method':'waist-width and neck-height constrained diagonal transform','neutral_reference':i in [0,11]}
  meta.append(m);audit.append({'action':action,'frame':i,**m})
 registered[action]=frames
 manifest['actions'][action]=bake(action,frames,meta)
 print(action,'head',round(min(m['head_ecc'] for m in meta),3),'body','waist/neck constrained',flush=True)
# Props are native SVG educational annotations. These can be reused separately
# or taken from the baked transparent action frames below.
question='''<svg xmlns="http://www.w3.org/2000/svg" width="384" height="576" viewBox="0 0 384 576"><g fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M164 39 C164 15 199 12 200 36 C200 48 183 48 183 59" stroke="#46392f" stroke-width="12"/><path d="M164 39 C164 15 199 12 200 36 C200 48 183 48 183 59" stroke="#ed826a" stroke-width="7"/><circle cx="183" cy="76" r="6" fill="#46392f"/><circle cx="183" cy="75" r="3.2" fill="#ed826a"/></g></svg>'''
(LIB/'props/question.svg').write_text(question)
pointer='''<svg xmlns="http://www.w3.org/2000/svg" width="384" height="576" viewBox="0 0 384 576"><g stroke-linecap="round"><path d="M302 313 L366 167" stroke="#46392f" stroke-width="7"/><path d="M302 313 L366 167" stroke="#be8756" stroke-width="3.5"/><path d="M362 176 L366 167" stroke="#ed826a" stroke-width="5"/></g></svg>'''
(LIB/'props/teaching-pointer.svg').write_text(pointer)
# Rasterize vector props with the SVG renderer (the artwork remains original).
import io
from svg_raster import rasterize
qp=np.array(Image.open(io.BytesIO(rasterize(question))))
qm=premul(qp)
questionframes=[]
for i,a in enumerate(registered['think']):
 # Reveal once, hold still above the head; opacity easing is intentional.
 opacity=1
 fg=qm*opacity;bg=premul(a);questionframes.append(unpremul(fg+bg*(1-fg[:,:,3:4])))
manifest['actions']['think-question']=bake('think-question',questionframes,[{'source_action':'think','source_frame':i,'prop':'props/question.svg'} for i in range(12)])
pointerframes=[]
for i,a in enumerate(registered['point-right']):
 # Attach the pointer to the registered palm, independently of the moving arm's
 # outer alpha bbox. Its tip stays above/right of the hand, inside the canvas.
 rgba=a[:,:,:3];skin=(rgba[:,:,0]>170)&(rgba[:,:,1]>100)&(rgba[:,:,1]<210)&(rgba[:,:,2]<165)&(a[:,:,3]>100)&(X>249)&(Y>260)&(Y<468)
 n,lab,st,_=cv2.connectedComponentsWithStats(np.uint8(skin),8)
 if n>1:
  cc=1+np.argmax(st[1:,cv2.CC_STAT_AREA]);ys,xs=np.where(lab==cc);hx=float(np.median(xs));hy=float(np.median(ys))
 else:hx,hy=274,450
 tx=min(374,hx+65);ty=max(137,hy-146)
 svg=pointer.replace('M302 313 L366 167',f'M{hx:.2f} {hy:.2f} L{tx:.2f} {ty:.2f}').replace('M362 176 L366 167',f'M{tx-4:.2f} {ty+9:.2f} L{tx:.2f} {ty:.2f}')
 pr=premul(np.array(Image.open(io.BytesIO(rasterize(svg)))))
 if i in [0,11]:pr*=0
 # Draw behind the hand so fingers visibly overlap the wooden shaft.
 bg=premul(a);mixframe=bg+pr*(1-bg[:,:,3:4]);pointerframes.append(unpremul(mixframe))
manifest['actions']['teach-pointer']=bake('teach-pointer',pointerframes,[{'source_action':'point-right','source_frame':i,'prop':'props/teaching-pointer.svg'} for i in range(12)])
(LIB/'registration/parameters.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
(LIB/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
# Visual contact sheet, generated from the exact files delivered to both places.
contact=Image.new('RGB',(4*192,7*288),(246,239,220))
for row,action in enumerate(manifest['actions']):
 for col,i in enumerate([0,3,6,9]):
  p=Image.open(LIB/f'frames/{action}/{i:03}.png').resize((192,288));contact.paste(p,(col*192,row*288),p)
contact.save(B/'qa/repaired-contact.png')
shutil.copytree(LIB,B/'assets/author-animation',dirs_exist_ok=True)
print(json.dumps({'cache':str(LIB),'video_copy':str(B/'assets/author-animation'),'actions':7,'frames':84},ensure_ascii=False))
