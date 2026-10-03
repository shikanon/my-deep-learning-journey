"""Verify narration-led opening and one handwriting pass in the encoded export."""
import hashlib
import json
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw
from runtime import BASE, font
import motion
import render


def main():
    hook,xor=render.D['scenes'][:2]
    fps=render.FPS
    start=next(w['start'] for w in hook['words'] if w['text']=='如')
    assert hook['kind']=='hook' and xor['kind']=='xor'
    assert 'hook' not in motion.FORMULAS
    assert motion.hook_state(hook,.7)['network']==0
    assert motion.hook_state(hook,.7)['points']==0
    assert render.actor_geometry(hook,.7)==((309,500),(400,600))
    assert motion.hook_state(hook,2.7)['network']==1
    assert motion.hook_state(hook,2.7)['depth']==1
    assert motion.hook_state(hook,5.3)['depth']==128
    assert motion.hook_state(hook,7.8)['points']==1
    # Check every intro frame and the full first explanation for extra entries.
    for f in range(math.ceil(hook['end']*fps)):
        assert motion.writer_state('hook',f/fps) is None
    visible=[]
    for f in range(math.ceil(xor['start']*fps),math.ceil(xor['end']*fps)):
        q=motion.writer_state('xor',f/fps-xor['start'])
        visible.append(q['opacity']>.01)
    entries=sum(v and (i==0 or not visible[i-1]) for i,v in enumerate(visible))
    assert entries==1
    video=BASE/'renders/activation-functions-v6.mp4'
    cap=cv2.VideoCapture(str(video))
    times=[.7,1.05,1.4,1.98,2.7,4.8,5.3,7.8,12.4,13.3,14.3,15.25,16.4]
    samples=[];images={}
    for t in times:
        f=round(t*fps);cap.set(cv2.CAP_PROP_POS_FRAMES,f)
        ok,bgr=cap.read();assert ok
        got=cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
        expected=np.asarray(render.frame_image(f),dtype=float)
        roi=(slice(470,1550),slice(64,986))
        mae=float(np.abs(got[roi].astype(float)-expected[roi]).mean())
        assert mae<9,(t,mae)
        samples.append({'time':f/fps,'frame':f,'board_and_actor_rgb_mae':mae})
        images[t]=Image.fromarray(got)
    cap.release()
    contact=Image.new('RGB',(1080,1004),render.PAPER)
    for i,t in enumerate([.7,1.4,2.7,4.8,7.8,12.4,14.3,16.4]):
        tile=images[t].resize((270,480),Image.Resampling.LANCZOS)
        x=i%4*270;y=i//4*502
        contact.paste(tile,(x,y))
        ImageDraw.Draw(contact).text((x+8,y+482),f'{t:g} s',font=font(17),fill=render.INK)
    contact.save(BASE/'qa/opening-encoded-contact.jpg',quality=97)
    images[.7].save(BASE/'qa/opening-thinker-encoded.jpg',quality=97)
    result={'status':'passed','video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
            'intro_has_formula':False,'opening_formula_writing_passes':entries,
            'narration_order_verified':True,
            'narration_cues':{'question_end':1.037169789516127,'network_start':start,
                              'depth_increase_start':hook['beats'][1]['start'],
                              'four_points_start':hook['beats'][2]['start'],
                              'first_handwriting_start':xor['start']+.3},
            'opening_actor':'one cached think-question actor, moves from board to presenter lane',
            'encoded_samples':samples,'comparison':'actual encoded board and actor versus deterministic source',
            'visual_review_contact':'qa/opening-encoded-contact.jpg'}
    (BASE/'qa/opening-story.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
