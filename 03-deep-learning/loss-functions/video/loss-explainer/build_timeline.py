"""Assemble scene-level speech; preserve actual provider word times (seconds)."""
import argparse, html, json, re, subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent
P=argparse.ArgumentParser(); P.add_argument('--ffmpeg',default='ffmpeg'); P.add_argument('--ffprobe',default='ffprobe'); P.add_argument('--speed',type=float,default=1.20); args=P.parse_args()
N=json.loads((BASE/'narration.json').read_text()); clips=[]; captions=[]; words_all=[]; scenes=[]
def run(cmd): return subprocess.check_output(cmd,text=True).strip()
def duration(path): return float(run([args.ffprobe,'-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)]))
def fmt(t):
    v=round(t*1000); return f'{v//3600000:02}:{v//60000%60:02}:{v//1000%60:02},{v%1000:03}'
def add_caps(words,scene_id):
    # Phrase chunks follow provider word boundaries. At most 19 Chinese characters.
    chunk=[]
    for wi,w in enumerate(words):
        chunk.append(w)
        txt=''.join(x['text'] for x in chunk)
        pause=wi+1<len(words) and words[wi+1]['start']-w['end']>.20
        if len(txt)>=15 or ((pause or txt.endswith(('。','？','！','；','，','：'))) and len(txt)>=6):
            captions.append({'scene':scene_id,'start':chunk[0]['start'],'end':chunk[-1]['end']+.055,'text':txt.replace('滴皮欧','DPO').replace('维斯波','VESPO')}); chunk=[]
    if chunk:
        captions.append({'scene':scene_id,'start':chunk[0]['start'],'end':chunk[-1]['end']+.075,'text':''.join(x['text'] for x in chunk).replace('滴皮欧','DPO').replace('维斯波','VESPO')})
cursor=.35
silence=BASE/'audio/gap.wav'
subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','0.35','-y',str(silence)],check=True)
clips.append(silence)
for s in N['scenes']:
    raw=BASE/'audio/edge'/f"{s['id']}.mp3"
    wav=BASE/'audio/edge'/f"{s['id']}.wav"
    subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-i',str(raw),'-af',f'atempo={args.speed}','-ar','48000','-ac','1','-y',str(wav)],check=True)
    length=duration(wav)
    data=json.loads((raw.with_suffix('.json')).read_text())
    words=[dict(w,start=round(cursor+w['start']/args.speed,4),end=round(cursor+w['end']/args.speed,4)) for w in data['words']]
    # Restore original punctuation after the provider's punctuation-free word tokens.
    source=s['text'].replace('Huber','胡伯')
    norm=lambda t:re.sub(r'[^\w\u4e00-\u9fff]','',t)
    assert norm(source)==norm(''.join(w['text'] for w in words)), f"Transcript mismatch: {s['id']}"
    offsets={}; count=0
    for ch in source:
        if norm(ch):count+=1
        else:offsets[count]=offsets.get(count,'')+ch
    count=0
    for w in words:
        count+=len(norm(w['text'])); w['text']+=offsets.get(count,'')
    scenes.append(dict(s,start=round(cursor-.10,4),speech_start=round(cursor,4),speech_end=round(cursor+length,4),duration=round(length+.35,4),words=words))
    words_all.extend(words); add_caps(words,s['id'])
    clips.extend([wav,silence]); cursor+=length+.35
# Last frame remains readable for 1.4s after voice completion.
end_pad=BASE/'audio/end-pad.wav'
subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','1.4','-y',str(end_pad)],check=True)
clips.append(end_pad)
concat=BASE/'audio/concat.txt'; concat.write_text('\n'.join("file '"+str(x).replace("'","'\\''")+"'" for x in clips))
subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-af','loudnorm=I=-16:TP=-1.5:LRA=8','-c:a','aac','-b:a','192k','-y',str(BASE/'audio/narration.m4a')],check=True)
full_duration=duration(BASE/'audio/narration.m4a')
for i,s in enumerate(scenes): s['end']=scenes[i+1]['start'] if i+1<len(scenes) else full_duration
for i,c in enumerate(captions):
    if i+1<len(captions): c['end']=min(c['end'],captions[i+1]['start'])
    c['end']=max(c['end'],c['start']+.06)
result={'title':N['title'],'duration':round(full_duration,4),'width':1080,'height':1920,'fps':30,'speech_speed':args.speed,'voice':'Microsoft zh-CN-YunxiNeural (synthetic)','scenes':scenes,'captions':captions}
(BASE/'timeline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(BASE/'captions.srt').write_text('\n\n'.join(f"{i+1}\n{fmt(c['start'])} --> {fmt(c['end'])}\n{c['text']}" for i,c in enumerate(captions))+'\n')
print(json.dumps({'duration':full_duration,'scenes':len(scenes),'captions':len(captions),'words':len(words_all)},ensure_ascii=False))
