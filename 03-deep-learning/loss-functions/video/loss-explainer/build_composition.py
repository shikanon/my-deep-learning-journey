"""Build original SVG/HTML scenes and embed a seekable, speech-timed timeline."""
import html,json,math
from pathlib import Path
B=Path(__file__).resolve().parent
D=json.loads((B/'timeline.json').read_text())
C={'mint':'#A5E1C8','orange':'#FFB56B','red':'#FF8B86','white':'#F3EDE1','muted':'#B8CCC9','line':'#34545B'}
def txt(x,y,t,size=38,color='white',cls='',anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{C.get(color,color)}" class="{cls}" text-anchor="{anchor}">{html.escape(str(t))}</text>'
def line(x1,y1,x2,y2,col='line',w=3,cls='',dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C.get(col,col)}" stroke-width="{w}" class="{cls}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def circle(x,y,r=10,col='mint',cls=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C.get(col,col)}" class="{cls}"/>'
def path(points,col,cls='',w=7):
    d=' '.join(('M' if i==0 else 'L')+f'{x:.2f},{y:.2f}' for i,(x,y) in enumerate(points))
    return f'<path d="{d}" stroke="{C[col]}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" fill="none" class="{cls}"/>'
def svg(body):return '<svg viewBox="0 0 920 800" aria-hidden="true">'+body+'</svg>'
def cat(x=460,y=220,scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})"><path d="M-130 30 L-130-120 L-65-70 Q0-110 65-70 L130-120 L130 30 Q110 140 0 150 Q-110 140-130 30" fill="#182F35" stroke="#A5E1C8" stroke-width="7"/>'+circle(-50,15,9)+circle(50,15,9)+f'<path d="M-13 55 L13 55 L0 70 Z" fill="#FFB56B"/><path d="M0 70 Q-35 110-55 85 M0 70 Q35 110 55 85" stroke="#A5E1C8" fill="none" stroke-width="5"/>'+line(-135,58,-195,40,'mint',4)+line(135,58,195,40,'mint',4)+'</g>'
def box(x,y,w,h,body,cls=''):
    return f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="24" fill="#182F35" stroke="#34545B" stroke-width="2"/>{body}</g>'
def axes(x0=100,y0=650,x1=830,y1=130):
    s=line(x0,y0,x1,y0,w=3)+line(x0,y0,x0,y1,w=3)
    for f in (.25,.5,.75,1):s+=line(x0,y0-(y0-y1)*f,x1,y0-(y0-y1)*f,w=1)
    return s
V={}
V['hook']=svg(cat(460,135,.84)+txt(460,330,'真实答案：猫',38,'mint',anchor='middle')+
    box(15,375,425,350,txt(45,434,'模型 A · 犹豫',38)+txt(230,554,'51%',100,'orange','mono',anchor='middle')+txt(230,615,'判成狗',38,'red',anchor='middle')+txt(230,683,'给猫 49%',34,'muted',anchor='middle'),'answer-card')+
    box(480,375,425,350,txt(510,434,'模型 B · 确信',38)+txt(690,554,'99%',100,'orange','mono',anchor='middle')+txt(690,615,'判成狗',38,'red',anchor='middle')+txt(690,683,'给猫 1%',34,'muted',anchor='middle'),'answer-card')+
    txt(460,784,'同样答错，严重程度不同',42,'white','hook-question',anchor='middle'))
steps=[('01','模型','先给出预测','mint'),('02','损失函数','把差距变成分数','orange'),('03','反向传播','计算参数梯度','mint'),('04','优化器','执行参数更新','white')]
s=''
for i,(n,name,desc,c) in enumerate(steps):
    y=30+i*184;s+=box(30,y,860,150,txt(70,y+88,n,52,c,'mono')+txt(185,y+65,name,48,c)+txt(185,y+118,desc,34,'muted'),'flow-node');
    if i<3:s+=txt(460,y+181,'↓',34,'orange','flow-arrow',anchor='middle')
