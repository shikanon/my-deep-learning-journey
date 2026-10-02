// Every effect is derived from the paused root timeline; seeking reproduces a frame.
(() => {
  const D = window.LOSS_DATA;
  const tl = gsap.timeline({ paused: true });
  const clean = s => s.replace(/[^\p{L}\p{N}]/gu, '');
  const sceneMap = Object.fromEntries(D.scenes.map(s => [s.id, s]));
  function cue(id, phrase, fallback = .5) {
    const s = sceneMap[id];
    const all = s.words.map(w => clean(w.text)).join('');
    const at = all.indexOf(clean(phrase));
    if (at < 0) return s.start + (s.end - s.start) * fallback;
    let pos = 0;
    for (const w of s.words) {
      pos += clean(w.text).length;
      if (pos > at) return Math.max(s.start + .3, w.start);
    }
    return s.start;
  }
  function reveal(id, sel, t, from = {}) {
    const els = document.getElementById(id).querySelectorAll(sel);
    if (!els.length) return;
    gsap.set(els, {opacity:0});
    tl.fromTo(els, { opacity: 0, y: 22, ...from }, {
      opacity: 1, y: 0, scale: 1, rotation: 0, duration: .55,
      stagger: .13, ease: 'power3.out', immediateRender: false,
    }, t);
  }
  function draw(id, sel, t, duration = 1.3) {
    document.getElementById(id).querySelectorAll(sel).forEach(el => {
      const length = el.getTotalLength();
      gsap.set(el, {strokeDasharray:`${length} ${length}`,strokeDashoffset:length});
      tl.fromTo(el, { strokeDasharray: `${length} ${length}`, strokeDashoffset: length },
        { strokeDashoffset: 0, duration, ease: 'power2.inOut', immediateRender: false }, t);
    });
  }
  function followCurve(id, sel, t, duration, curve, steps=54) {
    // Short deterministic segments keep the marker on the mathematical curve.
    for(let i=1;i<=steps;i++) {
      const [cx,cy]=curve(i/steps);
      tl.to('#'+id+' '+sel,{attr:{cx,cy},duration:duration/steps,ease:'none'},t+(i-1)*duration/steps);
    }
  }
  // Persistent progress provides orientation without competing with the experiment.
  tl.fromTo('.progress', {scaleX:0}, { scaleX: 1, duration: D.duration, ease: 'none' }, 0);
  D.scenes.forEach((s, i) => {
    const element = document.getElementById(s.id);
    const start = s.start;
    if (i > 0) {
      const mode = ['history', 'timeline', 'frontier'].includes(s.id) ? 'zoom' :
        ['outlier','huber','ce','focal','smoothing'].includes(s.id) ? 'dissolve' : 'push';
      const previous = document.getElementById(D.scenes[i-1].id);
      if(mode==='push') {
        // Matching motion preserves a seam between two full-frame scenes.
        tl.to(previous,{opacity:1,y:-1920,duration:.42,ease:'power2.inOut'},start);
        tl.fromTo(element,{opacity:1,y:1920,scale:1},
          {opacity:1,y:0,scale:1,duration:.42,ease:'power2.inOut',immediateRender:false},start);
      } else {
        // Text leaves before the following headline appears.
        tl.to(previous,{opacity:0,y:0,duration:.14,ease:'power2.inOut'},start);
        tl.fromTo(element,{opacity:0,y:0,scale:mode==='zoom'?.965:1},
          {opacity:1,y:0,scale:1,duration:.28,ease:'power3.out',immediateRender:false},start+.14);
      }
      tl.set(previous, { opacity: 0 }, start + .43);
    }
    if (i) reveal(s.id, 'h1', start+.18, {y:28});
    reveal(s.id, '.insight', cue(s.id, s.text.slice(-18), .82), {y:14});
  });
  const Q=(id,sel)=>'#'+id+' '+sel;
  reveal('hook','.answer-card',cue('hook','一台人工智能',.12),{scale:.95,y:30});
  reveal('hook','.hook-question',cue('hook','它们应该',.6),{scale:1.08,y:0});
  tl.to(Q('hook','.answer-card'),{stroke:'#FFB56B',duration:.8,ease:'sine.inOut'},cue('hook','百分之九十九'));
  reveal('loop','.flow-node',sceneMap.loop.start+.3,{x:-25,y:0});
  reveal('loop','.flow-arrow',cue('loop','模型先作答',.4),{scale:.6,y:0});
  ['模型先作答','损失函数负责扣分','反向传播','优化器'].forEach((w,i)=>{
    const r=document.querySelectorAll(Q('loop','.flow-node rect'))[i];
    tl.to(r,{attr:{stroke:'#FFB56B','stroke-width':5},duration:.3,ease:'sine.out'},cue('loop',w,.35+i*.13));
    tl.to(r,{attr:{stroke:'#34545B','stroke-width':2},duration:.4,ease:'power2.out'},cue('loop',w,.35+i*.13)+2.0);
  });
  draw('metric','.step-path',sceneMap.metric.start+.4,1.2);
  reveal('metric','.step-note',sceneMap.metric.start+1.0);
  tl.to(Q('metric','.flat-dot'),{attr:{cx:580},duration:3,ease:'none'},cue('metric','小幅调整',.2));
  draw('metric','.smooth-path',cue('metric','可优化的损失',.52),1.6);
  reveal('metric','.smooth-note',cue('metric','更细的反馈',.65));
  followCurve('metric','.smooth-dot',cue('metric','更细的反馈',.65),3.2,f=>[250+270*f,140+480*Math.pow((150+270*f)/730,1.8)]);
  draw('history','.orbit-path',sceneMap.history.start+.35,2.2);
  tl.fromTo(Q('history','.orbit-object'),{scale:.6,transformOrigin:'50% 50%'},{scale:1,duration:1,ease:'back.out(1.2)',immediateRender:false},sceneMap.history.start+.3);
  reveal('history','.history-node',cue('history','一八零五年',.23),{y:40,scale:.98});
  draw('mse','.mse-path',sceneMap.mse.start+.4,1.5);
  reveal('mse','.mse-one',cue('mse','错一点',.2),{scale:.8,y:0});
  reveal('mse','.mse-nine',cue('mse','错三点',.35),{scale:1.15,y:0});
  followCurve('mse','.mse-dot',cue('mse','错三点',.35),1.7,f=>[100+(1+2*f)*230,665-Math.pow(1+2*f,2)*55]);
  reveal('mse','.mse-formula',cue('mse','把误差平方',.12),{scale:.95,y:0});
  reveal('outlier','.sample:not(.outlier-sample)',sceneMap.outlier.start+.35,{scale:.85,y:-18});
  reveal('outlier','.outlier-sample',cue('outlier','还有二十',.45),{x:70,y:0,scale:.7});
  tl.to(Q('outlier','.mean-marker'),{x:142.763,duration:1.1,ease:'power2.inOut'},cue('outlier','还有二十',.45));
  reveal('outlier','.mse-winner',cue('outlier','平均数六',.60),{scale:.94,y:35});
  reveal('outlier','.mae-winner',cue('outlier','中位数三',.78),{scale:.94,y:35});
  draw('huber','.square-reference',sceneMap.huber.start+.4,1.3);
  draw('huber','.huber-path',cue('huber','小误差',.35),1.6);
  reveal('huber','.huber-small',cue('huber','小误差',.35));
  reveal('huber','.huber-large',cue('huber','大误差',.45),{x:20,y:0});
  followCurve('huber','.huber-dot',cue('huber','限速器',.63),2.5,f=>[465+3*f*115,655-(3*f<=1?.5*Math.pow(3*f,2):3*f-.5)*100]);
  draw('ce','.ce-path',sceneMap.ce.start+.4,1.5);
  reveal('ce','.ce-good',cue('ce','百分之九十',.40),{scale:.92,y:0});
  reveal('ce','.ce-bad',cue('ce','百分之一',.65),{scale:1.08,y:0});
  followCurve('ce','.ce-dot',cue('ce','百分之一',.65),2,f=>{const p=Math.exp(Math.log(.9)+(Math.log(.01)-Math.log(.9))*f);return [100+p*725,665+Math.log(p)*80];});
  reveal('focal','.easy-dot',sceneMap.focal.start+.35,{scale:0,y:0});
  reveal('focal','.hard-dot',cue('focal','背景',.18),{scale:.2,y:0});
  tl.to(Q('focal','.easy-dot'),{attr:{r:4},opacity:.5,duration:1.4,stagger:.025,ease:'power2.inOut'},cue('focal','乘上一个权重',.43));
  // Dot sizes merely encode relative influence; exact numeric loss weights are printed.
  reveal('focal','.easy-weight',cue('focal','权重越小',.60),{y:10});
  reveal('focal','.hard-weight',cue('focal','不会淹没难题',.72),{y:10});
  reveal('smoothing','.label-column',sceneMap.smoothing.start+.4,{y:35});
  const smoothAt=cue('smoothing','约百分之九十三',.47);
  [.9333333,.0333333,.0333333].forEach((v,i)=>{
    tl.to(Q('smoothing',`.sb-${i}`),{attr:{height:v*400,y:620-v*400},duration:1.4,ease:'power2.inOut'},smoothAt);
    tl.set(Q('smoothing',`.sn-${i}`),{textContent:(v*100).toFixed(1)+'%'},smoothAt+.5);
  });
  reveal('contrast','.cat-a,.cat-b,.car',sceneMap.contrast.start+.35,{scale:.7,y:0});
  draw('contrast','.attract-line',cue('contrast','两个视图',.30),1.1);
  tl.to(Q('contrast','.cat-b'),{x:-260,y:-155,duration:2.2,ease:'power2.inOut'},cue('contrast','靠近',.40));
  tl.to(Q('contrast','.attract-line'),{attr:{x2:373,y2:339},duration:2.2,ease:'power2.inOut'},cue('contrast','靠近',.40));
  tl.to(Q('contrast','.car'),{x:225,y:110,duration:1.7,ease:'sine.inOut'},cue('contrast','远离',.50));
  reveal('contrast','.contrast-pair',cue('contrast','同一张猫',.22));
  reveal('multitask','.task-card',sceneMap.multitask.start+.35,{y:35});
  draw('multitask','.gradient-a',cue('multitask','合并多个损失',.23),1.2);
  draw('multitask','.gradient-b',cue('multitask','一个数值大',.4),1.2);
  draw('multitask','.gradient-combined',cue('multitask','梯度方向',.65),1.2);
  reveal('multitask','.combined-note',cue('multitask','谁主导学习',.73));
  reveal('timeline','.era',sceneMap.timeline.start+.35,{x:35,y:0});
  tl.fromTo(Q('timeline','.era circle'),{scale:.55,transformOrigin:'50% 50%'},{scale:1,duration:.4,stagger:2,ease:'back.out(1.2)',immediateRender:false},sceneMap.timeline.start+1.0);
  reveal('dpo','.preferred',cue('dpo','更喜欢',.28),{x:-30,y:0});
  reveal('dpo','.dispreferred',cue('dpo','更不喜欢',.38),{x:30,y:0});
  reveal('dpo','.dpo-rule',cue('dpo','参考模型',.5),{scale:.94,y:0});
  tl.to(Q('dpo','.preferred rect'),{attr:{stroke:'#A5E1C8','stroke-width':5},duration:1,ease:'sine.inOut'},cue('dpo','直接调整',.63));
  reveal('frontier','.research-card',sceneMap.frontier.start+.35,{y:35});
  reveal('frontier','.importance',cue('frontier','旧策略',.47),{scaleY:.3,y:0});
  reveal('frontier','.vespo-title',cue('frontier','维斯波',.7),{scale:1.08,y:0});
  [0.18,.45,.7,1.5,2.4].forEach((v,i)=>tl.to(Q('frontier',`.iw-${i}`),{attr:{height:v*55,y:630-v*55},duration:1.5,ease:'power2.inOut'},cue('frontier','平衡重要性权重',.80)));
  reveal('frontier','.vespo-note',cue('frontier','训练稳定性',.89));
  reveal('newest','.cg-positive,.cg-negative',sceneMap.newest.start+.35,{scale:.4,y:0});
  tl.to(Q('newest','.cg-positive'),{x:i=>[25,-4,20,-28,0][i],y:i=>[23,16,-12,-9,-37][i],duration:2,ease:'power2.inOut'},cue('newest','聚类',.2));
  tl.to(Q('newest','.cg-negative'),{x:60,duration:2,ease:'sine.inOut'},cue('newest','检测',.32));
  reveal('newest','.evidence-tag',cue('newest','预印本',.49),{y:30});
  reveal('close','.closing-question',sceneMap.close.start+.4,{x:-40,y:0});
  ['怕哪一种错','有没有异常','真实效果'].forEach((w,i)=>{
    const r=document.querySelectorAll(Q('close','.closing-question rect'))[i];
    tl.to(r,{attr:{stroke:'#A5E1C8','stroke-width':5},duration:.4,ease:'sine.out'},cue('close',w,.23+i*.15));
  });
  D.captions.forEach((c,i)=>{
    const el=document.getElementById(`cap-${i}`);
    tl.fromTo(el,{opacity:0,y:7},{opacity:1,y:0,duration:.10,ease:'power1.out',immediateRender:false},c.start);
    tl.to(el,{opacity:0,duration:.08,ease:'power1.in'},Math.max(c.start+.1,c.end-.08));
    tl.set(el,{opacity:0},c.end);
  });
  tl.set({}, {}, D.duration);
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
