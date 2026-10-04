"""Verify delivered frame pixels: fixed mouth texture, articulated limbs, no drift."""
from pathlib import Path
import cv2,numpy as np,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent;L=B/'assets/author-animation'
CACHE=B.parents[3]/'assets/手绘形象/日常服动作序列帧'
M=json.loads((L/'manifest.json').read_text());W,H=M['frame_size']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def premul(a):
 a=a.astype(np.float32)/255;a[:,:,:3]*=a[:,:,3:4];return a
def unpremul(a):
 b=a.copy();b[:,:,:3]/=np.maximum(b[:,:,3:4],1e-8)
 return np.uint8(np.clip(b*255+.5,0,255))
head=premul(np.array(Image.open(L/M['rig']['head_layer'])))
base=np.array(Image.open(L/'rig/reference-neutral.png'))
mask=np.zeros((H,W),np.uint8);mask[275:298,153:200]=1
assert not M['mouth_animation'] and M['facial_expression']=='closed-smile'
assert sha(L/M['rig']['head_layer'])==M['rig']['head_sha256']
assert sha(L/M['rig']['mouth_reference'])==M['rig']['mouth_sha256']
rows=[];actions={};neutral=set()
for name,m in M['actions'].items():
 assert not m['mouth_animation']
 previous=None;head_deltas=[];leg_deltas=[];frames=[]
 for f in m['frames']:
  p=L/f['file'];assert sha(p)==f['sha256'];a=np.array(Image.open(p));frames.append(a)
  assert a.shape==(H,W,4) and not f['mouth_animation']
  assert f['head_layer_sha256']==M['rig']['head_sha256']
  hm=np.float64(f['head_transform']);assert abs(np.linalg.det(hm[:,:2])-1)<1e-6
  expected=unpremul(np.clip(cv2.warpAffine(head,hm,(W,H),flags=cv2.INTER_CUBIC),0,1))
  mm=cv2.warpAffine(mask,hm,(W,H),flags=cv2.INTER_NEAREST)>0
  d=np.abs(a[mm].astype(int)-expected[mm].astype(int));err=int(d.max())
  assert err<=1,(name,f['index'],'mouth altered',err)
  shirt=np.abs(a[379:415,151:229].astype(int)-base[379:415,151:229].astype(int))
  assert shirt.max()==0,(name,f['index'],'torso drift',shirt.max())
  assert not (a[:2,:,3]>50).any() and not (a[-2:,:,3]>50).any() and not (a[:,:2,3]>50).any() and not (a[:,-2:,3]>50).any()
  if previous:
   delta=abs(f['head_angle_deg']-previous['head_angle_deg']);head_deltas.append(delta);assert delta<.36
   for k in ['left_leg_angle_deg','right_leg_angle_deg']:
    delta=abs(f[k]-previous[k]);leg_deltas.append(delta);assert delta<.72,(name,f['index'],'leg discontinuity',delta)
  previous=f
  rows.append({'action':name,'frame':f['index'],'mouth_texture_max_error':err,'torso_max_pixel_difference':int(shirt.max())})
 assert np.array_equal(frames[0],frames[-1]),(name,'loop seam')
 if name!='think-question':neutral.add(sha(L/m['frames'][0]['file']))
 head_change=int(np.max([np.abs(a[91:310,59:287].astype(int)-frames[0][91:310,59:287].astype(int)).mean() for a in frames]))
 foot_change=float(np.max([np.abs(a[477:555,80:275].astype(int)-frames[0][477:555,80:275].astype(int)).mean() for a in frames]))
 arm_change=float(np.max([np.abs(a[335:470,240:350].astype(int)-frames[0][335:470,240:350].astype(int)).mean() for a in frames]))
 assert head_change>1 and foot_change>.3,(name,'rig not moving',head_change,foot_change)
 if name in ['talk','point-right','celebrate','wave','teach-pointer','step']:assert arm_change>2,(name,'hand not moving',arm_change)
 actions[name]={'frames':m['frame_count'],'fps':m['fps'],'max_head_angle_step_deg':max(head_deltas),'max_leg_angle_step_deg':max(leg_deltas),'head_changed_pixels_mean_max':head_change,'foot_changed_pixels_mean_max':round(foot_change,4),'arm_changed_pixels_mean_max':round(arm_change,4),'first_last_frames_identical':True}
assert len(neutral)==1,'action entry poses differ'
files=[L/f['file'] for action in M['actions'].values() for f in action['frames']]
assert all(p.read_bytes()==(CACHE/p.relative_to(L)).read_bytes() for p in files)
report={'storage':'transparent-png-sequence','mouth_animation':False,'expression':'closed-smile','actions':actions,'frames_verified':len(rows),'max_mouth_texture_error':max(r['mouth_texture_max_error'] for r in rows),'max_torso_drift':0,'canvas_edge_clipping':0,'shared_neutral_pose':True,'cache_copy_files':len(files),'copies_byte_identical':True,'new_image_generation_calls':0,'measurements':rows}
(B/'qa/rig-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='measurements'},ensure_ascii=False,indent=2))
