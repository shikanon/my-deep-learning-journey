"""Check numerical explanations, pen paths and the actual encoded new motion."""
import hashlib
import json
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from runtime import BASE
import render
import motion

def main():
    samples=[motion.xor_values(i/30) for i in range(270)]
    first=samples[0]
    assert first['W']==[1,1] and first['b']==-.5
    assert [p['z'] for p in first['points']]==[-.5,.5,.5,1.5]
    assert [p['prediction'] for p in first['points']]==[0,1,1,1]
    for s in samples:
        assert s['errors']>=1
        for p in s['points']:
            expected=sum(w*x for w,x in zip(s['W'],p['x']))+s['b']
            assert math.isclose(p['z'],expected,abs_tol=1e-8)
        for x,y in motion.boundary_segment(s['W'],s['b']):
            assert abs(s['W'][0]*x+s['W'][1]*y+s['b'])<1e-8
    pen_count=0
    for kind in motion.FORMULAS:
        previous=-1
        for i in range(80):
            q=motion.writer_state(kind,i/30)
            assert q['visible_length']>=previous
            previous=q['visible_length']
            if q['segments']:assert math.dist(q['tip'],q['segments'][-1][1])<1e-8
            # Check the actual full character, including the source-frame
            # graphite-tip registration and rounded raster placement.
            x,y=q['origin']
            for a,b in q['segments']:
                for px,py in (a,b):assert 64<=x+px<=954 and 435<=y+py<=1138
            if q['opacity']>.01:
                assert math.dist(q['placed_tip'],q['tip_absolute'])<=math.sqrt(.5)
                image=motion.writer_image(q['frame_index']);box=image.getbbox()
                px,py=q['position'];left,top,right,bottom=box
                assert 64<=px+left and px+right<=985,(kind,i,q)
                assert 480<=py+top and py+bottom<1050,(kind,i,q)
            pen_count+=1
    public=BASE.parents[3]/'assets/手绘形象/抱大铅笔写字-v2'
    for p in (BASE/'assets/pencil-writer').rglob('*'):
        if p.is_file():
            source=public/p.relative_to(BASE/'assets/pencil-writer')
            assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest()
    for i,filename in enumerate(motion.WRITER['frames']):
        p=BASE/'assets/pencil-writer'/filename
        assert hashlib.sha256(p.read_bytes()).hexdigest()==motion.REGISTRATION['source_frame_sha256'][i]
        original=Image.open(p).convert('RGBA');anchor=motion.REGISTRATION['tip_anchors'][i]
        r,g,b,a=original.getpixel(tuple(anchor));assert a>=150 and max(r,g,b)<50
    video=BASE/'renders/activation-functions-v6.mp4'
    cap=cv2.VideoCapture(str(video));encoded=[]
    def actual(f):
        cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,bgr=cap.read();assert ok
        return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    for s in render.D['scenes']:
        if s['kind'] not in motion.FORMULAS:continue
        for dt in [.65,1.4,2.65]:
            f=round((s['start']+dt)*30)
            got=actual(f).astype(float);expected=np.asarray(render.frame_image(f),dtype=float)
            roi=(slice(480,940),slice(64,986))
            mae=float(np.abs(got[roi]-expected[roi]).mean())
            assert mae<9,(s['id'],f,mae)
            sample={'scene':s['id'],'frame':f,'phase':dt,'rgb_mae':mae}
            encoded.append(sample)
            if s['kind']=='xor' and dt==1.4:
                Image.fromarray(got.astype(np.uint8)).save(BASE/'qa/handwriting-encoded.jpg',quality=97)
    # Compare every selected sprite pose to the actual encoded frame, both
    # forward and reverse seeking. This is not a rig certification.
    source_sequence=[];seen=set()
    s=render.D['scenes'][1]
    for index in list(range(16))+list(reversed(range(16))):
        f=round((s['start']+.3+(index+.4)/motion.WRITER['fps'])*30)
        q=motion.writer_state(s['kind'],f/30-s['start'])
        assert q['frame_index']==index,(index,q['frame_index'])
        expected=np.asarray(render.frame_image(f),dtype=float);got=actual(f).astype(float)
        left,top=q['position'];width,height=motion.REGISTRATION['display_size']
        roi=(slice(top,top+height),slice(left,left+width))
        mae=float(np.abs(got[roi]-expected[roi]).mean());assert mae<9,(index,mae)
        source_sequence.append({'source_index':index,'encoded_frame':f,'rgb_mae':mae,'tip_error_px':math.dist(q['placed_tip'],q['tip_absolute'])})
        seen.add(index)
    assert seen==set(range(16))
    s=render.D['scenes'][1];values=[];frames=[]
    for dt in [.25,1.4,3.2,5.9]:
        t=s['beats'][3]['start']+dt;f=round(t*30)
        arr=actual(f);values.append(motion.xor_values(f/30-s['beats'][3]['start']))
        frames.append(arr)
    delta=float(np.abs(frames[0][614:1078,90:928].astype(float)-frames[2][614:1078,90:928]).mean())
    assert delta>2
    Image.fromarray(frames[2]).save(BASE/'qa/xor-parameters-encoded.jpg',quality=97)
    # Compare settled and entering non-board regions, excluding the author and progress bars.
    outer=[]
    for s in render.D['scenes']:
        a=actual(round((s['start']+.3)*30)).astype(float)
        b=actual(round((s['start']+(3.2 if s['kind']=='hook' else 1.2))*30)).astype(float)
        left=550 if s['actor']=='doctor-pointer' else 375
        diff=float(np.abs(a[1202:1518,left:954]-b[1202:1518,left:954]).mean())
        assert diff>.25,(s['id'],diff)
        outer.append({'scene':s['id'],'knowledge_card_motion_rgb_mae':diff})
    cap.release()
    result={
        'status':'passed','video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
        'xor_math_samples':len(samples),'minimum_wrong_points':min(s['errors'] for s in samples),
        'unique_W':len({tuple(s['W']) for s in samples}),'unique_b':len({s['b'] for s in samples}),
        'pen_path_samples':pen_count,'pen_tip_matches_stroke_endpoint':True,
        'formulas_written':len(motion.FORMULAS),
        'formula_scene_count':len(motion.FORMULAS),'intro_has_formula':False,
        'writer_asset_copies_identical':True,
        'writer':{'source_archive_sha256':motion.REGISTRATION['source_archive_sha256'],
                  'source_frames_unchanged':True,'frames':16,'fps':8,'display_size':motion.REGISTRATION['display_size'],
                  'maximum_tip_registration_error_px':max(x['tip_error_px'] for x in source_sequence),
                  'encoded_source_frame_selection':source_sequence,'rigged_motion_certified':False},
        'actual_encoded_handwriting_samples':encoded,
        'actual_encoded_xor_parameter_states':values,'xor_motion_rgb_mae':delta,
        'actual_encoded_knowledge_card_motion':outer,
        'audio_source_sha256':hashlib.sha256((BASE/'audio/narration.m4a').read_bytes()).hexdigest()
    }
    (BASE/'qa/motion-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','formulas_written','pen_path_samples','xor_math_samples','xor_motion_rgb_mae']}))

if __name__=='__main__':main()
