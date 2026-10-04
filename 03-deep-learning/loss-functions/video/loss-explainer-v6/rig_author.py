"""Reuse registered artwork with a single closed-smile face and explicit joints.

No face or lip animation is sampled from the old frames. Hands retain the
existing painted poses; head and lower legs use deterministic rigid transforms.
Required registered source art is preserved inside this video project.
"""
from pathlib import Path
import hashlib,json,math,shutil
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont

B=Path(__file__).resolve().parent;ROOT=B.parents[3]
LIB=B/'assets/author-animation'
SOURCE=LIB/'source/registered-art'
W,H=384,576;COUNT=24;FPS=20
Y,X=np.mgrid[:H,:W]
ACTIONS=['talk','point-right','think','celebrate','wave','think-question','teach-pointer','step']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def premul(a):
 a=a.astype(np.float32)/255;a[:,:,:3]*=a[:,:,3:4];return a
def unpremul(a):
 b=a.copy();b[:,:,:3]/=np.maximum(b[:,:,3:4],1e-8)
 return np.uint8(np.clip(b*255+.5,0,255))
def over(a,b):return a+b*(1-a[:,:,3:4])
def part(a,m):return a*m[:,:,None]
def transform(a,angle,pivot,dx=0,dy=0):
 matrix=cv2.getRotationMatrix2D(pivot,angle,1);matrix[:,2]+=[dx,dy]
 return cv2.warpAffine(a,matrix,(W,H),flags=cv2.INTER_CUBIC),matrix.tolist()
