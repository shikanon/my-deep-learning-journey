/* Frame-pure SVG explanations. Every value and geometric change comes from a model. */
(() => {
'use strict';
const D=window.VIDEO_DATA;
const C={ink:'#403B35',paper:'#FFFDFA',muted:'#62574B',line:'#CDC2B0',f:'#287C78',fs:'#DFEFE8',g:'#C6533F',gs:'#FAE4DA',yellow:'#F2D179'};
const clamp=x=>Math.max(0,Math.min(1,x));
const lerp=(a,b,p)=>a+(b-a)*p;
const smooth=p=>p*p*(3-2*p);
const esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=(x,d=4)=>String(Number(x.toFixed(d))).replace('-', '−');
function scalar(w=1,b=0,x=2,y=5){const u=w*x,pred=u+b,r=pred-y,L=r*r/2;return{w,b,x,y,u,pred,r,L,gw:r*x,gb:r};}
function branch(x){return{x,square:x*x,z:x*x+x,viaSquare:2*x,viaIdentity:1,gradient:2*x+1};}
function mode(w=[1,1,1],seed=[1,0,0]){const gradient=[2*w[0],2,1];return{w,L:w[0]*w[0]+2*w[1]+w[2],gradient,jvp:gradient.reduce((s,g,i)=>s+g*seed[i],0),seed};}
function chain(x=2){const values=[x,2*x,2*x+1,(2*x+1)**2,(2*x+1)**2/5];return{values,gradient:(2*x+1)*4/5,recomputedOps:2};}
function selective(x=[1,2]){const matrix=[[2,1],[1,-3]],v=matrix.map(row=>row.reduce((s,a,i)=>s+a*x[i],0)),a=v.map(n=>Math.max(0,n));return{matrix,x,v,a,L:a.reduce((s,n)=>s+n*n,0),ga:a.map(n=>2*n)};}
function compression(values=[.1234,-.5678]){const restored=values.map(n=>Math.round(n*100)/100);return{values,restored,maxError:Math.max(...values.map((n,i)=>Math.abs(n-restored[i])))};}
const M=scalar(),BR=branch(2),MODE=mode(),MEM=chain(),SEL=selective(),ZIP=compression();
const txt=(x,y,s,size=34,color=C.ink,anchor='middle',weight=400,extra='')=>`<text x="${x}" y="${y}" font-size="${size}" fill="${color}" text-anchor="${anchor}" font-weight="${weight}" ${extra}>${esc(s)}</text>`;
const rect=(x,y,w,h,fill=C.paper,stroke=C.line,extra='')=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="17" fill="${fill}" stroke="${stroke}" stroke-width="3" ${extra}/>`;
function box(x,y,w,h,title,sub='',fill=C.paper,border=C.line,size=34){return rect(x,y,w,h,fill,border)+txt(x+w/2,y+(sub?45:h/2+12),title,size,C.ink,'middle',600)+(sub?txt(x+w/2,y+h-22,sub,30,C.muted):'');}
const tag=(x,y,s,color=C.g,size=32)=>txt(x,y,s,size,color,'middle',600);
const line=(x1,y1,x2,y2,color=C.line,width=4,dash='')=>`<path d="M${x1},${y1} L${x2},${y2}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" ${dash?'stroke-dasharray="'+dash+'"':''}/>`;
function arrow(x1,y1,x2,y2,color=C.f,p=1,width=5){p=clamp(p);if(!p)return'';const x=lerp(x1,x2,p),y=lerp(y1,y2,p),a=Math.atan2(y2-y1,x2-x1),l=14;return line(x1,y1,x,y,color,width)+`<path d="M${x-l*Math.cos(a)+7*Math.sin(a)},${y-l*Math.sin(a)-7*Math.cos(a)} L${x},${y} L${x-l*Math.cos(a)-7*Math.sin(a)},${y-l*Math.sin(a)+7*Math.cos(a)}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`+(p<1?`<circle cx="${x}" cy="${y}" r="8" fill="${color}"/>`:'');}
function chip(x,y,s,color=C.f){return rect(x-54,y-25,108,50,C.paper,color)+txt(x,y+12,s,30,color,'middle',600);}
function travel(a,b,p,value,color=C.f){if(p<=0||p>=1)return'';return chip(lerp(a[0],b[0],p),lerp(a[1],b[1],p),value,color);}
const poly=(points,color,width=5)=>`<path d="M${points.map(p=>p.map(v=>v.toFixed(3)).join(',')).join(' L')}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"/>`;
function focus(s,t){const steps=s.steps,step=[...steps].reverse().find(st=>t>=st.start)||steps[0];const at=id=>steps.find(st=>st.id===id);return{
 phase:id=>{const st=at(id);return st?clamp((t-st.start)/st.duration):0;},
 has:id=>{const st=at(id);return st&&t>=st.start;},
 start:id=>at(id)?.start??s.start,step,
};}
function result(svg,phase,insight,detail,state={}){return{svg,phase,insight,detail,state};}
// The same graph geometry is used in s02, s05 and s06, including all reverse edges.
const POS={w:[215,80],x:[735,80],u:[475,270],b:[810,465],pred:[475,465],y:[810,660],r:[475,660],L:[475,865]};
const EDGES={wu:[[245,130],[398,213]],xu:[[705,130],[552,213]],up:[[475,328],[475,407]],bp:[[725,465],[616,465]],pr:[[475,523],[475,602]],yr:[[725,660],[616,660]],rl:[[475,718],[475,807]]};
function graph({values={},forward={},reverse={},gradients={},rules=false,seed=false,emphasis=''}){
 let svg='';
 for(const [key,[a,b]] of Object.entries(EDGES)){
  svg+=arrow(...a,...b,C.line,1,3);
  if(forward[key])svg+=arrow(...a,...b,C.f,forward[key])+travel(a,b,forward[key],fmt(key==='wu'?M.w:key==='xu'?M.x:key==='bp'?M.b:key==='yr'?M.y:key==='up'?M.u:key==='pr'?M.pred:M.r));
  if(reverse[key])svg+=arrow(...b,...a,C.g,reverse[key],6)+travel(b,a,reverse[key],key==='wu'?fmt(M.gw):fmt(M.r),C.g);
 }
 const titles={w:'权重 w',x:'输入 x',u:'u = w × x',b:'偏置 b',pred:'ŷ = u + b',y:'目标 y',r:'r = ŷ − y',L:'L = r² / 2'};
 for(const [id,[x,y]]of Object.entries(POS)){
  const w=['u','pred','r','L'].includes(id)?280:170,h=['u','pred','r','L'].includes(id)?116:100;
  const active=id===emphasis;const value=values[id];
  svg+=`<g data-object="${id}">${rect(x-w/2,y-h/2,w,h,active?C.yellow:C.paper,active?C.ink:C.line)}${txt(x,y-9,titles[id],31)}${txt(x,y+37,value===undefined?'…':fmt(value),46,C.f,'middle',600)}</g>`;
 }
 if(rules){svg+=tag(310,372,'局部：1',C.muted,28)+tag(655,505,'局部：1',C.muted,28)+tag(310,571,'局部：1',C.muted,28)+tag(300,779,'局部：r = −3',C.g,28)+tag(222,200,'局部：x = 2',C.g,28);}
 if(seed)svg+=tag(475,981,'从 ∂L/∂L = 1 开始',C.g,31);
 if(gradients.r!==undefined)svg+=tag(160,667,'∂L/∂r = '+fmt(gradients.r),C.g,29);
 if(gradients.pred!==undefined)svg+=tag(158,468,'∂L/∂ŷ = '+fmt(gradients.pred),C.g,29);
 if(gradients.b!==undefined)svg+=tag(810,562,'∂L/∂b = '+fmt(gradients.b),C.g,29);
 if(gradients.w!==undefined)svg+=tag(175,249,'∂L/∂w = '+fmt(gradients.w),C.g,29);
 return svg;
}

function hook(s,t,F){
 const p=F.phase('reuse'),q=F.phase('trial'),trial=Math.min(2,Math.floor(q*3));let svg=txt(475,50,'很多参数，共用同一次模型计算',36,C.ink,'middle',600);
 const ys=[185,345,505];
 ys.forEach((y,i)=>{svg+=box(55,y-53,210,106,'w'+(i+1),'',q>0&&i===trial?C.yellow:C.paper)+arrow(265,y,425,345,C.f)+((p>0)?arrow(425,365,270,y+17,C.g,p,6):'');});
 svg+=box(430,278,255,140,'模型计算','共用中间值',C.fs,C.f,35)+arrow(685,345,745,345,C.f)+box(755,292,145,106,'L','损失',C.paper,C.f,38);
 if(p>0)svg+=arrow(747,373,688,373,C.g,p,6)+tag(555,472,'一份输出影响，沿原图分回去',C.g,32);
 svg+=txt(135,621,'… 上亿个参数',31,C.muted);
 if(q>0&&!p)svg+=rect(100,710,750,170,C.gs,C.g)+txt(475,769,'逐个试探：每动一个参数',37)+txt(475,833,'都重新计算整个模型',37);
 if(p>0)svg+=rect(100,710,750,170,C.fs,C.f)+txt(475,769,'复用共同计算',41,C.f,'middle',600)+txt(475,833,'一次反传，得到各参数梯度',36);
 if(F.has('example'))svg+=txt(475,963,'下一步：只用 w 和 b，完整算一遍',32);
 return result(svg,p>0?'核心：从一个损失，返回多个参数的影响':'问题：怎样知道每个参数该怎么改？',p>0?'共享的计算只需反着走一遍':'参数一起决定同一个损失',p>0?'接下来用两个参数，把每个步骤算出来。':'先建立共同的计算图，再观察梯度如何返回。',{trial,reverseProgress:p});
}
function forward(s,t,F){
 const v={};if(F.has('input')){v.x=M.x;v.y=M.y;}if(F.has('params')){v.w=M.w;v.b=M.b;}
 if(F.phase('params')>.8)v.u=M.u;if(F.phase('prediction')>.6)v.pred=M.pred;if(F.phase('residual')>.65)v.r=M.r;if(F.phase('loss')>.8)v.L=M.L;
 const fw={wu:F.phase('params'),xu:F.phase('params'),up:F.phase('prediction'),bp:F.phase('prediction'),pr:F.phase('residual'),yr:F.phase('residual'),rl:F.phase('loss')};
 let em=F.has('loss')?'L':F.has('residual')?'r':F.has('prediction')?'pred':F.has('params')?'u':'x';let svg=graph({values:v,forward:fw,emphasis:em});
 let a='先代入 x=2 与目标 y=5',b='w 与 b 是模型中需要学习的参数。';
 if(F.has('params')){a='先乘：1 × 2 = 2';b='乘法节点得到中间值 u=2。';}
 if(F.has('prediction')){a='再加：2 + 0 = 2';b='沿箭头送入偏置，得到预测 ŷ=2。';}
 if(F.has('residual')){a='误差：2 − 5 = −3';b='负号表示预测低于目标。';}
 if(F.has('loss')){const p=F.phase('loss');a=p<.5?'平方：(−3)² = 9':'损失：9 ÷ 2 = 4.5';b='同一前向计算，逐个生成中间数值。';}
 if(F.has('cache')){a='节点上的值，就是反传账本';b='后面沿同一张图返回，节点位置不变。';}
 return result(svg,'前向数值沿蓝绿箭头，从输入走到损失',a,b,{values:v,model:M});
}
function slope(s,t,F){
 const X=w=>95+w/4.6*755,Y=L=>745-L/13*560;let svg=txt(475,45,'只改变 w，固定 x=2、y=5、b=0',32);
 svg+=arrow(95,745,895,745,C.ink,1,3)+arrow(95,745,95,145,C.ink,1,3)+txt(903,800,'w',32)+txt(60,114,'损失 L',32);
 [0,1,2.5,4.5].forEach(w=>svg+=line(X(w),745,X(w),758,C.ink,2)+txt(X(w),801,fmt(w),28));
 [0,4.5,8,12].forEach(n=>svg+=line(86,Y(n),850,Y(n),'#E3D9C6',1)+txt(68,Y(n)+10,fmt(n),27,C.muted,'end'));
 svg+=poly(Array.from({length:185},(_,i)=>{const w=i*4.6/184;return[X(w),Y(scalar(w).L)]}),C.f,6);
 const base=[X(1),Y(M.L)];svg+=`<circle cx="${base[0]}" cy="${base[1]}" r="11" fill="${C.ink}"/>`+txt(base[0]+26,base[1]-35,'w=1，L=4.5',30,C.ink,'start');
 if(F.has('direction'))svg+=poly([.65,1.42].map(w=>[X(w),Y(M.L+M.gw*(w-1))]),C.g,5);
 if(F.has('gradient'))svg+=box(380,100,465,115,'w=1：∂L/∂w = −6','原位置的局部切线向右下',C.gs,C.g,34);
 let w=1,detail='斜率描述当前位置的变化趋势。',title='损失曲线来自同一个模型';
 if(F.has('small')){w=lerp(1,1.2,smooth(F.phase('small')));title='w 增加一点，损失下降';detail='w：1 → 1.2；L：4.5 → 3.38。';}
 if(F.has('local')){w=lerp(1.2,4.5,smooth(F.phase('local')));title='步子跨过最低点，损失可能上升';detail='大步示意：w=4.5 时，L=8。';}
 if(F.has('small')){const m=scalar(w);svg+=`<circle cx="${X(w)}" cy="${Y(m.L)}" r="13" fill="${F.has('local')?C.g:C.f}" stroke="${C.paper}" stroke-width="4"/>`+box(210,871,540,107,`w=${fmt(w,2)}    L=${fmt(m.L,3)}`,'',C.paper,F.has('local')?C.g:C.f,38);}
 if(F.has('sensitivity')){title='原位置 w=1：|−6| > |−3|';detail='同单位下，损失对 w 的局部变化更敏感。';}
 return result(svg,'曲线给出损失；局部切线给出梯度方向',title,detail,{w,L:scalar(w).L,gradient:M.gw});
}
function finite(s,t,F){
 const eps=.01,minus=scalar(1-eps),plus=scalar(1+eps),g=(plus.L-minus.L)/(2*eps),p=F.phase('perturb');
 let svg=txt(475,48,'放大 w=1 附近，ε = 0.01，固定 b=0',32);
 const runs=[{w:minus.w,pred:minus.pred,L:minus.L,y:135},{w:plus.w,pred:plus.pred,L:plus.L,y:330}];
 for(const [i,r] of runs.entries()){const q=clamp(p*2-i);svg+=box(40,r.y,220,110,'w = '+fmt(r.w),'一次模型前向',C.paper,C.f,34)+arrow(270,r.y+55,335,r.y+55,C.f,q)+box(350,r.y,220,110,q>.2?'ŷ = '+fmt(r.pred):'ŷ = …','预测值',C.fs,C.f,34)+arrow(580,r.y+55,645,r.y+55,C.f,clamp(q*2-1))+box(660,r.y,250,110,q>.7?'L = '+fmt(r.L):'L = …','损失值',C.paper,C.f,33);}
 let a='参数在 0.99 与 1.01 各算一次',b='两次前向给出两个邻近的损失。';
 if(F.has('quotient')){svg+=rect(90,515,770,205,C.gs,C.g)+txt(475,574,`损失差：${fmt(plus.L)} − ${fmt(minus.L)} = ${fmt(plus.L-minus.L)}`,31)+txt(475,642,`参数差：1.01 − 0.99 = ${fmt(2*eps)}`,34)+txt(475,701,`斜率 ≈ ${fmt(g)}`,43,C.g,'middle',600);a='损失差 ÷ 参数差 ≈ −6';b='中心差分结果与这次反传的梯度一致。';}
 if(F.has('cost')){const n=Math.min(3,Math.max(1,Math.ceil(F.phase('cost')*3)));svg+=txt(475,795,'每个参数各需要两次完整前向',32);for(let i=0;i<3;i++)svg+=box(100+i*260,841,230,100,'w'+(i+1),i<n?'2 次前向':'等待',i<n?C.yellow:C.paper,C.line,32);a=`三个参数：累计 ${n*2} 次前向`;b='n 个参数，中心差分约需要 2n 次前向。';}
 if(F.has('epsilon')){a='一般函数：ε 太大，近似误差';b='ε 太小易受舍入影响。本例为二次函数，中心差分在精确算术下恰好等于导数。';}
 if(F.has('reuse')){a='下一步：复用共同计算';b='每个基础运算只用自己的局部求导规则。';}
 return result(svg,'差分真实运行两次模型，再比较损失差',a,b,{eps,minus,plus,gradient:g});
}
function chainScene(s,t,F){
 const gradients=F.phase('residual')>.999?{r:M.r}:{};
 let svg=graph({values:M,reverse:{rl:F.phase('residual')},gradients,rules:F.has('rules'),seed:F.has('seed'),emphasis:F.has('residual')?'r':'L'});
 let a='每块运算只负责自己的局部规则',b='沿用刚才得到损失 4.5 的计算图。';
 if(F.has('product')){a='整段影响 = 上游影响 × 局部导数';b='先看最后一段：从损失 L 返回误差 r。';}
 if(F.has('seed')){a='1 × (−3) = −3';b='L=r²/2，所以局部导数 ∂L/∂r=r。';}
 if(F.has('residual')){a='误差节点收到梯度 −3';b='每条红色边都对应图中原来的一段计算。';}
 return result(svg,'链式法则：一条路径上的影响相乘',a,b,{gradients,model:M});
}
function reverse(s,t,F){
 const gp=F.phase('prediction'),gb=F.phase('bias'),gw=F.phase('weight'),gr={r:M.r};
 if(gp>.999)gr.pred=M.r;if(gb>.999)gr.b=M.gb;if(gw>.999)gr.w=M.gw;
 let svg=graph({values:M,reverse:{rl:1,pr:gp,bp:gb,up:clamp(gw*2),wu:clamp(gw*2-1)},gradients:gr,emphasis:gw>0?'w':gb>0?'b':'pred'});
 svg+=tag(288,574,'× 1',C.g,32)+tag(652,431,'× 1',C.g,32)+tag(142,189,'× 2',C.g,32);
 let a='预测 → 误差：局部导数 1',b='−3 × 1 = −3，影响沿原边返回。';
 if(F.has('bias')){a='偏置支路：−3 × 1 = −3';b='偏置每增加 1，预测就增加 1。';}
 if(F.has('weight')){a='权重支路：−3 × 1 × 2 = −6';b='乘法的局部导数是另一个因子 x=2。';}
 if(F.has('summary')){a='同一个损失，得到两个参数梯度';b='到这里反传完成，参数仍是 w=1、b=0。';}
 return result(svg,'反向梯度沿珊瑚箭头，沿原图返回参数',a,b,{gradients:gr,model:M});
}
function update(s,t,F){
 const q=smooth(F.phase('parameters')),w=lerp(M.w,M.w-.1*M.gw,q),b=lerp(M.b,M.b-.1*M.gb,q),newM=scalar(w,b),lp=smooth(F.phase('loss'));
 let svg=box(100,55,750,114,'反传结果：gw = −6，gb = −3','先有梯度，再执行优化器',C.gs,C.g,35);
 if(F.has('optimizer'))svg+=txt(475,260,'新参数 = 原参数 − 0.1 × 梯度',40,C.ink,'middle',600);
 svg+=box(55,325,390,155,'w = '+fmt(w,2),F.has('optimizer')?'1 − 0.1 × (−6)':'原权重 1',C.fs,C.f,43)+box(505,325,390,155,'b = '+fmt(b,2),F.has('optimizer')?'0 − 0.1 × (−3)':'原偏置 0',C.fs,C.f,43);
 if(F.has('prediction'))svg+=txt(475,579,`重新预测：2 × ${fmt(w,2)} + ${fmt(b,2)} = ${fmt(newM.pred,2)}`,37,C.f,'middle',600)+txt(475,642,`误差：${fmt(newM.pred,2)} − 5 = ${fmt(newM.r,2)}`,35);
 if(F.has('loss')){const L=lerp(M.L,scalar(1.6,.3).L,lp);svg+=txt(475,742,'相同刻度下比较损失',32)+txt(173,813,'更新前',31,C.muted,'end')+rect(200,777,620,53,C.gs,C.g)+tag(865,815,'4.5',C.g,32)+txt(173,906,'更新后',31,C.muted,'end')+rect(200,870,620*L/M.L,53,C.fs,C.f)+txt(220+620*L/M.L,909,fmt(L,3),33,C.f,'start',600);}
 return result(svg,'优化器接手：根据梯度改变参数',F.has('sign')?'减去负数，参数反而增加':F.has('loss')?'重新前向：损失 4.5 → 1.125':F.has('parameters')?'w：1 → 1.6；b：0 → 0.3':'反传只算梯度，更新是下一步',F.has('loss')?'学习率为 0.1；本例计算结果支持损失下降。':'每个参数变化都由同一更新公式计算。',{w,b,prediction:newM.pred,loss:newM.L,lossBar:lerp(M.L,1.125,lp)});
}
function branchScene(s,t,F){
 const sq=F.phase('square'),id=F.phase('identity'),sum=F.phase('sum');let svg=txt(475,47,'z = x² + x：同一个 x，被使用两次',36,C.ink,'middle',600);
 // Both endpoint and arrowhead must remain outside the opaque destination node.
 // Once reversing a path, remove its forward heads so only the current direction is visible.
 const leftTop=[[380,211],[235,340]],rightTop=[[570,211],[715,340]],leftBottom=[[235,485],[405,645]],rightBottom=[[715,485],[545,645]];
 for(const [a,b] of [leftTop,leftBottom])svg+=sq>0?line(...a,...b,C.line,3):arrow(...a,...b,C.f);
 for(const [a,b] of [rightTop,rightBottom])svg+=id>0?line(...a,...b,C.line,3):arrow(...a,...b,C.f);
 if(sq>0)svg+=arrow(...leftBottom[1],...leftBottom[0],C.g,sq,6)+arrow(...leftTop[1],...leftTop[0],C.g,clamp(sq*2-1),6);
 if(id>0)svg+=arrow(...rightBottom[1],...rightBottom[0],C.g,id,6)+arrow(...rightTop[1],...rightTop[0],C.g,clamp(id*2-1),6);
 svg+=box(330,93,290,113,F.has('forward')?'x = 2':'变量 x','两条路的同一个起点',C.paper,C.ink,40)+box(95,345,280,135,'平方 x²',F.has('forward')?'值：4':'',C.fs,C.f,39)+box(575,345,280,135,'直接 x',F.has('forward')?'值：2':'',C.fs,C.f,39)+box(335,650,280,130,'相加',F.has('forward')?'输出 z = 6':'',C.paper,C.f,39);
 if(F.has('square'))svg+=tag(179,566,'局部导数 2x = 4',C.g,29)+tag(165,270,'贡献：1 × 4 = 4',C.g,29);
 if(F.has('identity'))svg+=tag(773,566,'局部导数 1',C.g,29)+tag(815,270,'贡献：1 × 1 = 1',C.g,29);
 if(F.has('square')){const text=sum>.999?'梯度：4 + 1 = 5':id>.999?'等待汇总：4 与 1':sq>.999?'已收到贡献：4':'沿平方路径返回…';svg+=rect(220,832,510,122,C.gs,C.g)+txt(475,908,text,41,C.g,'middle',600);}
 if(sq>.999)svg+=tag(475,270,sum>.999?'x 收齐：4 + 1 = 5':id>.999?'x 收到：4 与 1':'x 已收到：4',C.g,28);
 return result(svg,'先沿每条原路径求贡献，再汇总到同一个 x',sum>0?'两条贡献相加：4 + 1 = 5':id>0?'直接路径也贡献 1':sq>0?'平方路径贡献 4':'一个变量进入两个下游运算',sum>0?'输出值 z=6；输入对输出的导数 dz/dx=5。':'方框保存数值，红色文字表示导数贡献。',{model:BR,contributions:[sq>.999?4:0,id>.999?1:0],gradient:sum>.999?BR.gradient:null});
}
function history(s,t,F){
 let svg=box(65,35,820,110,'局部导数：先追踪程序里的运算','反向模式思想早于神经网络的广泛应用',C.fs,C.f,34);
 if(F.has('paper'))svg+=txt(475,222,'1986 · Learning representations',38,C.ink,'middle',600)+txt(475,275,'Rumelhart · Hinton · Williams，Nature',30,C.muted);
 const xs=[130,475,815],ys=[[455,615,775],[400,555,710],[490,695]],p=F.phase('learning');
 for(let l=0;l<2;l++)for(let i=0;i<ys[l].length;i++)for(let j=0;j<ys[l+1].length;j++){svg+=line(xs[l]+26,ys[l][i],xs[l+1]-26,ys[l+1][j],C.line,2);if(p>0&&j===0)svg+=arrow(xs[l+1]-30,ys[l+1][j],xs[l]+30,ys[l][i],C.g,p,5);}
 ys.forEach((arr,l)=>arr.forEach(y=>svg+=`<circle cx="${xs[l]}" cy="${y}" r="30" fill="${l===1?C.yellow:C.fs}" stroke="${C.ink}" stroke-width="3"/>`));
 svg+=txt(130,867,'输入',34)+txt(475,867,'隐藏单元',34)+txt(815,867,'输出',34);
 if(p>0)svg+=tag(674,348,'输出误差',C.g,33)+tag(285,338,'权重收到影响',C.g,30)+txt(475,956,'网络结构示意：误差沿连接指导内部特征',31);
 return result(svg,'应用到多层网络：误差能抵达内部可训练连接',p>0?'隐藏层也能收到来自输出的影响':'先有求导规则，再应用到网络学习',p>0?'内部表示由误差指导学习；图示只展示传播路径。':'1986 年论文是经典应用节点。',{illustration:true,learningProgress:p});
}
function modes(s,t,F){
 const rp=F.phase('reverse'),p=F.phase('forward');let svg=txt(475,46,'本例：L = w₁² + 2w₂ + w₃',37,C.ink,'middle',600)+txt(475,105,'在 (w₁,w₂,w₃)=(1,1,1) 处，L=4',32);
 const ys=[275,470,665];
 ys.forEach((y,i)=>{svg+=box(45,y-60,230,120,`w${['₁','₂','₃'][i]} = 1`,rp>0?`偏导：${MODE.gradient[i]}`:i===0?'方向种子：1':'方向种子：0',rp>0?C.gs:C.paper,rp>0?C.g:C.f,34)+arrow(282,y,435,470,C.line,1,3);if(rp>0)svg+=arrow(435,488,287,y+18,C.g,rp,6);else if(i===0)svg+=arrow(282,y,435,470,C.f,p,6);});
 svg+=box(445,394,250,153,'同一程序','执行局部求导规则',C.paper,C.ink,35)+arrow(700,470,765,470,C.line,1,3)+box(775,415,150,110,rp>0?'种子 1':'变化 2',rp>0?'输出反传':'J·方向',rp>0?C.gs:C.fs,rp>0?C.g:C.f,33);
 if(rp>0)svg+=arrow(766,494,705,494,C.g,rp,6);else svg+=arrow(700,470,765,470,C.f,p,6);
 if(F.has('dimensions'))svg+=box(85,837,370,123,'前向：3 个输入方向','逐方向得到全部偏导',C.fs,C.f,31)+box(495,837,370,123,'反向：1 个标量输出','一遍得到全部三个偏导',C.gs,C.g,31);
 return result(svg,rp>0?'反向模式：从输出影响 1，返回所有输入':'前向模式：从一个输入方向，往前带变化',F.has('dimensions')?'训练：很多参数，一个标量损失':rp>0?'一遍反向，得到 (2,2,1)':'方向 (1,0,0)，得到输出变化 2',F.has('rules')?'两种模式都执行求导规则，无须差分步长 ε。':'输入方向表示导数种子，不是实际扰动参数。',{model:MODE,reverseProgress:rp});
}
function autograd(s,t,F){
 let svg=rect(65,35,820,270,C.paper,C.ink);const current=F.has('read')?3:F.has('code')?2:0;
 const code=['w.requires_grad_(True)','loss = (2*w + b - 5)**2 / 2','loss.backward()','w.grad = −6; b.grad = −3'];
 code.forEach((l,i)=>svg+=txt(105,89+i*62,l,i===3?33:31,i===current?C.g:C.muted,'start',i===current?600:400));
 let buffer=0,first=0,second=0,mean=F.has('mean'),cleared=F.has('clear');
 if(F.has('read'))buffer=-6;
 if(F.has('batch')){const p=F.phase('accumulate');first=-6;second=p>.5?-6:0;buffer=first+second;}
 if(cleared&&!mean){buffer=F.phase('clear')<.4?0:-6;first=-6;second=0;}
 if(mean){const p=F.phase('scale');first=-3;second=p>.3?-3:0;buffer=first+second;}
 svg+=txt(475,386,mean?'两批等大小 · 参数不变 · 每批 loss / 2':'参数尚未更新 · 每个新批次重新前向',30);
 svg+=box(85,453,300,132,'批次 1',mean?'梯度贡献 −3':'梯度贡献 −6',C.fs,C.f,36)+box(565,453,300,132,'批次 2',mean?'梯度贡献 −3':'梯度贡献 −6',C.fs,C.f,36);
 const p=mean?F.phase('scale'):F.phase('accumulate');svg+=arrow(235,589,414,717,C.g,mean?1:clamp(p*2),6)+arrow(715,589,536,717,C.g,clamp(p*2-1),6);
 svg+=rect(185,729,580,165,C.gs,C.g)+txt(475,782,'同一个梯度缓冲区 w.grad',33)+txt(475,858,fmt(buffer),62,C.g,'middle',600);
 if(cleared&&!mean)svg+=tag(475,959,'zero_grad()：先清零，再处理下一批',C.g,31);
 else if(mean)svg+=txt(475,959,'平均目标：−3 + (−3) = −6',34,C.g,'middle',600);
 else svg+=txt(475,959,'没有清零：0 → −6 → −12',34,C.g,'middle',600);
 return result(svg,'区分：图内路径求和，与跨批次缓冲区累计',mean?'平均目标，贡献要按总目标缩放':cleared?'独立更新：先清空梯度缓冲区':'backward() 会累加到已有 grad',mean?'两批等大小时，每批 loss/2；总梯度仍是 −6。':cleared?'清零后，新批次自己的 −6 不会叠上旧值。':'两次 −6 进入同一个缓冲区，得到 −12。',{buffer,first,second,mean,cleared});
}
function recap(s,t,F){
 let svg='';const stages=[['前向：算数值','w=1，b=0 → L=4.5','forward'],['反向：算梯度','gw=−6，gb=−3','reverse'],['优化器：更新参数','w=1.6，b=0.3','update']];
 stages.forEach(([a,b,key],i)=>{const y=60+i*265;svg+=box(125,y,700,170,a,F.has(key)?b:'等待这一阶段',F.has(key)?[C.fs,C.gs,C.yellow][i]:C.paper,F.has(key)?C.ink:C.line,40);if(i<2)svg+=arrow(475,y+175,475,y+246,i===0?C.g:C.f,F.phase(stages[i+1][2]),6);});
 if(F.has('check'))svg+=rect(120,894,710,91,C.paper,C.f)+txt(475,952,'梯度检查：差分 −6 ↔ 自动微分 −6',33,C.f,'middle',600);
 return result(svg,'一个训练步骤中，三种职责依次衔接','数值 → 梯度 → 参数更新',F.has('check')?'自动微分执行规则；差分帮助核对实现。':'求出梯度之后，才交给优化器改变参数。',{loss:M.L,gradients:[M.gw,M.gb],parameters:[1.6,.3]});
}
function memory(s,t,F){
 let svg=txt(475,43,'示例链：×2 → +1 → 平方 → ÷5',35,C.ink,'middle',600);const xs=[80,275,470,665,860],vals=MEM.values,checkpoint=F.has('checkpoint'),re=F.phase('recompute');
 xs.forEach((x,i)=>{svg+=box(x-76,155,152,109,`a${['₀','₁','₂','₃','₄'][i]}`,fmt(vals[i]),C.fs,C.f,35);if(i<4)svg+=arrow(x+78,208,xs[i+1]-79,208,C.f,1,4);});
 svg+=txt(65,359,'前向保存区（槽数示意）',30,C.muted,'start');
 const fillN=checkpoint?1:Math.min(4,Math.ceil(F.phase('all')*4));
 for(let i=0;i<4;i++){const filled=i<fillN,restored=checkpoint&&i===2&&re>.75;svg+=rect(65+i*220,387,160,130,filled||restored?C.yellow:C.paper,filled||restored?C.ink:C.line,!filled&&!restored?'stroke-dasharray="9 7"':'')+txt(145+i*220,434,`a${['₀','₁','₂','₃'][i]}`,32)+txt(145+i*220,491,filled||restored?fmt(vals[i]):'空',39,filled||restored?C.ink:C.muted,'middle',600);}
 svg+=txt(475,599,checkpoint?'检查点保留输入 a₀=2':'全部保存策略：逐步放入中间值',35);
 if(checkpoint){svg+=rect(90,682,770,165,C.paper,C.g)+txt(475,734,'反传经过平方：需要 a₂ 才能求 2a₂',32,C.g)+txt(475,806,re>.75?'a₂ = 5 → 局部导数 2a₂ = 10':'a₂ 已经丢弃：从保存的 a₀ 重算',35,C.g,'middle',600);}
 if(re>0){svg+=tag(735,114,'反向需用 a₂',C.g,28)+arrow(858,134,668,134,C.g,re,5)+arrow(663,134,478,134,C.g,re,5)+arrow(82,277,274,277,C.f,clamp(re*2),6)+arrow(276,277,470,277,C.f,clamp(re*2-1),6)+arrow(470,281,585,382,C.f,re,6);}
 if(F.has('trade'))svg+=txt(475,943,'本例：4 个长期保存槽 → 1 个；额外重算 2 步',31,C.ink,'middle',600);
 return result(svg,'激活检查点：先少存，反传需要时从检查点重建',F.has('recompute')?'先找回 a₂=5，再执行求导':checkpoint?'保留输入，暂时丢弃中间值':'反传需要前向中间值',F.has('trade')?'恢复值用于当前步骤后可释放；这是计算换存储。':'同一变量 a₂ 保持名称和位置，缺失与恢复都可见。',{values:vals,saved:fillN,recomputed:re>.75?vals[2]:null,recomputedOps:re>.75?2:0});
}
function selectiveScene(s,t,F){
 const ep=F.phase('expensive'),cp=F.phase('cheap'),rp=F.phase('compiler');let svg=txt(475,43,'选择性激活检查点 · 保存昂贵结果',35,C.ink,'middle',600);
 svg+=txt(475,110,'示例：矩阵乘法 → ReLU → 平方和',32);
 svg+=box(50,191,290,132,'矩阵乘法',ep>.7?'v = [4, −5]':'v = …',C.paper,C.f,36)+arrow(345,258,390,258,C.f,cp,5)+box(400,191,235,132,'ReLU',cp>.7?'a = [4, 0]':'a = …',C.paper,C.f,35)+arrow(640,258,685,258,C.f,cp,5)+box(695,191,205,132,'平方和',cp>.7?'L = 16':'L = …',C.paper,C.f,33);
 svg+=txt(200,163,'[[2,1],[1,−3]] × [1,2]',28,C.muted);
 if(ep>0)svg+=arrow(195,327,195,470,C.f,ep,5)+box(50,476,290,131,'保存 v','[4, −5]',C.yellow,C.ink,38);
 if(cp>0)svg+=rect(395,476,245,131,C.paper,C.line,'stroke-dasharray="8 6"')+txt(517,523,'a 不长期保存',30)+txt(517,580,rp>.7?'重建：[4,0]':'需要时再算',30,rp>.7?C.f:C.muted);
 if(rp>0)svg+=arrow(695,284,641,284,C.g,rp,6)+tag(800,381,'反向需要 a',C.g,28)+arrow(517,327,517,470,C.g,rp,5)+arrow(341,539,390,539,C.f,rp,6)+arrow(517,611,517,716,C.f,rp,5)+box(375,721,500,121,'找回 a 后计算 ∂L/∂a','2a = [8, 0]',C.gs,C.g,33);
 if(F.has('measure'))svg+=txt(475,957,'一起测：显存占用 · 训练吞吐 · 训练质量',32);
 return result(svg,'保留矩阵乘法结果，反向需要时重算便宜操作',rp>0?'缓存 v → 重算 ReLU → 得到 a':cp>0?'便宜激活可丢弃，保留重建所需输入':'昂贵结果优先保留',F.has('measure')?'实际收益依赖模型与硬件；本图是机制示例。':'算子是否保存，要考虑前向与反向各需要什么。',{model:SEL,stored:ep>.7?SEL.v:null,recomputed:rp>.7?SEL.a:null});
}
function adacc(s,t,F){
 let svg=txt(475,55,'2025 · Adacc',49,C.ink,'middle',600)+txt(475,124,'同一张量的三种选择',35);
 const xs=[170,475,780],titles=['保留','重算','压缩'];
 xs.forEach((x,i)=>{svg+=box(x-140,215,280,119,titles[i],['原值常驻','需要时恢复','更少存储'][i],[C.yellow,C.fs,C.gs][i],C.line,39);});
 if(F.has('choices'))svg+=txt(475,177,'原张量：[0.1234，−0.5678]',37,C.f,'middle',600)+arrow(170,338,170,450,C.f,1)+arrow(475,338,475,450,C.f,1)+arrow(780,338,780,450,C.f,1)+box(50,457,245,104,'精确原值','保持数值',C.paper,C.line,33)+box(350,457,250,104,'精确重算','增加运算',C.paper,C.line,33)+box(655,457,245,104,'恢复近似值','可能引入误差',C.paper,C.line,31);
 if(F.has('error'))svg+=rect(85,615,780,187,C.gs,C.g)+txt(475,663,'舍入到两位小数的误差示意',31)+txt(475,724,'恢复：[0.12，−0.57]',39,C.g,'middle',600)+txt(475,778,`最大绝对误差 = ${fmt(ZIP.maxError)}`,34,C.g);
 if(F.has('quality'))svg+=txt(475,876,'同一目标：比较存储、吞吐与训练质量',32);
 if(F.has('mechanism'))svg+=txt(475,962,'链式法则不变，改变的是保存与执行策略',31,C.ink,'middle',600);
 return result(svg,'研究方向：在保留、重算和压缩之间联合选择',F.has('error')?'恢复值与原值的差异必须检查':'同一目标下，比较三种执行选择',F.has('error')?'本图舍入仅示意误差，未复现论文的压缩配置。':'同一模型、硬件与精度设置才能比较收益。',{illustration:true,compression:ZIP});
}
function follow(s,t,F){
 let svg=txt(475,160,'我的深度学习之路',62,C.ink,'middle',600)+txt(475,276,'一起把每个知识点学懂',37,C.muted)+rect(75,400,800,258,C.yellow,C.ink)+txt(475,467,'GitHub · shikanon',44,C.ink,'middle',600)+txt(475,541,'github.com/shikanon',37)+txt(475,600,'/my-deep-learning-journey',35);
 if(F.has('content'))svg+=txt(475,795,'知识点文章 · 原始论文 · 可运行实验',36);
 if(F.has('star'))svg+=txt(475,947,'点亮 Star，下个知识点见',43,C.ink,'middle',600);
 return result(svg,'开源资料：文章、论文与实验互相对照','继续跟着具体例子理解下一步','扫描项目文字地址，或使用播放器里的项目链接。',{noQR:true});
}
const renderers={hook,forward,slope,finite,chain:chainScene,reverse,update,branch:branchScene,history,modes,autograd,recap,memory,selective:selectiveScene,adacc,follow};
const dom={diagram:document.getElementById('diagram'),title:document.getElementById('title'),count:document.getElementById('scene-count'),phase:document.getElementById('phase'),insight:document.querySelector('#insight strong'),detail:document.querySelector('#insight p'),caption:document.querySelector('#captions span'),author:document.getElementById('author'),frame:document.getElementById('author-frame'),rail:document.getElementById('rail')};
dom.rail.innerHTML=D.chapters.map((c,i)=>`<div class="chapter"><i id="chapter-${i}"></i><span>${esc(['为什么反着算','沿图算梯度','保存与重算'][i])}</span></div>`).join('');
function render(t){
 t=Math.max(0,Math.min(t,D.duration-1e-7));const s=[...D.scenes].reverse().find(s=>t>=s.start)||D.scenes[0],F=focus(s,t),r=renderers[s.kind](s,t,F),idx=D.scenes.indexOf(s);
 dom.title.textContent=s.title;dom.count.innerHTML=`<span>${String(idx+1).padStart(2,'0')} / 16</span><span>${esc(s.question)}</span>`;dom.phase.textContent=r.phase;dom.diagram.innerHTML=r.svg;dom.insight.textContent=r.insight;dom.detail.textContent=r.detail;
 const cap=D.captions.find(c=>t>=c.start&&t<c.end);dom.caption.textContent=cap?.text||'';dom.caption.style.visibility=cap?'visible':'hidden';
 D.chapters.forEach((c,i)=>{document.getElementById('chapter-'+i).style.transform=`scaleX(${clamp((t-c.start)/(c.end-c.start))})`;});
 let actorFrame=0;if(s.kind==='follow'){const start=F.start('star');actorFrame=t>=start?Math.min(23,Math.floor((t-start)*20)):0;dom.frame.setAttribute('href','#wave-'+actorFrame);dom.author.setAttribute('viewBox','0 0 384 576');}
 else{const gesture={hook:'reuse',forward:'cache',slope:'gradient',finite:'quotient',chain:'seed',reverse:'weight',update:'sign',branch:'sum',history:'learning',modes:'dimensions',autograd:'clear',recap:'reverse',memory:'recompute',selective:'compiler',adacc:'error'};
  const st=F.start(gesture[s.kind]),elapsed=t-st;actorFrame=elapsed>=0&&elapsed<2?Math.min(15,Math.floor(elapsed*8)):0;dom.frame.setAttribute('href','#doctor-'+actorFrame);dom.author.setAttribute('viewBox','0 0 512 512');}
 dom.diagram.dataset.scene=s.id;dom.diagram.dataset.step=F.step.id;window.__frameState={time:t,scene:s.id,step:F.step.id,actorFrame,models:r.state};
}
// GSAP calls function setters on every render, including seeks with callbacks suppressed.
// This keeps renderer state frame-pure in Hyperframes as well as arbitrary QA seeks.
const clock={t:0,time(value){if(arguments.length===0)return this.t;this.t=value;render(value);}};
const tl=gsap.timeline({paused:true});tl.to(clock,{time:D.duration,duration:D.duration,ease:'none'},0);
window.__timelines=window.__timelines||{};window.__timelines.main=tl;window.SCIENCE={scalar,branch,mode,chain,selective,compression,render,POS,EDGES};render(0);
})();
