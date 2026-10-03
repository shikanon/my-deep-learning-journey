#!/usr/bin/env python3
"""Assemble only clear same-voice English spans; keep every source clock."""
import hashlib
import json
import re
import wave
import numpy as np
from runtime import BASE
from repair_english_terms import pcm, complete, key


def main():
    a,_=complete('evolution-a-v4');d,_=complete('english-terms-v4');sp,_=complete('spelled-terms-v4')
    source_words=[w for s in json.loads((a/'subtitle.json').read_text())['sentences'] for w in s['words']]
    sigmoid=next(w for w in source_words if key(w['text'])=='sigmoid')
    english=json.loads((BASE/'qa/english-dictionary-transcript.json').read_text())
    words=[w for s in english['segments'] for w in s['words']]
    linear=next(i for i,w in enumerate(words) if key(w['text'])=='linear')
    assert key(words[linear+1]['text'])=='unit'
    beta=next(w for w in words if key(w['text'])=='beta')
    llama=next(w for w in words if key(w['text']) in ['lama','llama'])
    gated=next(i for i,w in enumerate(words) if key(w['text'])=='gated')
    assert [key(w['text']) for w in words[gated:gated+3]]==['gated','linear','unit']
    old_dir=next((BASE/'audio/seed/evolution-b').glob('*/audio.wav')).parent
    old_words=[w for s in json.loads((old_dir/'subtitle.json').read_text())['sentences'] for w in s['words']]
    beta_index=next(i for i,w in enumerate(old_words) if w['text']=='贝')
    assert old_words[beta_index+1]['text']=='塔'
    spelling=json.loads((sp/'subtitle.json').read_text())
    spelling_words=[w for s in spelling['sentences'] for w in s['words'] if key(w['text'])]
    joined=''.join(key(w['text']) for w in spelling_words)
    assert joined=='swishswiglu',joined
    groups=[];pos=0
    for term in ['swish','swiglu']:
        selected=[];length=0
        while length<len(term):
            w=spelling_words[pos];selected.append(w);length+=len(key(w['text']));pos+=1
        assert ''.join(key(w['text']) for w in selected)==term
        groups.append((selected[0]['start_time']/1000,selected[-1]['end_time']/1000))
    rate=48000;samples={str(p):pcm(p) for p in [a/'audio.wav',d/'audio.wav',sp/'audio.wav',old_dir/'audio.wav']}
    specifications=[
        ('Sigmoid','Sigmoid',[(a/'audio.wav',sigmoid['start_time']/1000,sigmoid['end_time']/1000-.08,'Sigmoid')]),
        ('Sigmoid Linear Unit','Sigmoid Linear Unit',[(a/'audio.wav',sigmoid['start_time']/1000,sigmoid['end_time']/1000-.08,'Sigmoid'),(d/'audio.wav',words[linear]['start'],words[linear+1]['end'],'Linear Unit')]),
        ('Swish','S W I S H',[(sp/'audio.wav',*groups[0],'S W I S H')]),
        ('beta','贝塔',[(old_dir/'audio.wav',old_words[beta_index]['start_time']/1000,old_words[beta_index+1]['end_time']/1000,'贝塔')]),
        ('Swish Gated Linear Unit','S W I S H Gated Linear Unit',[(sp/'audio.wav',*groups[0],'S W I S H'),(d/'audio.wav',words[gated]['start'],words[gated+2]['end'],'Gated Linear Unit')]),
        ('Llama','Llama',[(d/'audio.wav',llama['start'],llama['end'],'Llama')])]
    blocks=[];phrases=[];clock=0
    for source_term,expected,slices in specifications:
        silence=np.zeros(round(rate*.25),dtype=np.float32);blocks.append(silence);clock+=len(silence)/rate
        begin=clock;phrase_words=[];provenance=[]
        for j,(path,st,en,text) in enumerate(slices):
            if j:
                pause=np.zeros(round(rate*.035),dtype=np.float32);blocks.append(pause);clock+=len(pause)/rate
            st=max(0,st-.015);en+=.015
            clip=samples[str(path)][round(st*rate):round(en*rate)].copy()
            fade=min(288,len(clip)//4);clip[:fade]*=np.linspace(0,1,fade);clip[-fade:]*=np.linspace(1,0,fade)
            blocks.append(clip);end=clock+len(clip)/rate
            phrase_words.append({'text':text,'start':clock+.015,'end':end-.015})
            provenance.append({'source':str(path.relative_to(BASE)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'start':st,'end':en})
            clock=end
        phrases.append({'match_source':source_term,'expected':expected,'start':begin,'end':clock,'words':phrase_words,'sources':provenance})
    audio=np.concatenate(blocks);output=BASE/'audio/checked-english-terms.wav'
    with wave.open(str(output),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        wav.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
    manifest={'audio_file':str(output.relative_to(BASE)),'audio_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'status':'requires_independent_asr','phrases':phrases}
    (BASE/'qa/assembled-english-terms.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'phrases':len(phrases),'duration':len(audio)/rate},ensure_ascii=False))


if __name__=='__main__':main()
