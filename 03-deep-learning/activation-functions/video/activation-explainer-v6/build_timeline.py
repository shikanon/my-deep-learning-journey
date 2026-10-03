#!/usr/bin/env python3
"""Align every visual cue to actual Seed word times; preserve raw subtitles."""
import difflib
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from runtime import BASE, ffmpeg, ffprobe

def han(text):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', text))

def speech_key(text):
    """Keep English pronunciation in alignment rather than discarding it."""
    return ''.join(re.findall(r'[\u4e00-\u9fffA-Za-z0-9]', text)).lower()

def speech_units(text, syllables, english_weight=1.5):
    words = re.findall(r'[A-Za-z]+', text)
    unknown = [w for w in words if w.lower() not in syllables]
    if unknown:
        raise ValueError(f'Add explicit timing units for English words: {unknown}')
    # Technical English needs more articulation time than a Chinese syllable.
    return len(han(text)) + english_weight*sum(syllables[w.lower()] for w in words)

def probe(path):
    return json.loads(subprocess.check_output([ffprobe(), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], text=True))

def run(*args):
    subprocess.run([ffmpeg(), '-hide_banner', '-loglevel', 'error', '-y', *map(str, args)], check=True)

def align(expected, observed, times):
    matcher = difflib.SequenceMatcher(None, expected, observed, autojunk=False)
    indices, diff = [None] * len(expected), []
    for op, i, j, k, l in matcher.get_opcodes():
        if op == 'equal':
            indices[i:j] = range(k, l)
        else:
            diff.append({'operation': op, 'expected': expected[i:j], 'observed': observed[k:l]})
    # Do not conceal omitted words or invent timestamps.
    if any(v is None for v in indices):
        raise ValueError(f'Speech differs from the script; review before rendering: {diff}')
    return [times[i] for i in indices], {'matching_ratio': matcher.ratio(), 'differences': diff}

def timestamp(t):
    m = round(t * 1000)
    return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'

