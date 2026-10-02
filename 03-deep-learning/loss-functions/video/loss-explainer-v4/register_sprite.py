"""Extract generated grids, anchor transparent frames, cache and sync the library."""
import argparse,hashlib,json,math,shutil,subprocess,statistics
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

B=Path(__file__).resolve().parent
ROOT=B.parents[3]
LIB=ROOT/'assets/手绘形象/shikanon-animation-v1'
FF='/private/tmp/loss-video-bin/ffmpeg'
WIDTH,HEIGHT=384,576
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):subprocess.run([FF,'-hide_banner','-loglevel','error','-y',*args],check=True)

def register(action,source,columns=4,rows=3):
    for d in ['atlases','frames','previews','prompts']:(LIB/d).mkdir(parents=True,exist_ok=True)
    raw=LIB/'atlases'/f'{action}-generated.png';shutil.copy2(source,raw)
    im=Image.open(raw);aw,ah=im.size
    assert im.mode=='RGBA',f'{action}: missing alpha'
    alpha=np.array(im.getchannel('A'))
    assert (alpha==0).mean()>.10,f'{action}: no real transparency'
    cw,ch=aw/columns,ah/rows
    out=LIB/'frames'/action;out.mkdir(exist_ok=True)
    rawcells=LIB/'atlases'/f'.{action}-cells';rawcells.mkdir(exist_ok=True)
    # Generated grids can have a hand across a nominal cell boundary. Locate
    # each complete subject in the original alpha; never cut on a guessed grid.
    n,labels,stats,centers=cv2.connectedComponentsWithStats((alpha>20).astype('uint8'),8)
    subjects=sorted(range(1,n),key=lambda i:int(stats[i,cv2.CC_STAT_AREA]),reverse=True)[:columns*rows]
    assert len(subjects)==columns*rows and min(stats[i,cv2.CC_STAT_AREA] for i in subjects)>3000
    subjects=sorted(subjects,key=lambda i:(int(centers[i][1]/ch),centers[i][0]))
    items=[]
    for i,component in enumerate(subjects):
        sx,sy,sw,sh,area=map(int,stats[component]);margin=2
        assert sx>0 and sy>0 and sx+sw<aw and sy+sh<ah,(action,i,'subject touches full sheet edge')
        sx=max(0,sx-margin);sy=max(0,sy-margin);sw=min(aw-sx,sw+2*margin);sh=min(ah-sy,sh+2*margin)
        p=rawcells/f'{i:03}.png'
        run(['-i',str(raw),'-vf',f'crop={sw}:{sh}:{sx}:{sy}','-frames:v','1',str(p)])
        a=np.array(Image.open(p).getchannel('A'));yy,xx=np.where(a>20)
        assert len(xx)>300,(action,i,'empty',len(xx))
        full=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1))
        bottom=yy.max();feet=a[max(0,bottom-12):bottom+1,:]>40
        fy,fx=np.where(feet);footx=float(np.median(fx))
        items.append({'path':p,'visible_bbox':list(full),'bbox':full,'footx':footx,'bottom':int(bottom),'source_rect':[sx,sy,sw,sh]})
    # One scale per action preserves limb proportions and pose amplitude.
    scale=460/statistics.median(q['visible_bbox'][3]-q['visible_bbox'][1] for q in items)
    scale=min(scale,min((WIDTH/2-8)/max(q['footx']-q['bbox'][0],q['bbox'][2]-q['footx']) for q in items))
    # The corrected think sheet's tenth source pose lifts the opposite hand.
    # Reuse its third pose on the way down so the same arm completes the clip.
    source_order=list(range(len(items)))
    if action=='think':source_order[9]=2
    frames=[]
    for i,source_index in enumerate(source_order):
        item=items[source_index]
        x,y,x2,y2=item['bbox'];w,h=x2-x,y2-y
        sw,sh=round(w*scale),round(h*scale)
        px=round(WIDTH/2-(item['footx']-x)*scale);py=round(HEIGHT-28-(item['bottom']-y)*scale)
        assert px>=0 and py>=0 and px+sw<=WIDTH and py+sh<=HEIGHT,(action,i,'anchor needs more margin',px,py,sw,sh)
        p=out/f'{i:03}.png'
        filt=f'crop={w}:{h}:{x}:{y},scale={sw}:{sh}:flags=lanczos,pad={WIDTH}:{HEIGHT}:{px}:{py}:color=0x00000000,format=rgba'
        run(['-i',str(item['path']),'-vf',filt,'-frames:v','1',str(p)])
        frames.append({'index':i,'source_index':source_index,'file':str(p.relative_to(LIB)),'sha256':sha(p),'atlas_rect':[i%columns*WIDTH,i//columns*HEIGHT,WIDTH,HEIGHT],'source_rect':item['source_rect'],'source_visible_bbox':item['visible_bbox'],'anchor':[WIDTH//2,HEIGHT-28]})
    atlas=LIB/'atlases'/f'{action}.png'
    inputs=[]
    for f in frames:inputs+=['-i',str(LIB/f['file'])]
    layout='|'.join(f'{i%columns*WIDTH}_{i//columns*HEIGHT}' for i in range(len(frames)))
    run([*inputs,'-filter_complex',f'xstack=inputs={len(frames)}:layout={layout}:fill=0x00000000,format=rgba','-frames:v','1',str(atlas)])
    # Preserve an exact first-frame seam for replay. Frame 11 is the return pose;
    # loop playback returns to frame 0, never an interpolated image warp.
    preview=LIB/'previews'/f'{action}.webp'
    run(['-framerate','10','-i',str(out/'%03d.png'),'-c:v','libwebp_anim','-lossless','0','-quality','80','-loop','0',str(preview)])
    manifest_path=LIB/'manifest.json'
    manifest=json.loads(manifest_path.read_text()) if manifest_path.exists() else {'schema':'shikanon-sprite-library/v1','version':1,'character':'shikanon','style':'children-colored-pencil','source_image':'../shikanon-儿童手绘-v1.png','source_sha256':sha(LIB.parent/'shikanon-儿童手绘-v1.png'),'frame_size':[WIDTH,HEIGHT],'anchor':[WIDTH//2,HEIGHT-28],'generator':'built-in image_gen','actions':{}}
    manifest['source_image']='reference.png'
    manifest['actions'][action]={'name':action,'fps':10,'loop':True,'frame_count':len(frames),'columns':columns,'rows':rows,'atlas':str(atlas.relative_to(LIB)),'atlas_size':[WIDTH*columns,HEIGHT*rows],'atlas_sha256':sha(atlas),'generated_atlas':str(raw.relative_to(LIB)),'generated_atlas_sha256':sha(raw),'prompt':f'prompts/{action}.txt' if action!='think' else 'prompts/think-final.txt','preview':str(preview.relative_to(LIB)),'frames':frames,'generation_output_path':str(source),'identity_reference':'reference.png','alpha_background':True,'assembly_note':'Source pose 9 replaced with source pose 2 for same-hand retraction; no warped or invented frames.' if action=='think' else 'Complete generated poses extracted by connected alpha components and aligned at feet.'}
    for entry in manifest['actions'].values():entry['identity_reference']='reference.png'
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    shutil.rmtree(rawcells)
    sync=B/'assets/author-animation';sync.mkdir(exist_ok=True)
    shutil.copytree(LIB,sync,dirs_exist_ok=True)
    print(json.dumps({'action':action,'frames':len(frames),'unique_frames':len({f['sha256'] for f in frames}),'raw_size':[aw,ah],'cache':str(LIB),'video_copy':str(sync)},ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action');p.add_argument('source',type=Path);p.add_argument('--columns',type=int,default=4);p.add_argument('--rows',type=int,default=3);a=p.parse_args();register(a.action,a.source,a.columns,a.rows)
