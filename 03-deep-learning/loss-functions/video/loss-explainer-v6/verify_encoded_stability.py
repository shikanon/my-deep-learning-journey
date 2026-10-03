"""Check closed-smile pixels and torso stability in newly encoded video."""
from pathlib import Path
import cv2,numpy as np,json,subprocess,hashlib,math
from PIL import Image,ImageDraw
from author_motion import sample_actor
B=Path(__file__).resolve().parent;FF='/private/tmp/loss-video-bin/ffmpeg';V=B/'renders/loss-functions-v6.mp4';L=B/'assets/author-animation'
S=json.loads((B/'storyboard.json').read_text());M=json.loads((L/'manifest.json').read_text());C=json.loads((B/'qa/browser-rig-placements.json').read_text())['cases']
actors={a['id']:a for s in S['scenes'] for a in s['actors']}
reports=[];contact=Image.new('RGB',(7*192,3*216),'#FFF7E4');draw=ImageDraw.Draw(contact)
for ci,c in enumerate(C):
 a,b,d,e,tx,ty=c['local_to_video'];st=math.ceil(c['start']*30);count=math.floor(c['duration']*10)
 # yuv420 crops round odd origins to the chroma grid; explicitly align both
 # coordinates so measured source and decoded pixels share the same origin.
 x=max(0,int(tx)-3);x-=x%2;y=max(0,int(ty)-3);y-=y%2
 w=2*math.ceil((a*384+8)/2);h=2*math.ceil((e*576+8)/2)
 raw=subprocess.run([FF,'-hide_banner','-loglevel','error','-ss',str(st/30),'-i',str(V),'-vf',fr'select=not(mod(n\,3)),crop={w}:{h}:{x}:{y}','-fps_mode','vfr','-frames:v',str(count),'-f','rawvideo','-pix_fmt','rgb24','pipe:1'],check=True,capture_output=True).stdout
 frames=np.frombuffer(raw,np.uint8).reshape((-1,h,w,3));assert len(frames)==count
 # Transform actual source frame into the encoded actor's measured screen area.
 screen=np.float64([[a,d,tx-x],[b,e,ty-y]]);errors=[];details=[];torso=[]
 for i,decoded in enumerate(frames):
  t=(st+i*3)/30;pose=sample_actor(actors[c['actor']],t);f=M['actions'][pose['action']]['frames'][pose['sprite_frame']]
  sprite=np.array(Image.open(L/f['file']));rgb=sprite[:,:,:3]
  # Area-sample source pixels with correct pixel-center coordinates. The
  # browser minifies the raster, so a four-sample bilinear reference aliases.
  def render_reference(rgba):
   alpha=rgba[:,:,3:4].astype(np.float32)/255
   pixels=rgba[:,:,:3]*alpha+np.float32([255,247,228])*(1-alpha)
   ss=4;mat=screen*ss;mat[:,2]+=[ss*(a*.5+d*.5)-.5,ss*(b*.5+e*.5)-.5]
   large=cv2.warpAffine(pixels,mat,(w*ss,h*ss),flags=cv2.INTER_LINEAR)
   return cv2.resize(large,(w,h),interpolation=cv2.INTER_AREA)
  expected=render_reference(sprite)
  mouthmask=np.zeros((576,384),np.uint8);mouthmask[275:298,153:200]=1
  hm=np.float64(f['head_transform']);mouthmask=cv2.warpAffine(mouthmask,hm,(384,576),flags=cv2.INTER_NEAREST)
  mouthmask=cv2.warpAffine(mouthmask,screen,(w,h),flags=cv2.INTER_NEAREST)>0
  error=float(np.abs(decoded[mouthmask].astype(float)-expected[mouthmask].astype(float)).mean());errors.append(error)
  # Negative control: the old open talking mouth must fit encoded pixels worse
  # than the fixed smile. This tolerates real H.264/minification differences
  # without accepting an open mouth under a loose absolute-error threshold.
  opened=np.array(Image.open(L/'source/registered-art/frames/talk/006.png'))
  opened=cv2.warpAffine(opened,hm,(384,576),flags=cv2.INTER_CUBIC)
  negative=render_reference(opened)
  open_error=float(np.abs(decoded[mouthmask].astype(float)-negative[mouthmask].astype(float)).mean())
  assert error<open_error*.72,(c['action'],t,'encoded mouth is not clearly closer to closed smile',error,open_error)
  # Torso remains still while hands, head and feet make intentional gestures.
  p=np.array([[[151,379],[229,415]]],np.float32);z=cv2.transform(p,screen)[0];x1,y1=np.ceil(z[0]+2).astype(int);x2,y2=np.floor(z[1]-2).astype(int)
  torso.append(decoded[y1:y2,x1:x2]);details.append({'time':round(t,5),'sprite_frame':pose['sprite_frame'],'closed_smile_error':round(error,4),'open_mouth_negative_control_error':round(open_error,4),'closed_open_error_ratio':round(error/open_error,4)})
  if i in [0,count//2,count-1]:
   row=0 if i==0 else 1 if i==count//2 else 2
   p=Image.fromarray(decoded).resize((144,216));contact.paste(p,(ci*192+24,row*216));draw.text((ci*192+3,row*216+4),f"{c['action']} {t:.2f}",fill='#46392F')
 drifts=[];diffs=[];ref=torso[0]
 for patch in torso:
  diffs.append(float(np.abs(patch.astype(float)-ref.astype(float)).mean()))
 assert max(diffs)<3.5,(c['action'],'encoded torso drift',max(diffs))
 # Compare first and an opposite phase inside the same screen region.
 change=float(np.max([np.abs(f.astype(float)-frames[0].astype(float)).mean() for f in frames]))
 assert change>.35,(c['action'],'character motion missing',change)
 reports.append({'action':c['action'],'actor':c['actor'],'decoded_frames':count,'mouth_error_mean':round(float(np.mean(errors)),4),'mouth_error_max':round(max(errors),4),'torso_pixel_difference_max':round(max(diffs),4),'intentional_motion_pixel_difference_max':round(change,4),'samples':details})
contact.save(B/'qa/encoded-rig-contact.jpg',quality=94)
report={'video':V.name,'sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'decoded_frames':sum(r['decoded_frames'] for r in reports),'verified_actions':len(reports),'mouth_animation':False,'head_and_foot_motion_intentional':True,'mouth_reference_verified_in_encoded_pixels':True,'torso_stable':True,'max_mouth_error':max(r['mouth_error_max'] for r in reports),'max_closed_open_error_ratio':max(s['closed_open_error_ratio'] for r in reports for s in r['samples']),'cases':reports}
(B/'qa/encoded-stability.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
