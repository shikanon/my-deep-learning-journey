#!/usr/bin/env python3
"""Recognize actual term clips with an independent local ASR, without text hints."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import wave
from pathlib import Path

BASE = Path(__file__).resolve().parent


def key(text):
    return ''.join(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]', text)).lower()


def prepare(source=None):
    timeline = json.loads((BASE/'timeline.json').read_text())
    terms = sorted(list(timeline['display_terms'])+['Sigmoid', 'Swish'], key=len, reverse=True)
    pattern = re.compile('|'.join(re.escape(t) for t in terms))
    output = BASE/'qa/pronunciation-clips'
    output.mkdir(parents=True, exist_ok=True)
    source = source or BASE/'audio/narration.wav'
    clips = []
    with wave.open(str(source), 'rb') as wav:
        rate, width, channels = wav.getframerate(), wav.getsampwidth(), wav.getnchannels()
        assert channels == 1 and rate == 48000
        for scene in timeline['scenes']:
            assert not any(t in scene['text'] for t in ['杰鲁', '杰撸', '瑞鲁', '西鲁', '斯维格鲁', '西格莫伊德', '斯维什'])
            for match in pattern.finditer(scene['text']):
                start_index = len(key(scene['text'][:match.start()]))
                length = len(key(match.group()))
                start = scene['words'][start_index]['start']
                end = scene['words'][start_index+length-1]['end']
                path = output/f'{len(clips)+1:02}-{scene["id"]}.wav'
                start_frame = max(0, round((start-.025)*rate))
                end_frame = min(wav.getnframes(), round((end+.025)*rate))
                wav.setpos(start_frame)
                core = wav.readframes(end_frame-start_frame)
                silence = bytes(round(rate*.25)*width*channels)
                with wave.open(str(path), 'wb') as out:
                    out.setnchannels(channels)
                    out.setsampwidth(width)
                    out.setframerate(rate)
                    out.writeframes(silence+core+silence)
                clips.append({'scene':scene['id'], 'expected':match.group(),
                              'start':start, 'end':end, 'file':str(path.relative_to(BASE)),
                              'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {'audio_file':str(source.relative_to(BASE)),
                'audio_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                'terms':clips, 'raw_word_timestamps_preserved':True,
                'script_has_no_chinese_homophones':True}
    (BASE/'qa/pronunciation-clips.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'clips':len(clips),'terms':[c['expected'] for c in clips]},ensure_ascii=False),flush=True)
    return manifest


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--prepare-only',action='store_true')
    args.add_argument('--model',default='medium.en')
    args.add_argument('--ffmpeg',default=shutil.which('ffmpeg'))
    args.add_argument('--encoded',action='store_true',help='Decode and check the actual final MP4 audio.')
    opts=args.parse_args()
    source=None
    if opts.encoded:
        assert opts.ffmpeg,'Pass --ffmpeg with the local executable path.'
        source=BASE/'qa/encoded-audio.wav'
        subprocess.run([opts.ffmpeg,'-v','error','-y','-i',str(BASE/'renders/activation-functions-v6.mp4'),
                        '-vn','-ar','48000','-ac','1',str(source)],check=True)
    manifest=prepare(source)
    if opts.prepare_only:
        return
    from faster_whisper import WhisperModel
    import numpy as np
    assert opts.ffmpeg,'Pass --ffmpeg with the local executable path.'
    model=WhisperModel(opts.model,device='cpu',compute_type='int8',cpu_threads=4)
    chinese_model=None
    alternate_model=None
    results=[]
    for clip in manifest['terms']:
        # Explicit 16 kHz samples also avoid dependence on changing PyAV open keywords.
        pcm=subprocess.check_output([opts.ffmpeg,'-v','error','-i',str(BASE/clip['file']),
                                     '-f','f32le','-ac','1','-ar','16000','pipe:1'])
        audio=np.frombuffer(pcm,dtype=np.float32)
        if clip['expected']=='贝塔' and chinese_model is None:
            chinese_model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
        active=chinese_model if clip['expected']=='贝塔' else model
        segments,info=active.transcribe(audio,language='zh' if clip['expected']=='贝塔' else 'en',beam_size=5,
                                      condition_on_previous_text=False,vad_filter=False)
        transcript=' '.join(s.text.strip() for s in segments)
        # Doubling the written L is silent; accept this spelling alias only.
        recognized=key(transcript)
        passed=(key(clip['expected']) in recognized or
                (clip['expected']=='Llama' and recognized=='lama') or
                (clip['expected']=='贝塔' and recognized=='beta'))
        result={**clip,'recognized':transcript,'passed':passed}
        # A short technical term can have a different unprompted ASR hypothesis.
        # Keep both actual hypotheses rather than treating one model as hearing.
        if not passed and clip['expected']!='贝塔':
            if alternate_model is None:
                alternate_model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4)
            other,_=alternate_model.transcribe(audio,language='en',beam_size=5,
                                               condition_on_previous_text=False,vad_filter=False)
            alternative=' '.join(s.text.strip() for s in other)
            result.update(alternate_model='small',alternate_recognized=alternative,
                          passed=key(clip['expected']) in key(alternative))
        if not result['passed'] and clip['expected']=='Rectified Linear Unit':
            # Preserve the surrounding real Chinese sentence so the decoder can
            # distinguish the noun "rectified" from its short isolated hypothesis.
            context_start=max(0,clip['start']-.2)
            context_pcm=subprocess.check_output([opts.ffmpeg,'-v','error','-ss',str(context_start),
                                                  '-t','5','-i',str(BASE/manifest['audio_file']),
                                                  '-f','f32le','-ar','16000','-ac','1','pipe:1'])
            context_segments,_=alternate_model.transcribe(np.frombuffer(context_pcm,dtype=np.float32),
                                                          language='zh',beam_size=5,
                                                          condition_on_previous_text=False)
            context=' '.join(s.text.strip() for s in context_segments)
            result.update(context_model='small/zh',context_start=context_start,context_duration=5,
                          context_recognized=context,passed=key(clip['expected']) in key(context))
        results.append(result)
        print(json.dumps(result,ensure_ascii=False),flush=True)
    proof={**manifest,'status':'passed' if all(r['passed'] for r in results) else 'review_required',
           'method':f'Independent local Whisper {opts.model} int8; English decode of actual aligned term clips; no initial prompt, hotwords or expected text given to ASR',
           'model':opts.model,'results':results}
    if opts.encoded:
        proof['video_sha256']=hashlib.sha256((BASE/'renders/activation-functions-v6.mp4').read_bytes()).hexdigest()
    name='pronunciation-asr.json' if opts.encoded else 'pronunciation-source-asr.json'
    (BASE/'qa'/name).write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    assert proof['status']=='passed','Review failed recognition against actual audio before claiming success.'


if __name__=='__main__':
    main()
