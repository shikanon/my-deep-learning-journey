"""Check anatomical drift in fresh H.264 output at unchanged screen positions."""
from pathlib import Path
import cv2,numpy as np,json,subprocess,hashlib
B=Path(__file__).resolve().parent;FF='/private/tmp/loss-video-bin/ffmpeg';V=B/'renders/loss-functions-v5.mp4'
# These screen coordinates were measured from the live V5 SVG getScreenCTM,
# with a 2 px inner margin. Scene placement and camera remain fixed here.
CASES=[
 ('talk',7.05,2.8,{'hair':[238,803,395,883],'shirt':[304,1007,354,1027],'feet':[253,1076,386,1123]}),
 ('think-question',17.82,2.0,{'hair':[355,1146,445,1191],'shirt':[393,1266,421,1276],'feet':[364,1307,440,1333]}),
 ('point-right',127.09,3.5,{'hair':[252,650,328,688],'shirt':[285,752,307,760],'feet':[260,787,324,808]}),
 ('celebrate',167.96,2.0,{'hair':[237,1174,313,1212],'shirt':[270,1276,293,1284],'feet':[245,1310,309,1332]}),
 ('wave',176.15,2.6,{'hair':[233,606,426,706],'shirt':[313,856,376,882],'feet':[251,941,416,1000]}),
]
reports=[]
for ac,start,duration,rois in CASES:
 paths=B/'qa'/f'stability-{ac}';paths.mkdir(exist_ok=True)
 # Extract actual compressed frames at ten samples/second. No player screenshot
 # or source atlas can substitute for the final encoded video.
 subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-ss',str(start),'-i',str(V),'-t',str(duration),'-vf','fps=10','-frames:v',str(int(duration*10)) ,str(paths/'%03d.png')],check=True)
 imgs=[cv2.imread(str(p)) for p in sorted(paths.glob('*.png'))];ref=imgs[0];details={}
 for name,(x,y,x2,y2) in rois.items():
  template=ref[y:y2,x:x2];moves=[];diff=[]
  for a in imgs:
   search=a[y-4:y2+4,x-4:x2+4];result=cv2.matchTemplate(search,template,cv2.TM_SQDIFF_NORMED);_,_,at,_=cv2.minMaxLoc(result)
   moves.append([at[0]-4,at[1]-4]);diff.append(float(np.abs(a[y:y2,x:x2].astype(float)-template).mean()))
  maxdrift=max(max(abs(v) for v in pair) for pair in moves)
  assert maxdrift<=1,(ac,name,maxdrift,moves)
  assert max(diff)<3.5,(ac,name,max(diff))
  details[name]={'screen_roi':[x,y,x2,y2],'max_translation_px':maxdrift,'mean_pixel_difference':round(float(np.mean(diff)),3),'max_pixel_difference':round(max(diff),3),'measured_translations':moves}
 reports.append({'action':ac,'start':start,'duration':duration,'decoded_frames':len(imgs),'anatomical_regions':details})
report={'video':V.name,'video_sha256':hashlib.sha256(V.read_bytes()).hexdigest(),'sampled_decoded_frames':sum(r['decoded_frames'] for r in reports),'max_measured_translation_px':max(q['max_translation_px'] for r in reports for q in r['anatomical_regions'].values()),'all_frames_keep_same_screen_rois':True,'cases':reports}
(B/'qa/encoded-stability.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