def main():
    N = json.loads((BASE / 'narration.json').read_text())
    requests = json.loads((BASE / 'audio/generation-requests.json').read_text())
    scenes, captions, batches, clips = [], [], [], []
    offset = 0
    for request in requests:
        batch = request['batch']
        paths = list((BASE / 'audio/seed' / batch).glob('*/manifest.json'))
        complete = [(p, json.loads(p.read_text())) for p in paths if json.loads(p.read_text()).get('status') == 'complete']
        if len(complete) != 1:
            raise ValueError(f'Expected exactly one complete generation for {batch}, got {len(complete)}')
        path, job = complete[0]
        raw = BASE/request['edited_audio_file'] if request.get('edited_audio_file') else path.parent / Path(job['audio_path']).name
        raw_duration = float(probe(raw)['format']['duration'])
        batch_scenes = [s.copy() for s in N['scenes'] if s['id'] in request['scene_ids']]
        text = ''.join(s['text'] for s in batch_scenes)
        expected = speech_key(text)
        units = speech_units(text, N['english_syllables'])
        duration = units / N['target_cpm'] * 60
        speed = raw_duration / duration
        if not 0.8 <= speed <= 1.3:
            raise ValueError(f'Excessive voice speed calibration: {batch} {speed}')
        subtitle_path = BASE/request['edited_subtitle_file'] if request.get('edited_subtitle_file') else path.parent / Path(job['subtitle_json_path']).name
        data = json.loads(subtitle_path.read_text())
        observed, times = '', []
        for sentence in data['sentences']:
            for word in sentence['words']:
                chars = speech_key(word['text'])
                st, en = word['start_time'] / 1000, word['end_time'] / 1000
                if en > raw_duration + .1:
                    raise ValueError('Provider subtitle clock is longer than the returned actual audio; review scaling.')
                for j, char in enumerate(chars):
                    observed += char
                    times.append((offset + (st + (en-st)*j/len(chars))/speed, offset + (st + (en-st)*(j+1)/len(chars))/speed))
        aligned, report = align(expected, observed, times)
        wav = BASE / 'audio' / f'{batch}-calibrated.wav'
        run('-i', raw, '-af', f'atempo={speed:.12f},apad=whole_dur={duration:.12f}', '-t', f'{duration:.12f}', '-ar', '48000', '-ac', '1', wav)
        clips.append(wav)
        pos = 0
        for scene in batch_scenes:
            words = []
            for c in scene['text']:
                if speech_key(c):
                    st, en = aligned[pos]
                    pos += 1
                    words.append({'text': c, 'start': st, 'end': en})
                else:
                    words[-1]['text'] += c
            scene.update(words=words, speech_start=words[0]['start'], speech_end=words[-1]['end'])
            normalized = speech_key(scene['text'])
            scene['beats'] = []
            for index, cue in enumerate(scene['cues']):
                position = normalized.index(speech_key(cue))
                st = max(0, words[position]['start'] - .06)
                scene['beats'].append({'cue': cue, 'start': st, 'end': st + .8, 'frame_start': math.floor(st*N['fps']), 'frame_end': math.ceil((st+.8)*N['fps'])})
            protected = []
            for term in N['display_terms']:
                protected.extend((m.start(), m.end()) for m in re.finditer(re.escape(speech_key(term)), normalized))
            for match in re.finditer(r'[A-Za-z]+', scene['text']):
                start = len(speech_key(scene['text'][:match.start()]))
                protected.append((start, start + len(match.group())))
            bucket = []
            for i, word in enumerate(words):
                bucket.append(word)
                txt = ''.join(w['text'] for w in bucket)
                protected_boundary = any(a <= i < b - 1 for a,b in protected)
                sentence_boundary = txt.endswith(('。','？','！','；','，','：')) and len(speech_key(txt)) >= 5
                if not protected_boundary and (sentence_boundary or len(speech_key(txt)) >= 17 or i == len(words)-1):
                    display = txt
                    for old, new in sorted(N['display_terms'].items(), key=lambda x:-len(x[0])):
                        display = display.replace(old, new)
                    captions.append({'scene':scene['id'],'start':bucket[0]['start'],'end':bucket[-1]['end']+.09,'spoken_text':txt,'text':display})
                    bucket = []
            scenes.append(scene)
        batches.append({'batch':batch,'request_id':job['request_id'],'model':job['model'],'raw_audio_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'raw_duration':raw_duration,'original_provider_duration':job.get('original_duration'),'subtitle_clock':'Measured English splice map and actual source word times' if request.get('edited_subtitle_file') else 'returned Chinese and English words, already matching the returned audio duration','audio_edit_provenance':request.get('audio_edit_provenance'),'target_duration':duration,'atempo':speed,'han_characters':len(han(text)),'equivalent_speech_units':units,**report})
        offset += duration
    full = math.ceil((offset+2)*N['fps'])/N['fps']
    silence = BASE / 'audio/end.wav'
    run('-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t',f'{full-offset:.12f}',silence)
    clips.append(silence)
    concat = BASE / 'audio/concat.txt'
    concat.write_text('\n'.join("file '"+p.name.replace("'","'\\''")+"'" for p in clips)+'\n')
    run('-f','concat','-safe','0','-i',concat,'-af','loudnorm=I=-16:TP=-1.5:LRA=8','-ar','48000','-ac','1',BASE/'audio/narration.wav')
    run('-i',BASE/'audio/narration.wav','-c:a','aac','-b:a','160k',BASE/'audio/narration.m4a')
    for i,s in enumerate(scenes):
        s['start'] = 0 if i == 0 else max(scenes[i-1]['speech_end'],s['speech_start']-.16)
        s['end'] = full
    for i,s in enumerate(scenes[:-1]):
        s['end'] = scenes[i+1]['start']
    for i,c in enumerate(captions[:-1]):
        c['end'] = min(c['end'],captions[i+1]['start'])
    chapters=[]
    knowledge_chars=sum(speech_units(s['text'],N['english_syllables']) for s in scenes if not s.get('exclude_from_content_share'))
    for ch in N['chapters']:
        ss=[s for s in scenes if s['chapter']==ch['id']]
        chars=sum(speech_units(s['text'],N['english_syllables']) for s in ss)
        chapters.append({**ch,'start':ss[0]['start'],'end':ss[-1]['end'],'equivalent_speech_units':chars,'share':chars/knowledge_chars})
    D={**{k:N[k] for k in ['title','project_name','project_url','width','height','fps','display_terms','research_checked','revision_date','history_checked']},'duration':full,'speech_duration':offset,'target_cpm':N['target_cpm'],'chapters':chapters,'scenes':scenes,'captions':captions,'audio_audit':batches}
    (BASE/'timeline.json').write_text(json.dumps(D,ensure_ascii=False,indent=2)+'\n')
    (BASE/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{timestamp(c["start"])} --> {timestamp(c["end"])}\n{c["text"]}' for i,c in enumerate(captions))+'\n')
    meta=[';FFMETADATA1','title=激活函数 · 我的深度学习之路']
    for s in scenes:
        meta.extend(['[CHAPTER]','TIMEBASE=1/1000',f'START={round(s["start"]*1000)}',f'END={round(s["end"]*1000)}','title='+s['title'].replace('\n',' ')])
    (BASE/'chapters.ffmetadata').write_text('\n'.join(meta)+'\n')
    plan={'fps':N['fps'],'frame_count':round(full*N['fps']),'interpolation':'deterministic Pillow drawing; t=frame/fps; smoothstep cue reveals; author assets sampled at manifest fps on engineering time (V3 20 fps; doctoral pointer 8 fps); no random or wall-clock animation','scenes':[{k:s[k] for k in ['id','title','kind','start','end','beats','actor','insight','source']} for s in scenes]}
    (BASE/'storyboard.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    rows=['# 激活函数 V6：口播与分镜','', '下表时间来自实际 Seed Audio 逐词时间，英文也参与对齐。ReLU、GELU、SiLU 和 SwiGLU 的口播使用英文全称，字幕显示标准缩写；Sigmoid、Swish 和 beta 按英文发音。Tanh 等使用准确的中文概念名称。原始服务字幕独立保留，不再使用中文谐音发音稿。','', '| 小节 / 秒 | 口播 | 动态图解 / 目的 | 作者动作 |','| --- | --- | --- | --- |']
    for s in scenes:
        rows.append(f'| {s["id"]} · {s["start"]:.2f}–{s["end"]:.2f} | {s["text"]} | {s["kind"]}：{s["insight"].replace(chr(10)," / ")}；关键词 {"、".join(s["cues"])} | {s["actor"]} |')
    (BASE/'storyboard.md').write_text('\n'.join(rows)+'\n')
    review={'total_han':sum(len(han(s['text'])) for s in scenes),'equivalent_speech_units':sum(speech_units(s['text'],N['english_syllables']) for s in scenes),'english_syllables':N['english_syllables'],'narration_seconds_including_pauses':offset,'measured_han_per_minute':sum(len(han(s['text'])) for s in scenes)/offset*60,'equivalent_units_per_minute':sum(speech_units(s['text'],N['english_syllables']) for s in scenes)/offset*60,'shares':chapters,'batches':batches,'raw_subtitles_preserved':True,'last_spoken_end':scenes[-1]['speech_end'],'last_frame_time':full,'end_hold_seconds':full-scenes[-1]['speech_end']}
    (BASE/'qa/audio-alignment.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'duration':full,'frames':round(full*N['fps']),'scenes':len(scenes),'captions':len(captions),'han_per_minute':review['measured_han_per_minute'],'equivalent_units_per_minute':review['equivalent_units_per_minute'],'alignment_ratios':[r['matching_ratio'] for r in batches]},ensure_ascii=False))

if __name__=='__main__':
    main()
