"""Build the hand-drawn composition plus a word-triggered, frame-indexed plan."""
import base64,json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
from html import escape
from visuals import artwork,INSIGHTS
from author_motion import actor_clips,sample_actor
BASE=Path(__file__).resolve().parent;D=json.loads((BASE/'timeline.json').read_text())
def norm(t):return ''.join(re.findall(r'[\u4e00-\u9fff]',t))
def cue_time(s,cue):
    source=norm(s['text']);wanted=norm(cue);assert wanted in source,(s['id'],cue)
    i=source.index(wanted);return s['words'][i]['start']
def beat_duration(el):
    labels=len(el.findall('.//text'));paths=[p for p in el.findall('.//path') if 'draw' in p.attrib.get('class','').split()]
    appearance=max(.30,.38+.035*max(0,labels-1),.63+.018*min(8,max(0,len(paths)-1)))
    action=el.attrib.get('data-action','')
    spans={'hop':1.55,'ruler':.66+.018*max(0,len(el.findall('.//path'))-1),'left-to-center':1.75,'right-to-center':1.75,'cells':.54+.020*max(0,len(paths)-1),'sum':1.33,'underline':1.33,'relative':1.33,'celebrate':1.33,'question':1.33,'score-contrast':1.33,'bar':1.05,'samples':.60+.07*max(0,len(el.findall('.//circle'))-1),'pull-mean':1.85,'brake':1.95,'easy-down':1.692,'split-prob':1.23,'pull-positive':2.15,'push-negative':2.15,'zoom-local':1.28,'teach':1.70,'tokens':.60+.10*max(0,labels-1),'soften':1.23,'qr':.60,'resources':.60}
    return max(appearance,spans.get(action,0))
scenes=[];plans=[]
for si,s in enumerate(D['scenes']):
    svg=ET.fromstring('<svg>'+artwork(s['kind'])+'</svg>');beats=[]
    for bi,el in enumerate(svg.findall('g')):
        if el.attrib.get('class')!='beat':continue
        cue=el.attrib['data-cue'];eid=f'{s["id"]}-b{bi:02}';el.set('id',eid)
        t=max(s['start']+.3,cue_time(s,cue)-.08)
        finish=min(s['end'],t+beat_duration(el))
        beats.append({'id':eid,'cue':cue,'start':round(t,5),'end':round(finish,5),'action':el.attrib.get('data-action',''),'frame_start':math.floor(t*D['fps']),'frame_end':math.ceil(finish*D['fps'])})
    if s['kind']=='curves':
        # A real marker follows the mathematically generated squared-error curve.
        svg.append(ET.fromstring('<circle id="curve-marker" cx="435" cy="740" r="13" fill="#ED826A" stroke="#46392F" stroke-width="3"/>'))
    if s['kind']=='huber':svg.append(ET.fromstring('<circle id="huber-marker" cx="435" cy="740" r="13" fill="#73A6A3" stroke="#46392F" stroke-width="3"/>'))
    actors=[]
    for beat_el in svg.findall('g'):
        if beat_el.attrib.get('class')!='beat':continue
        beat_plan=next(b for b in beats if b['id']==beat_el.attrib['id'])
        for actor in beat_el.iter('g'):
            if 'author-character' not in actor.attrib.get('class','').split():continue
            ai=len(actors);aid=f'{s["id"]}-author-{ai:02}'
            actor.set('id',aid)
            viewport=actor.find('svg');viewport.set('id',aid+'-viewport')
            atlas=viewport.find('use');atlas.set('id',aid+'-atlas')
            clips=actor_clips(s,beats,ai,beat_plan['start']+.10)
            atlas.set('href','#sprite-atlas-'+clips[0]['action'])
            actors.append({'id':aid,'beat_id':beat_plan['id'],'start':clips[0]['start'],'end':s['end'],'clips':clips,'origin':[float(actor.attrib['data-origin-x']),float(actor.attrib['data-origin-y'])]})
    content=''.join(ET.tostring(x,encoding='unicode') for x in svg)
    takeaway,detail=INSIGHTS[s['kind']];chapter=next(c for c in D['chapters'] if c['id']==s['chapter']);chapter_label="开源学习项目" if s["kind"]=="follow" else chapter["title"]
    scenes.append(f'<section id="{s["id"]}" class="scene" data-layout-allow-overflow="paper-slide-transition"><div class="paper-stripes" data-layout-ignore></div><div class="scene-content"><div class="eyebrow"><b>{si+1:02} / {len(D["scenes"])}</b><span>{escape(chapter_label)}</span></div><h1>{escape(s["title"])}</h1><div class="visual"><svg viewBox="0 0 910 980" xmlns="http://www.w3.org/2000/svg">{content}</svg></div><div class="takeaway"><strong>{escape(takeaway)}</strong><span>{escape(detail)}</span></div></div></section>')
    marker_motion=[]
    if s['kind'] in ('curves','huber'):
        cue='均方误差' if s['kind']=='curves' else '大误差改成直线'
        st=next(b['start'] for b in beats if b['cue']==cue)+.55;en=max(st+.1,min(s['end']-.30,st+3.4))
        marker_motion=[{'id':'curve-marker' if s['kind']=='curves' else 'huber-marker','start':st,'end':en,'frame_start':math.floor(st*30),'frame_end':math.ceil(en*30),'action':'formula-marker'}]
    plans.append({'id':s['id'],'chapter':s['chapter'],'title':s['title'],'kind':s['kind'],'text':s['text'],'start':s['start'],'end':s['end'],'frame_start':math.floor(s['start']*30),'frame_end':math.ceil(s['end']*30)-1,'beats':beats,'marker_motion':marker_motion,'actors':actors,'purpose':takeaway})