def save_rgba(a,path):Image.fromarray(unpremul(a)).save(path)
for d in ['frames','props','rig']:(LIB/d).mkdir(parents=True,exist_ok=True)
base=np.array(Image.open(SOURCE/'registration/reference-neutral.png'))
fixed=premul(base)
shutil.copy2(SOURCE/'reference.png',LIB/'reference.png')
shutil.copy2(SOURCE/'registration/reference-neutral.png',LIB/'rig/reference-neutral.png')
# Same complete head, eyes and closed curved smile in every frame. The neck
# overlap is below the chin; the original moving face is never composited.
head_mask=(1-np.clip((Y-320)/15,0,1))*((X<282)|(Y<230))
head=part(fixed,head_mask)
save_rgba(head,LIB/'rig/head-closed-smile.png')
# Lower-leg layers must exclude the neutral palms, whose fingertips also reach
# y=466. A simple horizontal cut accidentally attaches those fingers to feet.
leg_region=((Y<480)&(X>108)&(X<250))|((Y>=480)&(X>80)&(X<276))
left_mask=np.clip((Y-462)/8,0,1)*(X<177)*leg_region
right_mask=np.clip((Y-462)/8,0,1)*(X>=177)*leg_region
leg_mask=left_mask+right_mask
left=part(fixed,left_mask);right=part(fixed,right_mask)
save_rgba(left,LIB/'rig/leg-left.png');save_rgba(right,LIB/'rig/leg-right.png')
save_rgba(part(fixed,1-head_mask),LIB/'rig/body-neutral.png')
mouth_box=[151,273,202,301]
Image.fromarray(base[273:301,151:202]).save(LIB/'rig/mouth-reference.png')
manifest={'schema':'author-png-sequence/v1','version':1,'storage':'transparent-png-sequence','character':'shikanon','style':'children-colored-pencil','source_image':'reference.png','source_sha256':sha(LIB/'reference.png'),'frame_size':[W,H],'anchor':[192,548],'generator':'Existing registered artwork, immutable closed-smile head layer, deterministic head/leg joints and existing SVG props','repair_source':'source/registered-art/manifest.json','mouth_animation':False,'facial_expression':'closed-smile','rig':{'head_layer':'rig/head-closed-smile.png','head_sha256':sha(LIB/'rig/head-closed-smile.png'),'mouth_reference':'rig/mouth-reference.png','mouth_sha256':sha(LIB/'rig/mouth-reference.png'),'mouth_box_head_local':mouth_box,'head_pivot':[174,333],'left_leg_pivot':[143,463],'right_leg_pivot':[209,463],'body_scale':1,'head_scale':1,'notes':'Motion is intentional rigid rotation around named joints, never per-frame recentering or generated face deformation.'},'actions':{}}
cache={a:[premul(np.array(Image.open(SOURCE/f'frames/{a}/{i:03}.png'))) for i in range(12)] for a in ACTIONS if a!='step'}
# Question belongs to the head gesture. The pointer stays with its painted hand.
question=cache['think-question'][0]-cache['think'][0]
question=np.clip(question,0,1)
shutil.copytree(SOURCE/'props',LIB/'props',dirs_exist_ok=True)
save_rgba(question,LIB/'rig/question.png')
all_frames={}
for action in ACTIONS:
 frames=[];meta=[];folder=LIB/'frames'/action;folder.mkdir(exist_ok=True)
 for i in range(COUNT):
  phase=i/(COUNT-1);u=math.sin(math.pi*phase)**2
  source_action='talk' if action=='step' else 'think' if action=='think-question' else action
  source_index=min(11,int(phase*11+.5))
  src=cache[source_action][source_index].copy()
  # Replace the entire original head, then separate it from the lower body.
  src=src*(1-head_mask[:,:,None])+fixed*head_mask[:,:,None]
  body=part(src,(1-head_mask)*(1-leg_mask))
  # Raised-arm poses inherited a tiny fragment of the old resting hand below
  # the waist. Clear only that old hand location, after locating the real palm.
  if action in ['think','think-question','celebrate'] and source_index in range(2,10):
   body[(X<106)&(Y>448)&(Y<474)]=0
  if action=='celebrate' and source_index in range(2,10):
   body[(X>248)&(Y>448)&(Y<474)]=0
  if action in ['talk','point-right','wave','teach-pointer','step']:
   skin=(src[:,:,0]>src[:,:,1]*1.12)&(src[:,:,1]>src[:,:,2]*1.05)&(src[:,:,3]>.5)&(X>249)&(Y>260)&(Y<468)
   n,lab,stats,_=cv2.connectedComponentsWithStats(np.uint8(skin),8)
   if n>1:
    palm=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);ys,_=np.where(lab==palm)
    if np.median(ys)<428:body[(X>248)&(Y>448)&(Y<474)]=0
  angle=(2.0 if action in ['talk','step'] else -2.2 if action in ['think','think-question'] else 1.7 if action in ['point-right','teach-pointer'] else 2.5)*u
  nod=1.7*math.sin(2*math.pi*phase)*u if action in ['talk','celebrate'] else 0
  moving_head,hm=transform(head,angle,(174,333),0,nod)
  foot_amp=2.6 if action=='step' else 1.7 if action in ['celebrate','wave'] else .7
  foot=foot_amp*math.sin(2*math.pi*phase)*u
  lift=3.0 if action=='step' else 1.5 if action in ['celebrate','wave'] else .5
  la,ra=foot,-foot
  ld=-lift*max(0,math.sin(2*math.pi*phase))*u
  rd=-lift*max(0,-math.sin(2*math.pi*phase))*u
  ll,lm=transform(left,la,(143,463),0,ld);rr,rm=transform(right,ra,(209,463),0,rd)
  # Non-overlapping anatomical parts are additive. Premultiplied edge colors
  # remain correct when composited on either a cream or a dark background.
  out=body+ll+rr+moving_head
  # Restore the pre-existing foreground thinking hand, below the mouth. The
  # face above y=306 still comes solely from the shared closed-smile head.
  if action in ['think','think-question'] and source_index in range(2,10):
   mask=np.zeros((H,W),np.float32)
   cv2.fillPoly(mask,[np.int32([(105,345),(117,315),(145,303),(178,303),(181,340),(169,363),(125,372)])],1)
   mask=cv2.GaussianBlur(mask,(0,0),1.2)*np.clip((Y-305)/9,0,1)
   hand=part(cache['think'][source_index],mask)
   out=out*(1-mask[:,:,None])+hand
  if action=='celebrate' and source_index in range(2,10):
   mask=np.zeros((H,W),np.float32)
   for points in [[(60,348),(70,309),(99,299),(127,315),(125,355),(108,380),(65,376)],[(230,311),(257,298),(286,313),(298,353),(286,380),(246,371)]]:
    cv2.fillPoly(mask,[np.int32(points)],1)
   mask=cv2.GaussianBlur(mask,(0,0),1.2)
   out=out*(1-mask[:,:,None])+part(cache['celebrate'][source_index],mask)
  if action=='think-question':
   q,_=transform(question,angle,(174,333),0,nod);out=over(q,out)
  # The first and last frame are the same neutral pose in all base actions.
  if i in [0,COUNT-1]:out=fixed.copy();out=over(question,out) if action=='think-question' else out
  rgba=unpremul(np.clip(out,0,1))
  # Registration left a few disconnected old-hand pixels below the raised
  # sleeves. Remove only detached fragments, preserving the deliberate question
  # symbol above the head and the antialiased main character edges.
  n,labels,stats,_=cv2.connectedComponentsWithStats(np.uint8(rgba[:,:,3]>16),8)
  main=1+np.argmax(stats[1:,cv2.CC_STAT_AREA]);keep=labels==main
  if action=='think-question':keep|=(Y<86)&(labels>0)
  support=cv2.dilate(np.uint8(keep),np.ones((3,3),np.uint8));rgba[:,:,3]*=support
  p=folder/f'{i:03}.png';Image.fromarray(rgba).save(p);frames.append(rgba)
  meta.append({'index':i,'file':str(p.relative_to(LIB)),'sha256':sha(p),'anchor':[192,548],'source_action':source_action,'source_frame':source_index,'mouth_animation':False,'head_layer_sha256':manifest['rig']['head_sha256'],'head_angle_deg':round(angle,6),'head_offset_px':[0,round(nod,6)],'head_transform':hm,'left_leg_angle_deg':round(la,6),'right_leg_angle_deg':round(ra,6),'left_leg_offset_px':[0,round(ld,6)],'right_leg_offset_px':[0,round(rd,6)],'left_leg_transform':lm,'right_leg_transform':rm,'neutral_reference':i in [0,COUNT-1]})
 manifest['actions'][action]={'name':action,'fps':FPS,'loop':True,'frame_count':COUNT,'frames':meta,'alpha_background':True,'mouth_animation':False,'assembly_note':'One closed-smile head texture, original hand gestures, smooth intentional head/foot joints; no lip or eye animation.'}
 all_frames[action]=frames
 print(action,COUNT,'frames, closed smile, explicit head/feet joints',flush=True)
(LIB/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
contact=Image.new('RGB',(4*192,8*312),(246,239,220));draw=ImageDraw.Draw(contact)
for row,action in enumerate(ACTIONS):
 for col,i in enumerate([0,6,12,18]):
  p=Image.fromarray(all_frames[action][i]).resize((192,288));contact.paste(p,(col*192,row*312+24),p)
 draw.text((8,row*312+5),action,fill='#46392f')
contact.save(B/'qa/fixed-smile-contact.png')
print(json.dumps({'sequence_library':str(LIB),'source_inputs':str(SOURCE),'actions':len(ACTIONS),'frames':len(ACTIONS)*COUNT,'storage':'transparent-png-sequence','mouth_animation':False},ensure_ascii=False))
