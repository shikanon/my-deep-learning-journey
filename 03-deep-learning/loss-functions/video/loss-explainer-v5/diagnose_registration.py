"""Compare head registration, shirts and feet; diagnostics, not frame generation."""
from pathlib import Path
import cv2, numpy as np,json
from PIL import Image
B=Path(__file__).resolve().parent
L=B.parents[3]/'assets/手绘形象/shikanon-animation-v1'
base=np.array(Image.open(L/'frames/talk/000.png'))
def gray(a):
 r=a[:,:,:3].astype(np.float32)/255;alpha=a[:,:,3:4]/255
 return cv2.cvtColor((r*alpha+(1-alpha)).astype(np.float32),cv2.COLOR_RGB2GRAY)
bg=gray(base); yy,xx=np.mgrid[:576,:384]
mask=(((xx-183)/116)**2+((yy-171)/90)**2<1).astype(np.uint8)*255
sift=cv2.SIFT_create();kp0,d0=sift.detectAndCompute((bg*255).astype(np.uint8),mask)
rows=[];cells=[]
for action in ['talk','point-right','think','celebrate','wave']:
 for i in range(12):
  a=np.array(Image.open(L/f'frames/{action}/{i:03}.png'));g=gray(a)
  k,d=sift.detectAndCompute((g*255).astype(np.uint8),mask)
  matches=cv2.BFMatcher().knnMatch(d0,d,k=2)
  good=[x for x,y in matches if x.distance<.8*y.distance]
  p=np.array([kp0[m.queryIdx].pt for m in good]);q=np.array([k[m.trainIdx].pt for m in good]);T=None
  if len(p)>=3:
   T,inliers=cv2.estimateAffinePartial2D(p,q,method=cv2.RANSAC,ransacReprojThreshold=2,maxIters=4000)
  if T is None:T=np.eye(2,3)
  W=T.astype(np.float32)
  try:score,W=cv2.findTransformECC(bg,g,W,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,120,1e-5),mask,5)
  except cv2.error:score=0
  reg=cv2.warpAffine(a,W,(384,576),flags=cv2.INTER_CUBIC|cv2.WARP_INVERSE_MAP)
  rows.append({'action':action,'frame':i,'ecc':score,'matrix':W.tolist(),'sift_matches':len(good)})
  if i in [0,4,7,11]:
   cell=Image.new('RGB',(192,288),(246,239,220));img=Image.fromarray(reg).resize((192,288));cell.paste(img,(0,0),img);cells.append(cell)
mont=Image.new('RGB',(192*4,288*5),(246,239,220))
for j,c in enumerate(cells):mont.paste(c,(j%4*192,j//4*288))
mont.save(B/'qa/head-registration-contact.png')
(B/'qa/head-registration.json').write_text(json.dumps(rows,indent=2))
for action in ['talk','point-right','think','celebrate','wave']:
 rr=[r for r in rows if r['action']==action];print(action,round(min(r['ecc'] for r in rr),3),round(max(r['ecc'] for r in rr),3),'sift',min(r['sift_matches'] for r in rr))
