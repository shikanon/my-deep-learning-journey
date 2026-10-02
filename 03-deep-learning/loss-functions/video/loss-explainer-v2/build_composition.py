"""Build the hand-drawn composition plus a word-triggered, frame-indexed plan."""
import json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
from html import escape
from visuals import artwork,INSIGHTS
BASE=Path(__file__).resolve().parent;D=json.loads((BASE/'timeline.json').read_text())
def norm(t):return ''.join(re.findall(r'[\u4e00-\u9fff]',t))
def cue_time(s,cue):
    source=norm(s['text']);wanted=norm(cue);assert wanted in source,(s['id'],cue)
    i=source.index(wanted);return s['words'][i]['start']
scenes=[];plans=[]
for si,s in enumerate(D['scenes']):
    svg=ET.fromstring('<svg>'+artwork(s['kind'])+'</svg>');beats=[]
    for bi,el in enumerate(svg.findall('g')):
        if el.attrib.get('class')!='beat':continue
        cue=el.attrib['data-cue'];eid=f'{s["id"]}-b{bi:02}';el.set('id',eid)
        t=max(s['start']+.3,cue_time(s,cue)-.08)
        beats.append({'id':eid,'cue':cue,'start':round(t,5),'end':round(min(s['end'],t+3.5),5),'action':el.attrib.get('data-action',''),'frame_start':math.floor(t*D['fps']),'frame_end':math.ceil(min(s['end'],t+3.5)*D['fps'])})
    if s['kind']=='curves':
        # A real marker follows the mathematically generated squared-error curve.
        svg.append(ET.fromstring('<circle id="curve-marker" cx="435" cy="740" r="13" fill="#ED826A" stroke="#46392F" stroke-width="3"/>'))
    if s['kind']=='huber':svg.append(ET.fromstring('<circle id="huber-marker" cx="435" cy="740" r="13" fill="#73A6A3" stroke="#46392F" stroke-width="3"/>'))
    content=''.join(ET.tostring(x,encoding='unicode') for x in svg)
    takeaway,detail=INSIGHTS[s['kind']];chapter=next(c for c in D['chapters'] if c['id']==s['chapter'])
    scenes.append(f'<section id="{s["id"]}" class="scene"><div class="paper-stripes" data-layout-ignore></div><div class="scene-content"><div class="eyebrow"><b>{si+1:02} / 16</b><span>{escape(chapter["title"])}</span></div><h1>{escape(s["title"])}</h1><div class="visual"><svg viewBox="0 0 910 980" xmlns="http://www.w3.org/2000/svg">{content}</svg></div><div class="takeaway"><strong>{escape(takeaway)}</strong><span>{escape(detail)}</span></div></div></section>')
    plans.append({'id':s['id'],'chapter':s['chapter'],'title':s['title'],'kind':s['kind'],'text':s['text'],'start':s['start'],'end':s['end'],'frame_start':math.floor(s['start']*30),'frame_end':math.ceil(s['end']*30)-1,'beats':beats,'purpose':takeaway})
D['storyboard']=plans;(BASE/'timeline-data.js').write_text('window.LOSS_DATA='+json.dumps(D,ensure_ascii=False,separators=(',',':'))+';\n')
(BASE/'storyboard.json').write_text(json.dumps({'fps':30,'duration':D['duration'],'frame_count':round(D['duration']*30),'interpolation':'GSAP paused timeline; t = frame / 30. Pen draw power2.out, actor movement power2.inOut, chapter progress linear.','chapters':D['chapters'],'scenes':plans},ensure_ascii=False,indent=2))
progress='<div class="top-progress"><div class="chapter-rail">'+''.join(f'<div class="chapter-segment" style="flex:{c["share"]}"><div id="chapter-fill-{i}" class="chapter-fill"></div><span class="chapter-label">{escape(["为什么 30%","演化 50%","前沿 20%"][i])}</span></div>' for i,c in enumerate(D['chapters']))+'</div><div class="section-rail">'+''.join(f'<div class="section-segment" style="flex:{s["end"]-s["start"]}"><div id="section-fill-{i}" class="section-fill"></div></div>' for i,s in enumerate(D['scenes']))+'</div>'+''.join(f'<div id="current-{i}" class="current-section">当前小节 <b>{i+1:02} · {escape(s["title"])}</b></div>' for i,s in enumerate(D['scenes']))+'</div>'
captions='<div class="captions">'+''.join(f'<div id="cap-{i}" class="caption"><span>{escape(c["text"])}</span></div>' for i,c in enumerate(D['captions']))+'</div>'
body=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>损失函数 · 手绘小课堂</title><link rel="stylesheet" href="style.css"></head><body><div id="main" data-composition-id="main" data-start="0" data-duration="{D['duration']}" data-width="1080" data-height="1920"><div class="paper-edge" data-layout-ignore></div>{''.join(scenes)}{progress}{captions}<footer><span>豆豆的损失函数小课堂</span><span>你怎么扣分，模型就怎么学</span></footer><audio id="narration-audio" src="audio/narration.m4a" data-start="0" data-duration="{D['duration']}" data-track-index="1" data-volume="1"></audio><audio id="effects-audio" src="audio/effects.m4a" data-start="0" data-duration="{D['duration']}" data-track-index="2" data-volume="0.40"></audio></div><script src="assets/gsap.min.js"></script><script src="timeline-data.js"></script><script>
{(BASE/'animation.js').read_text()}
</script></body></html>'''
(BASE/'index.html').write_text(body)
rows=['# 分镜与逐帧规划','',f'30 fps，共 {round(D["duration"]*30):,} 帧。下表按实际语音词时间确定关键帧；`storyboard.json` 保存每个动作的开始 / 结束帧。`qa/frame-plan.jsonl` 为每一帧记录小节、字幕、已揭示图解、进行中动作的相位。静态轮廓固定，动作由同一 GSAP 时间线插值；随机跳到任意帧都可重建画面。','', '| 小节 / 时间 | 教学目的 | 逐词触发的图解动作 |','| --- | --- | --- |']
for p in plans:rows.append(f'| {p["id"]} {p["title"]} / {p["start"]:.2f}–{p["end"]:.2f}s | {p["purpose"]} | '+ '；'.join(f'{b["cue"]}：第 {b["frame_start"]} 帧，{b["action"] or "描线揭示"}' for b in p['beats'])+' |')
rows.extend(['','技术：HTML / CSS + 原创 SVG + GSAP。角色与箭头用逐笔描线，数据曲线由公式计算。相邻小节使用纸页横推，新大章使用圆形展开。顶部三段配额与 16 小节进度持续同步。',''])
(BASE/'storyboard.md').write_text('\n'.join(rows))
with (BASE/'qa/frame-plan.jsonl').open('w') as out:
    for f in range(round(D['duration']*30)):
        t=f/30;scene=next((s for s in reversed(plans) if s['start']<=t),plans[0]);cap=next((i for i,c in enumerate(D['captions']) if c['start']<=t<c['end']),None)
        revealed=[b['id'] for b in scene['beats'] if b['start']<=t];moving=[{'id':b['id'],'phase':round((t-b['start'])/(b['end']-b['start']),4)} for b in scene['beats'] if b['start']<=t<b['end']]
        out.write(json.dumps({'frame':f,'time':round(t,5),'scene':scene['id'],'caption':cap,'revealed':revealed,'actions':moving,'overall_progress':round(t/D['duration'],5)},ensure_ascii=False,separators=(',',':'))+'\n')
print(json.dumps({'scenes':len(plans),'explanation_beats':sum(len(p['beats']) for p in plans),'frames':round(D['duration']*30)},ensure_ascii=False))