V['loop']=svg(s)
s=axes(90,665,830,110)+txt(70,70,'损失 / 评分反馈',34,'muted')+txt(670,725,'参数的小调整',34,'muted')
s+=path([(100,310),(720,310),(720,640),(830,640)],'orange','step-path',7)
s+=path([(100+i*730/100,140+480*(i/100)**1.8) for i in range(101)],'mint','smooth-path',7)
s+=txt(120,274,'只看对错：一大段不变',35,'orange','step-note')+txt(150,570,'连续损失：细小变化也可见',35,'mint','smooth-note')
s+=circle(250,310,14,'orange','flat-dot')+circle(250,140+480*(150/730)**1.8,14,'mint','smooth-dot')
V['metric']=svg(s)
s=''
for i,(x,y) in enumerate([(110,125),(290,80),(665,175),(780,310),(610,445),(190,365)]):
    s+=circle(x,y,5,'muted','star')
s+=circle(470,250,66,'orange','orbit-object')+path([(80+i*7.6,250+160*math.sin(i*math.pi/50)) for i in range(101)],'mint','orbit-path',3)
s+=box(25,510,420,240,txt(65,610,'1805',85,'orange','mono')+txt(65,677,'勒让德 · 公开发表',34)+txt(65,725,'最小二乘法',34,'muted'),'history-node')
s+=box(475,510,420,240,txt(515,610,'1809',85,'mint','mono')+txt(515,677,'高斯 · 概率解释',34)+txt(515,725,'误差如何汇总',34,'muted'),'history-node')
V['history']=svg(s)
s=axes(100,665,830,120)+txt(90,76,'单样本损失 · 横轴为 |e|',34,'muted')+''
for val in (0,1,2,3):s+=txt(100+val*230,710,str(val),32,'muted','mono',anchor='middle')
for val in (3,6,9):s+=txt(78,665-val*55,str(val),32,'muted','mono',anchor='end')
s+=path([(100+e*230,665-e*e*55) for e in [i*3/100 for i in range(101)]],'orange','mse-path')
s+=circle(330,610,16,'orange','mse-dot')+txt(540,315,'e²',130,'orange','mse-formula mono',anchor='middle')
s+=txt(210,425,'1 → 1',62,'white','mse-one mono')+txt(210,500,'3 → 9',62,'orange','mse-nine mono')
s+=txt(460,780,'MSE = 所有 e² 的平均值',38,'white',anchor='middle')
V['mse']=svg(s)
s=txt(35,64,'同一个数字 c，预测五个样本',38,'muted')
for i,n in enumerate([1,2,3,4,20]):
    x=42+i*179;s+=box(x,115,148,140,txt(x+74,209,str(n),66,'orange' if n==20 else 'white','mono',anchor='middle'),'sample outlier-sample' if n==20 else 'sample')
s+=line(70,385,845,385,w=4)
for n in [1,2,3,4,6,10,15,20]:
    x=70+(n-1)*775/19;s+=line(x,373,x,397,w=3)+txt(x,440,str(n),28,'muted','mono',anchor='middle')
