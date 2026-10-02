/* Every exported frame samples this one paused, deterministic timeline. */
const D=window.LOSS_DATA;
const tl=gsap.timeline({paused:true});
const q=(id,selector)=>document.getElementById(id).querySelectorAll(selector);
const pen=(nodes,t,d=.58)=>nodes.forEach((p,i)=>{const len=p.getTotalLength();tl.fromTo(p,{strokeDasharray:len,strokeDashoffset:len},{strokeDashoffset:0,duration:d,ease:'power2.out',immediateRender:true},t+(i%9)*.018);});
function pulse(nodes,t,strength=1.05){tl.fromTo(nodes,{scale:1},{scale:strength,duration:.22,ease:'sine.inOut',repeat:3,yoyo:true,transformOrigin:'50% 50%',immediateRender:false},t);}
function moveCharacters(nodes,t,dx,dy,vars){
  // Keep authored SVG translate() positions when animating supplied character art.
  Array.from(nodes).forEach(node=>{const x=Number(node.dataset.originX),y=Number(node.dataset.originY);tl.fromTo(node,{x,y},{x:x+dx,y:y+dy,immediateRender:false,...vars},t);});
}
function pathMarker(id,scene,plan,cue,formula,maxy){
  const p=document.getElementById(id),st=plan.beats.find(b=>b.cue===cue).start+.55;
  const en=Math.max(st+.1,Math.min(scene.end-.30,st+3.4));
  tl.from(p,{opacity:0,duration:.20},st);
  for(let i=0;i<45;i++){
    const e=3*(i+1)/45,x=e/6*650,y=-formula(e)/maxy*490;
    tl.to(p,{x,y,duration:(en-st)/45,ease:'none'},st+i*(en-st)/45);
  }
}
D.chapters.forEach((c,i)=>tl.fromTo('#chapter-fill-'+i,{scaleX:0},{scaleX:1,duration:c.end-c.start,ease:'none',immediateRender:true},c.start));
D.scenes.forEach((s,i)=>{
  const root=document.getElementById(s.id),plan=D.storyboard[i],previous=i?D.scenes[i-1]:null;
  if(!previous){tl.set(root,{opacity:1},0);}
  else if(previous.chapter!==s.chapter){
    tl.set(root,{opacity:1},s.start);tl.fromTo(root,{clipPath:'circle(0% at 50% 48%)'},{clipPath:'circle(150% at 50% 48%)',duration:.38,ease:'power2.inOut',immediateRender:false},s.start);
    tl.set('#'+previous.id,{opacity:0},s.start+.38);
  }else{
    tl.fromTo(root,{x:1080,opacity:1},{x:0,opacity:1,duration:.32,ease:'power2.inOut',immediateRender:false},s.start);
    tl.to('#'+previous.id,{x:-1080,duration:.32,ease:'power2.inOut'},s.start);tl.set('#'+previous.id,{opacity:0},s.start+.32);
  }
  if(i){
    tl.from(q(s.id,'.eyebrow'),{opacity:0,y:10,duration:.30},s.start+.10);
    tl.from(q(s.id,'h1'),{opacity:0,y:18,duration:.38,ease:'back.out(1.2)'},s.start+.12);
  }
  tl.from(q(s.id,'.takeaway strong'),{opacity:0,y:8,duration:.35},s.start+.75);
  tl.from(q(s.id,'.takeaway span'),{opacity:0,y:6,duration:.35},s.start+1.05);
  tl.fromTo('#section-fill-'+i,{scaleX:0},{scaleX:1,duration:s.end-s.start,ease:'none',immediateRender:true},s.start);
  tl.set('#current-'+i,{opacity:1},s.start);tl.set('#current-'+i,{opacity:0},s.end);
  plan.beats.forEach(b=>{
    const group=document.getElementById(b.id),t=b.start;
    tl.from(group,{opacity:0,y:10,duration:.30,ease:'power2.out'},t);
    pen(Array.from(group.querySelectorAll('path.draw')),t+.05,.58);
    const labels=group.querySelectorAll('text');
    if(labels.length)tl.from(labels,{opacity:0,y:6,duration:.26,stagger:.035},t+.12);
    const mascots=group.querySelectorAll('.mascot');
    // Author limbs, mouths and eyelids animate through actual raster frames.
    // Entry gestures use talk / point / wave clips instead of a bitmap hop.
    if(b.action==='ruler')tl.from(group.querySelectorAll('path'),{x:-35,duration:.46,stagger:.018,ease:'back.out(1.2)'},t+.2);
    if(b.action==='left-to-center')tl.to(group,{x:42,duration:1.2,ease:'power2.inOut'},t+.55);
    if(b.action==='right-to-center')tl.to(group,{x:-42,duration:1.2,ease:'power2.inOut'},t+.55);
    if(b.action==='cells')tl.from(group.querySelectorAll('path.draw'),{scale:.92,duration:.36,stagger:.020,transformOrigin:'50% 50%',ease:'back.out(1.7)'},t+.18);
    if(['sum','underline','relative','celebrate','question','score-contrast'].includes(b.action))pulse(group.querySelectorAll('text'),t+.45);
    if(b.action==='score-contrast')tl.fromTo(group.querySelectorAll('text')[3],{scale:.8},{scale:1,duration:.42,ease:'back.out(1.8)',transformOrigin:'50% 50%',immediateRender:false},t+.75);
    if(b.action==='bar')tl.from(group.querySelectorAll('.loss-bar'),{scaleX:0,duration:.8,ease:'power2.inOut',transformOrigin:'0% 50%'},t+.25);
    if(b.action==='samples')tl.from(group.querySelectorAll('.sample'),{y:-55,duration:.5,stagger:.07,ease:'bounce.out'},t+.10);
    if(b.action==='pull-mean'){
      pulse(group.querySelectorAll('text'),t+.4,1.09);
      tl.fromTo('#mean-marker',{x:0},{x:110.25,duration:1.6,ease:'power2.inOut',immediateRender:false},t+.25);
    }
    if(b.action==='brake')moveCharacters(mascots,t+.35,75,0,{duration:1.6,ease:'power3.out'});
    if(b.action==='easy-down'){
      const crowd=q(s.id,'.beat[data-action="crowd"] .mascot');tl.to(crowd,{scale:.42,opacity:.60,duration:1.1,stagger:.028,ease:'power2.inOut',transformOrigin:'50% 50%'},t+.2);
    }
    if(b.action==='split-prob')pulse(group.querySelectorAll('text'),t+.35,1.04);
    if(b.action==='pull-positive')moveCharacters(group.querySelectorAll('.mascot-cat'),t+.35,85,100,{duration:1.8,ease:'power2.inOut'});
    if(b.action==='push-negative')moveCharacters(mascots,t+.35,65,55,{duration:1.8,ease:'power2.inOut'});
    if(b.action==='zoom-local')tl.from(group.querySelectorAll('path.draw'),{scale:.88,duration:1.1,transformOrigin:'50% 50%',ease:'power2.inOut'},t+.18);
    // Teacher points; student speaks, with their own sequence-frame clips.
    if(b.action==='tokens')tl.from(group.querySelectorAll('text'),{y:12,duration:.25,stagger:.10,ease:'back.out(1.4)'},t+.35);
    if(b.action==='soften')pulse(group.querySelectorAll('path.draw'),t+.35,1.025);
    if(b.action==='qr')tl.from(group.querySelector('image'),{opacity:0,scale:.96,duration:.4,transformOrigin:'50% 50%'},t+.2);
    if(b.action==='resources')tl.from(group.querySelectorAll('text'),{x:-15,duration:.4,ease:'power2.out'},t+.2);
  });
  if(s.kind==='curves')pathMarker('curve-marker',s,plan,'均方误差',e=>e*e,9);
  if(s.kind==='huber')pathMarker('huber-marker',s,plan,'大误差改成直线',e=>e<=1?.5*e*e:e-.5,4.5);
});
// Actual pose frames are selected at exact timeline times, including seeks.
// No requestAnimationFrame clock, random phase, CSS loop or image warping.
D.author_motion.forEach(actor=>{
  const viewport=document.getElementById(actor.id+'-viewport');
  const atlas=document.getElementById(actor.id+'-atlas');
  tl.set(viewport,{attr:{viewBox:'0 0 384 576','data-sprite-frame':0}},0);
  tl.set(atlas,{attr:{href:'#sprite-atlas-'+actor.clips[0].action}},0);
  actor.clips.forEach(clip=>{
    tl.set(atlas,{attr:{href:'#sprite-atlas-'+clip.action}},clip.start);
    const count=Math.ceil((clip.end-clip.start)*clip.fps-1e-7);
    for(let k=0;k<count;k++){
      const step=k+clip.phase,cycle=Math.floor(step/clip.frames.length);
      let frame=clip.frames[step%clip.frames.length];
      if(clip.action==='talk'&&frame===5&&cycle%clip.blink_every_cycles!==0)frame=6;
      const box=[frame%4*384,Math.floor(frame/4)*576,384,576].join(' ');
      tl.set(viewport,{attr:{viewBox:box,'data-sprite-frame':frame}},clip.start+k/clip.fps);
    }
  });
});
D.captions.forEach((c,i)=>{
  tl.fromTo('#cap-'+i,{opacity:0,y:5},{opacity:1,y:0,duration:.1,ease:'power2.out',immediateRender:true},c.start);
  tl.set('#cap-'+i,{opacity:0},c.end);
});
// Keep the last section label readable through the final exported frame.
tl.set('#current-'+(D.scenes.length-1),{opacity:1},D.duration-.001);
window.__timelines=window.__timelines||{};
window.__timelines.main=tl;
