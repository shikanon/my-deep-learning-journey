/* Inspect actual rendered teaching states, including transitions and seek order. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.VIDEO_PLAYWRIGHT_MODULE||'playwright');
const sharp=require(process.env.VIDEO_SHARP_MODULE||'sharp');
const B=path.dirname(new URL(import.meta.url).pathname),D=JSON.parse(fs.readFileSync(path.join(B,'timeline.json'),'utf8'));
const browser=await chromium.launch({headless:true,executablePath:process.env.VIDEO_CHROME_PATH,args:['--disable-gpu']});
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
await page.goto('file://'+path.join(B,'index.html'),{waitUntil:'domcontentloaded'});
await page.evaluate(()=>document.fonts.ready);
const checks=[],composite=[],states=[];
for(let i=0;i<D.scenes.length;i++){
 const s=D.scenes[i],time=s.end-.12;
 await page.evaluate(t=>{window.__timelines.main.time(t,false)},time);
 const p=path.join(B,'qa',`source-${s.id}.png`);await page.screenshot({path:p});
 composite.push({input:await sharp(p).resize(270,480).png().toBuffer(),left:i%4*270,top:Math.floor(i/4)*480});
 for(const step of s.steps){
  for(const position of ['start','middle','end']){
   const t=step.start+(position==='start'?.01:position==='middle'?step.duration/2:step.duration+.01);
   if(t>=s.end)continue;
   await page.evaluate(t=>{window.__timelines.main.time(t,false)},t);
   const v=await page.evaluate(()=>{
    const root=document.getElementById('diagram'),labels=[...root.querySelectorAll('text')],bounds=x=>x.getBoundingClientRect();
    const overflow=[...labels,...document.querySelectorAll('#title,#phase,#scene-count,#insight strong,#insight p')].filter(x=>{const r=bounds(x);return r.left<49||r.right>1031||r.top<0||r.bottom>1662}).map(x=>x.textContent);
    const overlaps=[];for(let a=0;a<labels.length;a++)for(let b=a+1;b<labels.length;b++){
      const r=bounds(labels[a]),v=bounds(labels[b]);if(Math.min(r.right,v.right)-Math.max(r.left,v.left)>3&&Math.min(r.bottom,v.bottom)-Math.max(r.top,v.top)>3)overlaps.push([labels[a].textContent,labels[b].textContent]);
    }
    const title=bounds(document.getElementById('title')),phase=bounds(document.getElementById('phase'));if(title.bottom>phase.top)overlaps.push(['title','phase']);
    const lineOcclusion=[],opaqueRects=[...root.querySelectorAll('rect')].filter(r=>!['none','transparent'].includes(r.getAttribute('fill')));
    for(const p of root.querySelectorAll('path')){
      const len=p.getTotalLength(),m=p.getScreenCTM();
      for(let pos=0;pos<=len;pos+=6){const point=p.getPointAtLength(pos),x=m.a*point.x+m.c*point.y+m.e,y=m.b*point.x+m.d*point.y+m.f;
       // Later opaque nodes/chips cover an underlying path; such layering is visible and intentional.
       if(opaqueRects.some(r=>{if(!(p.compareDocumentPosition(r)&Node.DOCUMENT_POSITION_FOLLOWING))return false;const b=bounds(r);return x>b.left+3&&x<b.right-3&&y>b.top+3&&y<b.bottom-3;}))continue;
       for(const l of labels){const r=bounds(l);if(x>r.left+6&&x<r.right-6&&y>r.top+6&&y<r.bottom-6){if(!lineOcclusion.includes(l.textContent))lineOcclusion.push(l.textContent);}}
      }
    }
    return{state:window.__frameState,overflow,overlaps,lineOcclusion};
   });
   states.push({scene:s.id,step:step.id,position,time:t,...v.state});if(v.overflow.length||v.overlaps.length||v.lineOcclusion.length)checks.push({scene:s.id,step:step.id,position,time:t,...v});
  }
 }
 console.log(`Source ${s.id}: ${s.steps.length} steps`);
}
await sharp({create:{width:1080,height:1920,channels:3,background:'#FFF9EC'}}).composite(composite).jpeg({quality:94}).toFile(path.join(B,'qa/source-contact.jpg'));
const dense=await page.evaluate(D=>{
 let sampled=0;const issues=[];
 for(const scene of D.scenes)for(const step of scene.steps){
  for(let f=Math.floor(step.start*30);f<=Math.ceil((step.start+step.duration)*30);f++){
   const t=f/30;if(t>=scene.end)continue;window.__timelines.main.time(t,false);sampled++;
   const labels=[...document.querySelectorAll('#diagram text')],r=labels.map(x=>x.getBoundingClientRect());
   for(let a=0;a<labels.length;a++)for(let b=a+1;b<labels.length;b++)if(Math.min(r[a].right,r[b].right)-Math.max(r[a].left,r[b].left)>3&&Math.min(r[a].bottom,r[b].bottom)-Math.max(r[a].top,r[b].top)>3){
     if(issues.length<25)issues.push({time:t,scene:scene.id,step:step.id,labels:[labels[a].textContent,labels[b].textContent]});
   }
  }
 }
 return{sampled,issues};
},D);
const determinism=[];
for(const t of [13.9,43,77.5,92,122,169.9,191.8,206,222,239]){
 await page.evaluate(t=>{window.__timelines.main.time(t,false)},t);
 const one=crypto.createHash('sha256').update(await page.screenshot()).digest('hex');
 await page.evaluate(t=>{window.__timelines.main.time(239,false);window.__timelines.main.time(1,false);window.__timelines.main.time(t,false)},t);
 const two=crypto.createHash('sha256').update(await page.screenshot()).digest('hex');determinism.push({time:t,identical:one===two});
}
const math=await page.evaluate(()=>({scalar:window.SCIENCE.scalar(),updated:window.SCIENCE.scalar(1.6,.3),branch:window.SCIENCE.branch(2),mode:window.SCIENCE.mode(),chain:window.SCIENCE.chain(),selective:window.SCIENCE.selective(),compression:window.SCIENCE.compression()}));
fs.writeFileSync(path.join(B,'qa/math-rendered.json'),JSON.stringify(math,null,2));fs.writeFileSync(path.join(B,'qa/step-states.json'),JSON.stringify(states,null,2));
const result={sampledStates:states.length,dense,checks,determinism,errors};fs.writeFileSync(path.join(B,'qa/source-check.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({sampledStates:states.length,dense,issues:checks.length,determinism,errors}));
await browser.close();if(errors.length||checks.length||dense.issues.length||determinism.some(x=>!x.identical))process.exitCode=1;
