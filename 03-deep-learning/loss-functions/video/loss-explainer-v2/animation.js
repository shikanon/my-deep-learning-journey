/* Every frame is a deterministic sample of this one paused timeline. */
const D=window.LOSS_DATA;
const tl=gsap.timeline({paused:true});
const q=(id,selector)=>document.getElementById(id).querySelectorAll(selector);
const pen=(nodes,t,d=.9)=>nodes.forEach((p,i)=>{const len=p.getTotalLength();tl.fromTo(p,{strokeDasharray:len,strokeDashoffset:len},{strokeDashoffset:0,duration:d,ease:'power2.out',immediateRender:true},t+(i%9)*.024);});
function pulse(nodes,t,strength=1.05){tl.fromTo(nodes,{scale:1},{scale:strength,duration:.32,ease:'sine.inOut',repeat:3,yoyo:true,transformOrigin:'50% 50%',immediateRender:false},t);}
function moveCharacters(nodes,t,dx,dy,vars){
  // SVG translate() is already a position. Animate from its authored position.
  Array.from(nodes).forEach(node=>{const x=Number(node.dataset.originX),y=Number(node.dataset.originY);tl.fromTo(node,{x,y},{x:x+dx,y:y+dy,immediateRender:false,...vars},t);});
}
function pathMarker(id,scene,plan,cue,formula,maxy){
  const p=document.getElementById(id);const st=plan.beats.find(b=>b.cue===cue).start+.8;const en=Math.min(scene.end-1,st+7);
  tl.from(p,{opacity:0,duration:.35},st);
  for(let i=0;i<45;i++){
    const e=3*(i+1)/45;const x=e/6*650;const y=-formula(e)/maxy*490;
    tl.to(p,{x,y,duration:(en-st)/45,ease:'none'},st+i*(en-st)/45);
  }
}
D.chapters.forEach((c,i)=>tl.fromTo('#chapter-fill-'+i,{scaleX:0},{scaleX:1,duration:c.end-c.start,ease:'none',immediateRender:true},c.start));
D.scenes.forEach((s,i)=>{
  const root=document.getElementById(s.id);const plan=D.storyboard[i];const previous=i?D.scenes[i-1]:null;
  if(!previous){tl.fromTo(root,{opacity:0},{opacity:1,duration:.45,ease:'sine.out'},.1);}
  else if(previous.chapter!==s.chapter){
    tl.set(root,{opacity:1},s.start);tl.fromTo(root,{clipPath:'circle(0% at 50% 48%)'},{clipPath:'circle(150% at 50% 48%)',duration:.60,ease:'power2.inOut',immediateRender:false},s.start);
    tl.set('#'+previous.id,{opacity:0},s.start+.60);
  }else{
    tl.fromTo(root,{x:1080,opacity:1},{x:0,opacity:1,duration:.50,ease:'power2.inOut',immediateRender:false},s.start);
    tl.to('#'+previous.id,{x:-1080,duration:.50,ease:'power2.inOut'},s.start);tl.set('#'+previous.id,{opacity:0},s.start+.50);
  }
  tl.from(q(s.id,'.eyebrow'),{opacity:0,y:12,duration:.5},s.start+.2);
  tl.from(q(s.id,'h1'),{opacity:0,y:24,duration:.65,ease:'back.out(1.2)'},s.start+.24);
  tl.from(q(s.id,'.takeaway strong'),{opacity:0,y:10,duration:.6},s.start+1.5);
  tl.from(q(s.id,'.takeaway span'),{opacity:0,y:8,duration:.6},s.start+2.1);
  tl.fromTo('#section-fill-'+i,{scaleX:0},{scaleX:1,duration:s.end-s.start,ease:'none',immediateRender:true},s.start);
  tl.set('#current-'+i,{opacity:1},s.start);tl.set('#current-'+i,{opacity:0},s.end);
  plan.beats.forEach(b=>{
    const group=document.getElementById(b.id),t=b.start;
    tl.from(group,{opacity:0,y:14,duration:.52,ease:'power2.out'},t);
    pen(Array.from(group.querySelectorAll('path.draw')),t+.1,1.0);
    const labels=group.querySelectorAll('text');
    if(labels.length)tl.from(labels,{opacity:0,y:8,duration:.42,stagger:.08},t+.28);
    const mascots=group.querySelectorAll('.mascot');
    if(b.action==='hop')moveCharacters(mascots,t+.6,0,-14,{duration:.55,ease:'sine.inOut',repeat:5,yoyo:true});
    if(b.action==='ruler')tl.from(group.querySelectorAll('path'),{x:-40,duration:.8,stagger:.03,ease:'back.out(1.2)'},t+.4);
    if(b.action==='left-to-center')tl.to(group,{x:42,duration:2.0,ease:'power2.inOut'},t+1.2);
    if(b.action==='right-to-center')tl.to(group,{x:-42,duration:2.0,ease:'power2.inOut'},t+1.2);
    if(b.action==='cells')tl.from(group.querySelectorAll('path.draw'),{scale:.92,duration:.55,stagger:.035,transformOrigin:'50% 50%',ease:'back.out(1.7)'},t+.3);
    if(['sum','underline','relative','celebrate'].includes(b.action))pulse(group.querySelectorAll('text'),t+1.0);
    if(b.action==='bar')tl.from(group.querySelectorAll('.loss-bar'),{scaleX:0,duration:1.25,ease:'power2.inOut',transformOrigin:'0% 50%'},t+.5);
    if(b.action==='samples')tl.from(group.querySelectorAll('.sample'),{y:-70,duration:.8,stagger:.12,ease:'bounce.out'},t+.2);
    if(b.action==='pull-mean'){
      pulse(group.querySelectorAll('text'),t+.9,1.09);
      tl.fromTo('#mean-marker',{x:0},{x:110.25,duration:2.5,ease:'power2.inOut',immediateRender:false},t+.4);
    }
    if(b.action==='brake')moveCharacters(mascots,t+.7,75,0,{duration:2.5,ease:'power3.out'});
    if(b.action==='easy-down'){
      const crowd=q(s.id,'.beat[data-action="crowd"] .mascot');tl.to(crowd,{scale:.42,opacity:.60,duration:2,stagger:.035,ease:'power2.inOut',transformOrigin:'50% 50%'},t+.3);
    }
    if(b.action==='split-prob')pulse(group.querySelectorAll('text'),t+.7,1.04);
    if(b.action==='pull-positive')moveCharacters(group.querySelectorAll('.mascot-cat'),t+.65,85,100,{duration:3,ease:'power2.inOut'});
    if(b.action==='push-negative')moveCharacters(mascots,t+.65,65,55,{duration:3,ease:'power2.inOut'});
    if(b.action==='zoom-local')tl.from(group.querySelectorAll('path.draw'),{scale:.88,duration:1.8,transformOrigin:'50% 50%',ease:'power2.inOut'},t+.3);
    if(b.action==='teach')moveCharacters(mascots,t+.6,0,-10,{duration:.6,repeat:3,yoyo:true,ease:'sine.inOut'});
    if(b.action==='tokens')tl.from(group.querySelectorAll('text'),{y:16,duration:.4,stagger:.16,ease:'back.out(1.4)'},t+.8);
    if(b.action==='soften')pulse(group.querySelectorAll('path.draw'),t+.8,1.025);
  });
  if(s.kind==='curves')pathMarker('curve-marker',s,plan,'均方误差',e=>e*e,9);
  if(s.kind==='huber')pathMarker('huber-marker',s,plan,'大误差改成直线',e=>e<=1?.5*e*e:e-.5,4.5);
  // A short finite blink gives the guide life without moving labels or data.
  q(s.id,'.eyes').forEach((eye,j)=>tl.fromTo(eye,{scaleY:1},{scaleY:.1,duration:.10,repeat:1,yoyo:true,transformOrigin:'50% 50%',immediateRender:false},Math.min(s.end-.3,s.start+5+j*.4)));
});
D.captions.forEach((c,i)=>{
  tl.fromTo('#cap-'+i,{opacity:0,y:7},{opacity:1,y:0,duration:.16,ease:'power2.out',immediateRender:true},c.start);
  tl.set('#cap-'+i,{opacity:0},c.end);
});
tl.from('.top-progress',{opacity:0,y:-10,duration:.5},.12);
tl.from('footer',{opacity:0,duration:.7},.4);
window.__timelines=window.__timelines||{};
window.__timelines.main=tl;
