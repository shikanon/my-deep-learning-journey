#!/usr/bin/env python3
"""Audit final encoded media, exact data, random frame reconstruction and author motion."""
import hashlib
import json
import math
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from runtime import BASE,ffmpeg,ffprobe
import render

def contrast(a,b):
    def lum(c):
        rgb=[int(c[i:i+2],16)/255 for i in (1,3,5)]
        rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
        return .2126*rgb[0]+.7152*rgb[1]+.0722*rgb[2]
    x,y=sorted([lum(a),lum(b)])
    return (y+.05)/(x+.05)

def main():
    D=render.D;video=BASE/'renders/activation-functions-v6.mp4'
    meta=json.loads(subprocess.check_output([ffprobe(),'-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(video)],text=True))
    (BASE/'qa/ffprobe-final.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
    v=next(x for x in meta['streams'] if x['codec_type']=='video');a=next(x for x in meta['streams'] if x['codec_type']=='audio')
    assert (v['codec_name'],v['width'],v['height'],v['pix_fmt'],v['avg_frame_rate'])==('h264',1080,1920,'yuv420p','30/1')
    assert a['codec_name']=='aac' and int(v['nb_frames'])==round(D['duration']*D['fps'])
    assert abs(float(meta['format']['duration'])-D['duration'])<1/D['fps']
    assert len(meta['chapters'])==len(D['scenes'])
    for c,s in zip(meta['chapters'],D['scenes']):
        assert abs(float(c['start_time'])-s['start'])<.002 and abs(float(c['end_time'])-s['end'])<.002
    with (BASE/'qa/decode-final.log').open('w') as log:
        subprocess.run([ffmpeg(),'-hide_banner','-v','error','-i',str(video),'-f','null','-'],stdout=log,stderr=log,check=True)
    assert not (BASE/'qa/decode-final.log').read_text().strip()
    # Validate source formulas against the exact four cases and branch arithmetic.
    xor=[max(0,x+y)-2*max(0,x+y-1) for x,y in [(0,0),(0,1),(1,0),(1,1)]]
    assert xor==[0,1,1,0]
    assert math.isclose(4*render.silu(2),7.046376623823059)
    # Seek order must not affect the frame or the actor phase.
    checks=[0,17,243,1031,2550,4391,5777,round(D['duration']*D['fps'])-4]
    initial={f:hashlib.sha256(render.frame_image(f).tobytes()).hexdigest() for f in checks}
    for f in reversed(checks):assert initial[f]==hashlib.sha256(render.frame_image(f).tobytes()).hexdigest()
    # All cue boundaries and caption midpoints: evaluate real text boxes, not only static previews.
    sample_frames=set()
    for s in D['scenes']:
        for t in [s['start'],s['end']-.04,*[b['start'] for b in s['beats']],*[b['end'] for b in s['beats']]]:
            for delta in [-1,0,1]:sample_frames.add(max(0,min(round(D['duration']*D['fps'])-1,round(t*D['fps'])+delta)))
    for c in D['captions']:sample_frames.add(round((c['start']+c['end'])/2*D['fps']))
    render.LOG_TEXT=True;render.TEXT_LOG.clear();render.background.cache_clear()
    for f in sorted(sample_frames):render.frame_image(f)
    violations=[x for x in render.TEXT_LOG if x['text'] and (x['box'][0]<60 or x['box'][2]>985 or x['box'][1]<65 or x['box'][3]>1855)]
    render.LOG_TEXT=False
    assert not violations,violations
    text_report={'sampled_frames':len(sample_frames),'text_boxes':len(render.TEXT_LOG),'violations':violations,'all_caption_midpoints_checked':True,'contrast':{'ink_on_paper':contrast(render.INK,render.PAPER),'teal_on_green':contrast(render.TEAL,'#e1eee5'),'coral_on_paper':contrast(render.CORAL,render.PAPER)}}
    assert min(text_report['contrast'].values())>=4.5
    (BASE/'qa/text-layout-full.json').write_text(json.dumps(text_report,ensure_ascii=False,indent=2)+'\n')
    # Test the complete pointer sweep against actual glyph boxes in every teaching scene.
    pointer_samples=0
    for s in D['scenes']:
        if s['actor']!='doctor-pointer':continue
        for phase in range(len(render.B['frames'])):
            f=round((s['start']+.12+(phase+.35)/render.B['fps'])*D['fps'])
            render.LOG_TEXT=True;render.TEXT_LOG.clear();render.background.cache_clear()
            render.frame_image(f)
            actor_index=render.state(f)[3]
            assert actor_index==phase
            alpha=np.array(render.sprite('doctor-pointer',phase))[:,:,3]
            for label in render.TEXT_LOG:
                x0,y0,x1,y1=map(int,label['box'])
                x0,x1=max(0,x0-22),min(alpha.shape[1],x1-22)
                y0,y1=max(0,y0-1040),min(alpha.shape[0],y1-1040)
                if x0<x1 and y0<y1:
                    assert not np.any(alpha[y0:y1,x0:x1]>20),(s['id'],phase,label)
            pointer_samples+=1
    render.LOG_TEXT=False
    text_report['doctor_pointer_sweep_samples']=pointer_samples
    text_report['doctor_pointer_glyph_intersections']=0
    (BASE/'qa/text-layout-full.json').write_text(json.dumps(text_report,ensure_ascii=False,indent=2)+'\n')
    cap=cv2.VideoCapture(str(video))
    def actual(f):
        cap.set(cv2.CAP_PROP_POS_FRAMES,f);ok,bgr=cap.read();assert ok,f
        return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    stills=[]
    for s in D['scenes']:
        f=round(min(s['end']-.1,s['beats'][-1]['start']+1.1)*D['fps'])
        arr=actual(f);im=Image.fromarray(arr)
        im.save(BASE/'qa'/f'{s["id"]}-encoded.jpg',quality=96)
        small=im.resize((270,480),Image.Resampling.LANCZOS);stills.append(small)
    contact=Image.new('RGB',(1080,480*math.ceil(len(stills)/4)),render.PAPER)
    for i,im in enumerate(stills):contact.paste(im,((i%4)*270,(i//4)*480))
    contact.save(BASE/'qa/encoded-contact.jpg',quality=96)
    used={s['actor']:s for s in reversed(D['scenes'])}
    stability=[];motion=[]
    for action,s in used.items():
        frames=[]
        for dt in [.27,.42,.59,.77,.94,1.12]:
            f=round((s['start']+dt)*D['fps']);got=actual(f).astype(float);expected=np.array(render.frame_image(f),dtype=float)
            # Even origin and dimensions avoid YUV420 chroma-origin artefacts.
            if action=='doctor-pointer':
                mouth=(slice(1280,1320),slice(190,246));body=(slice(1340,1390),slice(154,238))
            else:
                (px,py),(aw,ah)=render.actor_geometry(s,f/D['fps'])
                def actor_roi(x0,y0,x1,y1):
                    # Follow the actual actor while the intro character moves.
                    left=2*round((px+x0*aw/290)/2);right=2*round((px+x1*aw/290)/2)
                    top=2*round((py+y0*ah/435)/2);bottom=2*round((py+y1*ah/435)/2)
                    return slice(top,bottom),slice(left,right)
                mouth=actor_roi(102,203,160,241);body=actor_roi(102,277,160,317)
            mouth_mae=float(np.abs(got[mouth]-expected[mouth]).mean())
            body_mae=float(np.abs(got[body]-expected[body]).mean())
            assert mouth_mae<9 and body_mae<9,(action,f,mouth_mae,body_mae)
            stability.append({'action':action,'frame':f,'mouth_rgb_mae':mouth_mae,'body_rgb_mae':body_mae,'source_frame':render.state(f)[3]})
            if action=='doctor-pointer':frames.append(got[1130:1506,100:506])
            else:
                crop=Image.fromarray(got[py:py+ah,px:px+aw].astype(np.uint8))
                frames.append(np.asarray(crop.resize((290,435),Image.Resampling.LANCZOS),dtype=float))
        delta=float(np.abs(frames[0]-frames[3]).mean())
        assert delta>.25,(action,delta)
        motion.append({'action':action,'encoded_pose_change_mae':delta})
        if action=='doctor-pointer':
            entry=render.B
            files=[BASE/'assets/doctor-pointer'/f for f in entry['frames']]
            hashes=[hashlib.sha256(f.read_bytes()).hexdigest() for f in files]
            assert hashes==list(reversed(hashes)) and hashes[0]==hashes[-1]
        else:
            entry=render.M['actions'][action]
            assert all(f['anchor']==render.M['anchor'] and not f['mouth_animation'] and f['head_layer_sha256']==render.M['rig']['head_sha256'] for f in entry['frames'])
    # Check final EOF frame and the no-QR ending; also retain the actual opening as a poster.
    final=actual(int(v['nb_frames'])-1);Image.fromarray(final).save(BASE/'qa/last-frame.jpg',quality=97)
    Image.fromarray(actual(180)).save(BASE/'assets/poster.jpg',quality=97)
    detector=cv2.QRCodeDetector();qr_sampled=0
    for t in np.arange(D['scenes'][-1]['start'],D['duration']-.034,.1):
        f=round(t*D['fps']);arr=actual(f);detected,_,_=detector.detectAndDecode(arr)
        assert not detected,(f,detected);qr_sampled+=1
    detected,_,_=detector.detectAndDecode(final);assert not detected
    cap.release()
    # Encoded reference comparisons and atlas metadata complement visual review, not replace it.
    result={'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'bytes':video.stat().st_size,'duration':float(meta['format']['duration']),'dimensions':[v['width'],v['height']],'fps':v['avg_frame_rate'],'codecs':[v['codec_name'],a['codec_name']],'frames':int(v['nb_frames']),'chapters':len(meta['chapters']),'complete_decode_errors':0,'random_seek_frame_reconstruction':True,'xor_arithmetic':xor,'layout':text_report,'encoded_author_samples':stability,'encoded_actions':motion,'v3_anchors_and_closed_head_verified':True,'doctor_pointer':{'source':'assets/手绘形象/博士服教棍-v1','frames':len(render.B['frames']),'fps':render.B['fps'],'first_last_identical':True,'reverse_identical':True,'closed_smile_visual_review':True,'rigged_motion_certified':False,'notes':'Original hand-drawn poses preserve minor face, outline and fabric variation; checked exact encoded pose selection and a dedicated pointer lane.'},'ending_qr_samples':qr_sampled,'last_frame_no_qr':True,'browser_playthrough':'pending separate real browser evidence'}
    (BASE/'qa/media-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['sha256','bytes','duration','frames','chapters','complete_decode_errors','ending_qr_samples']},ensure_ascii=False))

if __name__=='__main__':main()