s+=f'<g class="mean-marker">'+circle(70+1.5*775/19,385,17,'orange')+txt(70+1.5*775/19,352,'平均数',32,'orange',anchor='middle')+'</g>'
s+=circle(70+2*775/19,385,11,'mint','median-marker')
s+=box(25,510,420,245,txt(65,572,'MSE 最小',40,'orange')+txt(230,676,'c = 6',90,'orange','mono',anchor='middle')+txt(230,728,'均方误差 50.0',34,'muted',anchor='middle'),'mse-winner')
s+=box(475,510,420,245,txt(515,572,'MAE 最小',40,'mint')+txt(690,676,'c = 3',90,'mint','mono',anchor='middle')+txt(690,728,'绝对误差 4.2',34,'muted',anchor='middle'),'mae-winner')
V['outlier']=svg(s)
s=axes(90,655,840,120)+txt(90,76,'单样本损失 · δ = 1',34,'muted')
for val in (0,1,2,3):s+=txt(465+val*115,709,str(val),30,'muted','mono',anchor='middle')
s+=path([(465+e*115,655-.5*e*e*100) for e in [-3+i*6/200 for i in range(201)]],'line','square-reference',4)
s+=path([(465+e*115,655-(.5*e*e if abs(e)<=1 else abs(e)-.5)*100) for e in [-3+i*6/200 for i in range(201)]],'mint','huber-path',8)
s+=line(350,150,350,655,'orange',2,dash='8 10')+line(580,150,580,655,'orange',2,dash='8 10')
s+=txt(465,335,'小误差：平方',42,'mint','huber-small',anchor='middle')+txt(665,420,'大误差：线性',36,'orange','huber-large',anchor='middle')
s+=circle(465,655,16,'mint','huber-dot')+txt(700,755,'残差 e',34,'muted')
V['huber']=svg(s)
s=txt(35,58,'给真实类别的概率 p',36,'muted')+txt(460,165,'−ln(p)',110,'mint','mono',anchor='middle')+axes(100,665,825,265)
for val in (0.01,.5,.9,1):s+=txt(100+val*725,715,str(val),28,'muted','mono',anchor='middle')
s+=path([(100+p*725,665+math.log(p)*80) for p in [.01+i*.99/180 for i in range(181)]],'mint','ce-path')
s+=circle(100+.9*725,665+math.log(.9)*80,16,'orange','ce-dot')
s+=txt(450,365,'90% → 0.11',48,'white','ce-good mono',anchor='middle')+txt(450,450,'1% → 4.61',48,'orange','ce-bad mono',anchor='middle')
s+=txt(40,785,'模型自信地错：给正确答案极低概率',34,'muted')
V['ce']=svg(s)
s=txt(35,65,'CE × (1 − p)²',64,'mint','mono')+txt(35,120,'此处 γ = 2，α = 1',32,'muted')
for i in range(40):
    x=68+(i%8)*76;y=240+(i//8)*76
    s+=circle(x,y,18,'mint','easy-dot')
for i,(x,y) in enumerate([(720,310),(790,470),(700,620)]):s+=circle(x,y,31,'orange','hard-dot')
s+=txt(60,690,'容易的样本',34,'mint')+txt(640,690,'困难的样本',34,'orange')
s+=txt(60,760,'p = .99',36,'mint','mono')+txt(610,760,'p = .20',36,'orange','mono')
s+=txt(35,180,'损失权重 .0001',38,'mint','easy-weight')+txt(590,180,'损失权重 .64',38,'orange','hard-weight')
V['focal']=svg(s)
s=txt(35,65,'3 类 · 平滑强度 ε = .1',40,'muted')
for i,(label,val,c) in enumerate([('猫',1,'mint'),('狗',0,'orange'),('鸟',0,'orange')]):
    x=85+i*270;s+=f'<g class="label-column"><rect x="{x}" y="220" width="160" height="400" rx="10" fill="#182F35"/><rect x="{x}" y="{620-val*400}" width="160" height="{val*400}" rx="10" fill="{C[c]}" class="smooth-bar sb-{i}"/>'+txt(x+80,702,label,46,'white',anchor='middle')+txt(x+80,180,f'{val*100:.0f}%',48,c,f'smooth-num sn-{i} mono',anchor='middle')+'</g>'
s+=txt(460,790,'q′ = (1 − ε) q + ε / K',39,'white','mono',anchor='middle')
V['smoothing']=svg(s)
s=txt(35,55,'二维表示空间 · 教学示意',34,'muted')
s+=line(70,680,850,680,w=2)+line(70,680,70,140,w=2)
s+=f'<g class="cat-a">'+circle(290,310,72,'mint')+txt(290,325,'猫 A',36,'#101F24',anchor='middle')+'</g>'
s+=f'<g class="cat-b">'+circle(705,520,72,'mint')+txt(705,535,'猫 A′',36,'#101F24',anchor='middle')+'</g>'
s+=f'<g class="car">'+circle(485,400,65,'orange')+txt(485,415,'车',40,'#101F24',anchor='middle')+'</g>'
s+=line(362,346,636,491,'mint',5,'attract-line',dash='10 10')
s+=txt(460,105,'同一张猫，两个视图',40,'mint','contrast-pair',anchor='middle')+txt(460,765,'匹配的靠近 · 不匹配的分开',38,'white',anchor='middle')
V['contrast']=svg(s)
s=txt(460,110,'J = λ₁L₁ + λ₂L₂',72,'mint','mono',anchor='middle')
s+=box(25,180,420,150,txt(65,240,'类别损失',42,'mint')+txt(65,297,'正确识别物体',34,'muted'),'task-card')
s+=box(475,180,420,150,txt(515,240,'深度损失',42,'orange')+txt(515,297,'正确判断距离',34,'muted'),'task-card')
s+=line(460,700,460,380,w=2)+line(190,680,790,680,w=2)
s+=line(460,680,245,435,'mint',8,'gradient-a')+line(460,680,695,500,'orange',8,'gradient-b')
s+=circle(460,680,15,'white')+line(460,680,468.47,500,'white',10,'gradient-combined')
s+=txt(70,460,'目标 1',32,'mint')+txt(690,455,'目标 2',32,'orange')+txt(495,560,'合成方向',34,'white','combined-note')
s+=txt(460,785,'示意方向；数值大 ≠ 梯度贡献大',34,'muted',anchor='middle')
V['multitask']=svg(s)
s=line(135,50,135,710,'line',5)
for i,(year,name,meaning,c) in enumerate([('1805','最小二乘','拟合观测','orange'),('1964','Huber','抵抗污染','mint'),('1986','反向传播代表论文','计算梯度','white'),('2017','Focal Loss','重视困难样本','orange'),('2021','CLIP','连接图像与文字','mint'),('2023','DPO','学习答案偏好','orange')]):
    y=50+i*114;s+=f'<g class="era">'+circle(135,y+25,13,c)+txt(180,y+32,year,46,c,'mono')+txt(380,y+32,name,41,'white')+txt(380,y+79,meaning,32,'muted')+'</g>'
s+=txt(460,785,'旧公式没有被集体淘汰',38,'mint',anchor='middle')
V['timeline']=svg(s)
s=txt(35,55,'Direct Preference Optimization · 2023',33,'muted')
s+=box(25,115,870,230,txt(65,180,'回答 A · 更受偏好',42,'mint')+txt(65,250,'有证据，承认不确定性',38)+txt(65,309,'✓  preferred',32,'mint','mono'),'preferred')
s+=box(25,380,870,230,txt(65,445,'回答 B · 较少偏好',42,'orange')+txt(65,515,'编造细节，掩盖不确定性',38)+txt(65,574,'×  dispreferred',32,'orange','mono'),'dispreferred')
s+=txt(460,691,'参考模型约束 + 成对偏好',44,'white','dpo-rule',anchor='middle')+txt(460,770,'示例偏好，不是自动真实性保证',34,'muted',anchor='middle')
V['dpo']=svg(s)
s=box(25,15,870,195,txt(65,75,'SigLIP 2 · 2025',49,'mint')+txt(65,134,'全局配对 + 局部定位 + 其他目标',37)+txt(65,180,'学习目标协同，训练配方也变化',32,'muted'),'research-card')
s+=txt(35,297,'旧策略生成的答案，如何加权？',40,'white')
for i,val in enumerate([.2,.5,.8,2.2,5]):
    x=65+i*172;s+=f'<rect x="{x}" y="{630-val*55}" width="90" height="{val*55}" rx="9" fill="#FFB56B" class="importance iw-{i}"/>'+txt(x+45,680,f'样本{i+1}',30,'muted',anchor='middle')
s+=txt(460,350,'VESPO · 2026',54,'mint','vespo-title',anchor='middle')+txt(460,745,'软重塑重要性权重',43,'mint','vespo-note',anchor='middle')+txt(460,792,'示意条形，不是论文实验或精确变换',29,'muted',anchor='middle')
V['frontier']=svg(s)
s=txt(460,100,'2026 / 09',74,'orange','mono',anchor='middle')+txt(460,175,'Centroid-Guided Contrastive Loss',38,'white',anchor='middle')
for i,(x,y) in enumerate([(170,355),(260,335),(200,440),(325,445),(265,510)]):s+=circle(x,y,17,'mint','cg-positive')
for i,(x,y) in enumerate([(580,335),(730,400),(660,505),(575,520)]):s+=circle(x,y,17,'orange','cg-negative')
s+=circle(265,425,8,'white','centroid')+line(190,520,350,520,'mint',2,'centroid-line')
s+=txt(460,620,'分类目标 + 表示空间推拉',44,'mint',anchor='middle')
s+=box(25,660,870,120,txt(65,711,'预印本 · EMSCAD 数据集',36,'orange')+txt(65,755,'关注消融、划分和跨数据集复现',32,'muted'),'evidence-tag')
V['newest']=svg(s)
s=''
for i,(n,t,sub) in enumerate([('01','究竟怕哪一种错？','需求决定扣分规则'),('02','数据是否可靠？','异常值、错标签与偏好偏差'),('03','分数代表真实效果吗？','用独立评估检验')]):
    y=50+i*228;s+=box(25,y,870,190,txt(65,y+90,n,54,'orange','mono')+txt(190,y+82,t,47,'white')+txt(190,y+145,sub,34,'muted'),'closing-question')
s+=txt(460,790,'损失定义方向，评估检验结果',39,'mint',anchor='middle')
V['close']=svg(s)
INSIGHTS={
'hook':('准确率：都答错','损失：还能看见错得有多离谱'),
'loop':('目标 → 梯度 → 更新','损失函数负责定义目标'),
'metric':('更细的反馈，更容易优化','分数下降仍需独立评估'),
'history':('先有测量误差，再有机器学习','损失函数没有统一的发明者'),
'mse':('大误差，会被平方放大','要不要重罚，取决于真实需求'),
'outlier':('换规则，就会换最佳答案','已用固定数据与网格搜索核验'),
'huber':('限制大残差的梯度影响','阈值随数据尺度调整'),
'ce':('分类评分，关注真实类别的概率','这里使用自然对数'),
'focal':('让容易样本少占话语权','这是损失权重，不是梯度比例'),
'smoothing':('改目标分布，缓和过度自信','不保证任何任务的校准都变好'),
'contrast':('配对关系，就是学习信号','正负样本的选择也会改变结果'),
'multitask':('权重 + 单位 + 梯度方向','多目标学习，需要明确取舍'),
'timeline':('每次变化，都回应一个新问题','关键论文与版本见配套文章'),
'dpo':('从成对回答直接学习偏好','偏好数据的偏差也会被学入'),
'frontier':('目标协同 / 序列加权 / 稳定性','阅读入口：SigLIP 2、GSPO、VESPO'),
'newest':('新，不自动等于更通用','首次公开 2026-09-18，v1'),
'close':('你怎么扣分，AI 就怎么学','完整推导、文献和实验见配套文章')}
scenes=[]
for i,s in enumerate(D['scenes']):
    a,b=INSIGHTS[s['id']]
    scenes.append(f'''<section id="{s['id']}" class="scene {'first' if i==0 else ''}" aria-label="{s['title']}">
    <div class="scene-content"><header><div class="eyebrow"><span class="number">{i+1:02}</span> / 17<span class="chapter">{s['chapter']}</span></div><h1>{s['title']}</h1></header>
    <div class="visual">{V[s['id']]}</div><div class="insight"><strong>{a}</strong><span>{b}</span></div></div></section>''')
cap_html=''.join(f'<div id="cap-{i}" class="caption"><span>{html.escape(c["text"])}</span></div>' for i,c in enumerate(D['captions']))
index='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>损失函数：你怎么扣分，AI 就怎么学</title><link rel="stylesheet" href="style.css"></head><body>
<div id="main" data-composition-id="main" data-start="0" data-duration="DURATION" data-width="1080" data-height="1920">
<div class="canvas-grid" data-layout-ignore></div><div class="rail" data-layout-ignore><div class="progress"></div></div>
SCENES<div class="captions">CAPTIONS</div><footer><span>MY DEEP LEARNING JOURNEY</span><span>原创图形 · AI 合成解说</span></footer>
<audio id="narration-audio" src="audio/narration.m4a" data-start="0" data-duration="DURATION" data-track-index="20"></audio>
<audio id="effects-audio" src="audio/effects.m4a" data-start="0" data-duration="DURATION" data-track-index="21"></audio>
</div><script src="assets/gsap.min.js"></script><script src="timeline-data.js"></script><script>ANIMATION</script></body></html>'''
index=index.replace('DURATION',str(D['duration'])).replace('SCENES','\n'.join(scenes)).replace('CAPTIONS',cap_html)
index=index.replace('ANIMATION',(B/'animation.js').read_text())
(B/'index.html').write_text(index)
(B/'timeline-data.js').write_text('window.LOSS_DATA = '+json.dumps(D,ensure_ascii=False,separators=(',',':'))+';\n')
print(f'Built {len(scenes)} scenes; duration {D["duration"]:.2f}s')