D['author_motion']=[a for p in plans for a in p['actors']];D['author_library']='assets/author-animation/manifest.json';D['storyboard']=plans;(BASE/'timeline-data.js').write_text('window.LOSS_DATA='+json.dumps(D,ensure_ascii=False,separators=(',',':'))+';\n')
(BASE/'storyboard.json').write_text(json.dumps({'fps':30,'duration':D['duration'],'frame_count':round(D['duration']*30),'interpolation':'GSAP paused timeline; t = frame / 30. Pen draw power2.out, author sprite selection discrete 20 fps; immutable closed-smile face; explicit head and foot joints, semantic movement power2.inOut, chapter progress linear.','chapters':D['chapters'],'scenes':plans},ensure_ascii=False,indent=2))
progress='<div class="top-progress"><div class="chapter-rail">'+''.join(f'<div class="chapter-segment" style="flex:{c["share"]}"><div id="chapter-fill-{i}" class="chapter-fill"></div><span class="chapter-label">{escape(["为什么 30%","演化 50%","前沿 20%"][i])}</span></div>' for i,c in enumerate(D['chapters']))+'</div><div class="section-rail">'+''.join(f'<div class="section-segment" style="flex:{s["end"]-s["start"]}"><div id="section-fill-{i}" class="section-fill"></div></div>' for i,s in enumerate(D['scenes']))+'</div>'+''.join(f'<div id="current-{i}" class="current-section">当前小节 <b>{i+1:02} · {escape(s["title"])}</b></div>' for i,s in enumerate(D['scenes']))+'</div>'
captions='<div class="captions">'+''.join(f'<div id="cap-{i}" class="caption"><span>{escape(c["text"])}</span></div>' for i,c in enumerate(D['captions']))+'</div>'
manifest=json.loads((BASE/'assets/author-animation/manifest.json').read_text())
assert set(manifest['actions'])=={'talk','point-right','think','celebrate','wave','teach-pointer','think-question','step'}
images=[]
for action,entry in manifest['actions'].items():
    data=base64.b64encode((BASE/'assets/author-animation'/entry['atlas']).read_bytes()).decode('ascii')
    aw,ah=entry['atlas_size']
    images.append(f'<image id="sprite-atlas-{action}" href="data:image/png;base64,{data}" x="0" y="0" width="{aw}" height="{ah}"/>')
