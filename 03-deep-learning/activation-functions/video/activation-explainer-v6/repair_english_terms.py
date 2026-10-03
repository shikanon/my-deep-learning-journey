#!/usr/bin/env python3
"""Replace English term spans with checked Seed English clips, preserving Chinese."""
import hashlib
import json
import re
import subprocess
import wave
from pathlib import Path
import numpy as np
from runtime import BASE, ffmpeg


def key(text):
    return ''.join(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]',text)).lower()


def pcm(path):
    data=subprocess.check_output([ffmpeg(),'-v','error','-i',str(path),'-ac','1','-ar','48000','-f','f32le','pipe:1'])
    return np.frombuffer(data,dtype=np.float32).copy()


def complete(batch):
    items=[p for p in (BASE/'audio/seed'/batch).glob('*/manifest.json') if json.loads(p.read_text()).get('status')=='complete']
    assert len(items)==1,batch
    return items[0].parent,json.loads(items[0].read_text())


def main():
    source,job=complete('evolution-b-v4')
    proof=json.loads((BASE/'qa/english-dictionary-asr.json').read_text())
    assert proof['status']=='passed'
    dictionary_audio=BASE/proof['audio_file']
    speech=pcm(source/'audio.wav');english=pcm(dictionary_audio);rate=48000
    assert proof['audio_sha256']==hashlib.sha256(dictionary_audio.read_bytes()).hexdigest()
    original=json.loads((source/'subtitle.json').read_text())
    words=[w for sentence in original['sentences'] for w in sentence['words']]
    original_key=''.join(key(w['text']) for w in words)
    spans=[];position=0
    for i,w in enumerate(words):
        length=len(key(w['text']));spans.append((position,position+length,i));position+=length
    terms={key(p['match_source']):p for p in proof['phrases']}
    pattern=re.compile('|'.join(sorted(map(re.escape,terms),key=len,reverse=True)))
    edits=[]
    for match in pattern.finditer(original_key):
        a=next(i for st,en,i in spans if st<=match.start()<en)
        b=next(i for st,en,i in spans if st<match.end()<=en)
        assert spans[a][0]==match.start() and spans[b][1]==match.end()
        phrase=terms[match.group()]
        old_start=words[a]['start_time']/1000;old_end=words[b]['end_time']/1000
        en_start=max(0,phrase['start']-.025);en_end=phrase['end']+.025
        clip=english[round(en_start*rate):round(en_end*rate)].copy()
        old=speech[round(old_start*rate):round(old_end*rate)]
        old_rms=float(np.sqrt(np.mean(old**2)));new_rms=float(np.sqrt(np.mean(clip**2)))
        gain=float(np.clip(old_rms/max(new_rms,1e-7),.7,1.4));clip*=gain
        fade=min(round(.008*rate),len(clip)//4)
        clip[:fade]*=np.linspace(0,1,fade);clip[-fade:]*=np.linspace(1,0,fade)
        edits.append({'a':a,'b':b,'term':phrase['expected'],'old_start':old_start,'old_end':old_end,
                      'english_start':en_start,'english_end':en_end,'clip':clip,'words':phrase['words'],
                      'gain':gain,'new_duration':len(clip)/rate})
    assert len(edits)==8
    parts=[];cursor=0;delta=0;new_words=[];edits_by_a={e['a']:e for e in edits};skipped=set()
    for edit in edits:
        start=round(edit['old_start']*rate);end=round(edit['old_end']*rate)
        assert start>=cursor
        prior=speech[cursor:start].copy()
        if len(prior)>=384:prior[-384:]*=np.linspace(1,0,384)
        parts.extend([prior,edit['clip']]);cursor=end
        edit['new_start']=edit['old_start']+delta
        edit['delta_after']=delta+edit['new_duration']-(end-start)/rate
        delta=edit['delta_after'];skipped.update(range(edit['a'],edit['b']+1))
    parts.append(speech[cursor:]);audio=np.concatenate(parts)
    def shift(t):
        change=0
        for e in edits:
            if t+1e-8>=e['old_end']:change=e['delta_after']
        return t+change
    for i,w in enumerate(words):
        if i in edits_by_a:
            e=edits_by_a[i]
            for ew in e['words']:
                if not key(ew['text']):continue
                new_words.append({'text':ew['text'],'start_time':round((e['new_start']+ew['start']-e['english_start'])*1000),
                                  'end_time':round((e['new_start']+ew['end']-e['english_start'])*1000)})
        if i in skipped:continue
        new_words.append({**w,'start_time':round(shift(w['start_time']/1000)*1000),
                          'end_time':round(shift(w['end_time']/1000)*1000)})
    narration=json.loads((BASE/'narration.json').read_text())
    target=''.join(key(s['text']) for s in narration['scenes'] if s['id'] in ['s11','s12','s13','s14'])
    assert ''.join(key(w['text']) for w in new_words)==target
    output=BASE/'audio/evolution-b-repaired.wav'
    with wave.open(str(output),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        wav.writeframes((np.clip(audio,-1,1)*32767).astype('<i2').tobytes())
    subtitle=BASE/'audio/evolution-b-repaired-subtitle.json'
    subtitle.write_text(json.dumps({'source':'Seed original Chinese word times plus independent ASR checked English phrase word times; transformed through measured PCM edits',
                                   'sentences':[{'text':''.join(w['text'] for w in new_words),'words':new_words}]},ensure_ascii=False,indent=2)+'\n')
    for e in edits:
        e.pop('clip');e.pop('words')
    audit={'original_request':job['request_id'],'english_provenance':'qa/english-dictionary-asr.json',
           'original_sha256':hashlib.sha256((source/'audio.wav').read_bytes()).hexdigest(),
           'english_sha256':proof['audio_sha256'],'edited_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
           'duration':len(audio)/rate,'edits':edits,'english_clip_fade_ms':8,
           'method':'Preserve original Chinese PCM; replace only eight English spans with checked same-reference-voice English terms; remap actual source word clocks.'}
    (BASE/'audio/term-repair.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
    requests=json.loads((BASE/'audio/generation-requests.json').read_text())
    for request in requests:
        if request['batch']=='evolution-b-v4':
            request.update(edited_audio_file=str(output.relative_to(BASE)),edited_subtitle_file=str(subtitle.relative_to(BASE)),audio_edit_provenance='audio/term-repair.json')
    (BASE/'audio/generation-requests.json').write_text(json.dumps(requests,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'terms_repaired':len(edits),'duration':len(audio)/rate},ensure_ascii=False))


if __name__=='__main__':
    main()
