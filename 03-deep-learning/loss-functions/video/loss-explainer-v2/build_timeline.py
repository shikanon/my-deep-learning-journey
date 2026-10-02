"""Calibrate Seed narration to 164 Han chars/min and align actual word evidence."""
import argparse,difflib,json,math,re,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--ffprobe',default='ffprobe');a=p.parse_args()
N=json.loads((BASE/'narration.json').read_text());CPM=N['target_cpm']
def han(t):return ''.join(re.findall(r'[\u4e00-\u9fff]',t))
def duration(p):return float(subprocess.check_output([a.ffprobe,'-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],text=True))
def ff(cmd):subprocess.run([a.ffmpeg,'-hide_banner','-loglevel','error',*cmd],check=True)
def zhnum(n):
    if n=='1805':return '一八零五'
    if n=='0':return '零'
    v=int(n);digits='零一二三四五六七八九'
    if v<10:return digits[v]
    if v<100:return (digits[v//10] if v//10>1 else '')+'十'+(digits[v%10] if v%10 else '')
    return ''.join(digits[int(c)] for c in n)
def asr_chars(asr):
    raw='';times=[]
    for s in asr['segments']:
        for w in s['words']:
            for j,c in enumerate(w['text']):
                raw+=c;times.append((w['start']+(w['end']-w['start'])*j/len(w['text']),w['start']+(w['end']-w['start'])*(j+1)/len(w['text'])))
    out='';ts=[]
    for m in re.finditer(r'\d+\s*%|\d+|.',raw):
        q=m.group();converted=('百分之'+zhnum(re.search(r'\d+',q)[0])) if '%' in q else zhnum(q) if q.isdigit() else han(q)
        if not converted:continue
        st,en=times[m.start()][0],times[m.end()-1][1]
        for j,c in enumerate(converted):out+=c;ts.append((st+(en-st)*j/len(converted),st+(en-st)*(j+1)/len(converted)))
    return out,ts
def aligned(expected,observed,times,mode):
    m=difflib.SequenceMatcher(None,expected,observed,autojunk=False);indices=[None]*len(expected);diff=[]
    for op,i,j,k,l in m.get_opcodes():
        if op=='equal':indices[i:j]=list(range(k,l))
        else:
            diff.append({'type':op,'expected':expected[i:j],'observed':observed[k:l],'time':times[min(k,len(times)-1)][0]})
            if j>i and l>k:indices[i:j]=[k+round(q*(l-k-1)/max(j-i-1,1)) for q in range(j-i)]
    assert m.ratio()>.94,(mode,m.ratio(),diff)
    known=[i for i,x in enumerate(indices) if x is not None];assert known
    for i,x in enumerate(indices):
        if x is None:
            left=max((k for k in known if k<i),default=known[0]);right=min((k for k in known if k>i),default=known[-1]);u=(i-left)/max(right-left,1)
            indices[i]=round(indices[left]+u*(indices[right]-indices[left]))
    return [times[i] for i in indices],{'source':mode,'matching_ratio':m.ratio(),'differences':diff}

sets=[('chapter-1',N['scenes'][:5]),('chapter-2a',N['scenes'][5:9]),('chapter-2b',N['scenes'][9:13]),('chapter-3',N['scenes'][13:])]
offset=0;scenes=[];caps=[];clips=[];audit=[];reports=[]
for name,ss in sets:
    manifests=[json.loads(p.read_text()) for p in (BASE/'audio/seed'/name).glob('*/manifest.json')]
    good=[m for m in manifests if m.get('status')=='complete'];assert len(good)==1,(name,len(good))
    job=good[0];raw=Path(job['audio_path']);chars=sum(len(han(s['text'])) for s in ss);target=chars/CPM*60
    rawdur=duration(raw);speed=rawdur/target;wav=BASE/'audio'/f'{name}-calibrated.wav'
    ff(['-y','-i',str(raw),'-af',f'atempo={speed:.12f},apad=whole_dur={target:.12f}', '-t',f'{target:.12f}','-ar','48000','-ac','1',str(wav)])
    clips.append(wav)
    expected=han(''.join(s['text'] for s in ss))
    if job.get('subtitle_json_path'):
        data=json.loads(Path(job['subtitle_json_path']).read_text());items=[w for s in data['sentences'] for w in s.get('words',[]) if han(w['text'])]
        observed='';wt=[]
        for w in items:
            txt=han(w['text']);st=w['start_time']/1000/speed;en=w['end_time']/1000/speed
            for j,c in enumerate(txt):observed+=c;wt.append((st+(en-st)*j/len(txt),st+(en-st)*(j+1)/len(txt)))
        times,report=aligned(expected,observed,wt,'Seed Audio returned subtitle')
    else:
        # This ASR was run on the provisional calibrated chapter-1 output.
        rawasr=json.loads((BASE/'audio'/f'{name}-asr.json').read_text());observed,wt=asr_chars(rawasr)
        provisional=rawasr['duration'];wt=[(st*target/provisional,en*target/provisional) for st,en in wt]
        times,report=aligned(expected,observed,wt,'Actual audio / faster-whisper-small')
    reports.append(dict(report,batch=name))
    pos=0
    for s in ss:
        charwords=[]
        for c in s['text']:
            if han(c):
                st,en=times[pos];pos+=1;charwords.append({'text':c,'start':offset+st,'end':offset+max(st+.025,en)})
            elif charwords:charwords[-1]['text']+=c
        st=charwords[0]['start'];en=charwords[-1]['end'];scene=dict(s,speech_start=st,speech_end=en,words=charwords)
        scenes.append(scene)
        bucket=[]
        for i,w in enumerate(charwords):
            bucket.append(w);t=''.join(x['text'] for x in bucket);pause=i+1<len(charwords) and charwords[i+1]['start']-w['end']>.30
            if len(han(t))>=14 or (len(han(t))>=5 and (t.endswith(('。','？','！','；','，','：')) or pause)):
                caps.append({'scene':s['id'],'start':bucket[0]['start'],'end':bucket[-1]['end']+.1,'text':t});bucket=[]
        if bucket:caps.append({'scene':s['id'],'start':bucket[0]['start'],'end':bucket[-1]['end']+.1,'text':''.join(x['text'] for x in bucket)})
    audit.append({'batch':name,'model':job['model'],'request_id':job['request_id'],'characters':chars,'raw_duration':rawdur,'target_duration':target,'atempo':speed,'measured_cpm':chars/duration(wav)*60,'subtitle_source':report['source']})
    offset+=target
# One second of readable conclusion follows the narration; speech track itself is 164 cpm.
pad=BASE/'audio/end.wav';ff(['-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','1',str(pad)]);clips.append(pad)
concat=BASE/'audio/concat.txt';concat.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in clips))
ff(['-y','-f','concat','-safe','0','-i',str(concat),'-af','loudnorm=I=-16:TP=-1.5:LRA=8','-c:a','aac','-b:a','192k',str(BASE/'audio/narration.m4a')])
full=math.ceil(duration(BASE/'audio/narration.m4a')*30)/30
for i,s in enumerate(scenes):
    s['start']=0 if i==0 else max(scenes[i-1]['speech_end'],s['speech_start']-.42)
    s['end']=full
for i,s in enumerate(scenes[:-1]):s['end']=scenes[i+1]['start']
for i,c in enumerate(caps):
    if i+1<len(caps):c['end']=min(c['end'],caps[i+1]['start'])
    c['end']=max(c['start']+.04,c['end'])
chapters=[]
for i,ch in enumerate(N['chapters']):
    matching=[s for s in scenes if s['chapter']==ch['id']];count=sum(len(han(s['text'])) for s in matching)
    chapters.append(dict(ch,start=matching[0]['start'],end=matching[-1]['end'],characters=count,share=count/sum(len(han(s['text'])) for s in scenes)))
out={'title':N['title'],'width':1080,'height':1920,'fps':30,'duration':full,'speech_duration':offset,'target_cpm':CPM,'voice':'Seed Audio 1.0','chapters':chapters,'scenes':scenes,'captions':caps,'audio_audit':audit}
(BASE/'timeline.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));(BASE/'timeline-data.js').write_text('window.LOSS_DATA='+json.dumps(out,ensure_ascii=False,separators=(',',':'))+';\n')
def fmt(t):
    v=round(t*1000);return f'{v//3600000:02}:{v//60000%60:02}:{v//1000%60:02},{v%1000:03}'
(BASE/'captions.srt').write_text('\n\n'.join(f'{i+1}\n{fmt(c["start"])} --> {fmt(c["end"])}\n{c["text"]}' for i,c in enumerate(caps))+'\n')
(BASE/'qa/alignment-review.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
(BASE/'qa/speech-rate.json').write_text(json.dumps({'definition':'汉字含读出的汉字数字，不计标点；整段配音含句间停顿，不含最后一秒留白','total_han':sum(len(han(s['text'])) for s in scenes),'narration_duration':offset,'measured_cpm':sum(len(han(s['text'])) for s in scenes)/offset*60,'batches':audit,'shares':[{'chapter':c['title'],'share':c['share']} for c in chapters]},ensure_ascii=False,indent=2))
print(json.dumps({'duration':full,'speech_duration':offset,'characters':sum(x['characters'] for x in audit),'scenes':len(scenes),'captions':len(caps),'alignment':[(x['batch'],x['matching_ratio']) for x in reports]},ensure_ascii=False))