# Shared transparent atlases are decoded once and reused by all 27 actors.
character_definition='<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" aria-hidden="true" data-layout-ignore style="position:absolute"><defs>'+''.join(images)+'</defs></svg>'
body=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>损失函数 · 我的深度学习之路</title><link rel="stylesheet" href="style.css"></head><body><div id="main" data-composition-id="main" data-start="0" data-duration="{D['duration']}" data-width="1080" data-height="1920">{character_definition}<div class="paper-edge" data-layout-ignore></div>{''.join(scenes)}{progress}{captions}<footer><span>我的深度学习之路</span><span>你怎么扣分，模型就怎么学</span></footer><audio id="narration-audio" src="audio/narration.m4a" data-start="0" data-duration="{D['duration']}" data-track-index="1" data-volume="1"></audio><audio id="effects-audio" src="audio/effects.m4a" data-start="0" data-duration="{D['duration']}" data-track-index="2" data-volume="0.40"></audio></div><script src="assets/gsap.min.js"></script><script src="timeline-data.js"></script><script>
{(BASE/'animation.js').read_text()}
</script></body></html>'''
(BASE/'index.html').write_text(body)
rows=['# 分镜与逐帧规划','',f'30 fps，共 {round(D["duration"]*30):,} 帧。下表按实际语音词时间确定关键帧；`storyboard.json` 保存每个动作的开始 / 结束帧。`qa/frame-plan.jsonl` 为每一帧记录小节、字幕、已揭示图解、进行中动作的相位。人物共用同一闭嘴微笑底稿，图解动作由同一 GSAP 时间线插值；手势、头部、脚步与教棍按 20 fps 切换 PNG 帧；随机跳到任意帧都可重建画面。','', '| 小节 / 时间 | 教学目的 | 逐词触发的图解动作 |','| --- | --- | --- |']
for p in plans:rows.append(f'| {p["id"]} {p["title"]} / {p["start"]:.2f}–{p["end"]:.2f}s | {p["purpose"]} | '+ '；'.join(f'{b["cue"]}：第 {b["frame_start"]} 帧，{b["action"] or "描线揭示"}' for b in p['beats'])+' |')
rows.extend(['',f'技术：HTML / CSS + 原创 SVG + GSAP。作者以共用底稿修复过的透明序列帧呈现，箭头用逐笔描线，数据曲线由公式计算。相邻小节使用纸页横推，新大章使用圆形展开。顶部三段配额与 {len(D["scenes"])} 小节进度持续同步。',''])
(BASE/'storyboard.md').write_text('\n'.join(rows))
with (BASE/'qa/frame-plan.jsonl').open('w') as out:
    for f in range(round(D['duration']*30)):
        t=f/30;scene=next((s for s in reversed(plans) if s['start']<=t),plans[0]);cap=next((i for i,c in enumerate(D['captions']) if c['start']<=t<c['end']),None)
        revealed=[b['id'] for b in scene['beats'] if b['start']<=t];moving=[{'id':b['id'],'phase':round((t-b['start'])/(b['end']-b['start']),4)} for b in scene['beats']+scene['marker_motion'] if b['start']<=t<b['end']]
        out.write(json.dumps({'frame':f,'time':round(t,5),'scene':scene['id'],'caption':cap,'revealed':revealed,'actions':moving,'author_poses':[sample_actor(a,t) for a in scene['actors'] if a['start']<=t],'overall_progress':round(t/D['duration'],5)},ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({'scenes':len(plans),'explanation_beats':sum(len(p['beats']) for p in plans),'animated_authors':len(D['author_motion']),'sprite_actions':len(manifest['actions']),'frames':round(D['duration']*30)},ensure_ascii=False))
