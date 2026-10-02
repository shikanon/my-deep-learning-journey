"""Original vector artwork. Every reveal maps to spoken words, not slide timing."""
from html import escape
import math
INK='#46392F';RED='#ED826A';TEAL='#73A6A3';YELLOW='#EDCD74';PAPER='#FFFCF3'
def text(x,y,t,size=38,fill=INK,anchor='middle',weight=400):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}">{escape(t)}</text>'
def path(d,stroke=INK,width=4,fill='none',cls='draw'):
    return f'<path class="{cls}" d="{d}" stroke="{stroke}" stroke-width="{width}" fill="{fill}" stroke-linecap="round" stroke-linejoin="round"/>'
def rect(x,y,w,h,fill=PAPER):
    # Fixed little pencil imperfections; numeric axes and curves stay exact.
    d=f'M{x+20},{y} Q{x+w/2},{y-3} {x+w-18},{y+1} Q{x+w+2},{y+2} {x+w},{y+22} L{x+w-1},{y+h-20} Q{x+w+2},{y+h+2} {x+w-22},{y+h} L{x+18},{y+h+1} Q{x-3},{y+h} {x},{y+h-18} L{x+1},{y+18} Q{x-2},{y-2} {x+20},{y}'
    return path(d,INK,3.3,fill)+path(f'M{x+13},{y+h+8} Q{x+w/2},{y+h+11} {x+w-10},{y+h+7}',INK,1.2,cls='pencil')
def arrow(x1,y1,x2,y2,color=INK):
    a=math.atan2(y2-y1,x2-x1);ex=x2-15*math.cos(a);ey=y2-15*math.sin(a)
    return path(f'M{x1},{y1} Q{(x1+x2)/2+7},{(y1+y2)/2-5} {x2},{y2}',color,4)+path(f'M{ex+8*math.sin(a)},{ey-8*math.cos(a)} L{x2},{y2} L{ex-8*math.sin(a)},{ey+8*math.cos(a)}',color,4)
def bot(x,y,scale=1,color=RED,mood='smile',id=''):
    mouth='M42,67 Q55,79 69,66' if mood=='smile' else 'M43,72 Q55,60 69,71'
    return f'<g {"id="+chr(34)+id+chr(34) if id else ""} data-origin-x="{x}" data-origin-y="{y}" transform="translate({x} {y}) scale({scale})" class="mascot">'+path('M20,26 Q12,4 32,3 L83,4 Q106,4 107,25 L104,80 Q103,95 84,97 L28,95 Q9,94 10,76 Z',INK,3.3,color)+path('M59,3 L62,-20',INK,3)+f'<circle cx="62" cy="-24" r="7" fill="{YELLOW}" stroke="{INK}" stroke-width="2"/>'+f'<g class="eyes"><ellipse cx="37" cy="40" rx="7" ry="10" fill="{INK}"/><ellipse cx="78" cy="40" rx="7" ry="10" fill="{INK}"/><circle cx="39" cy="37" r="2.2" fill="white"/><circle cx="80" cy="37" r="2.2" fill="white"/></g>'+path(mouth,INK,2.5,cls='pencil')+f'<ellipse cx="26" cy="61" rx="8" ry="4" fill="#F5B8A0"/><ellipse cx="88" cy="61" rx="8" ry="4" fill="#F5B8A0"/>'+path('M10,53 Q-3,47 -8,65 M106,56 Q119,46 125,63 M34,97 L32,109 L20,110 M81,96 L85,110 L98,109',INK,3,cls='pencil')+'</g>'
def cat(x,y,scale=1,color=YELLOW):
    return f'<g class="mascot-cat" data-origin-x="{x}" data-origin-y="{y}" transform="translate({x} {y}) scale({scale})">'+path('M13,31 L9,0 L35,16 Q56,5 75,16 L98,1 L95,33 Q109,75 84,92 Q51,112 20,90 Q1,76 13,31 Z',INK,3,color)+f'<circle cx="36" cy="49" r="4" fill="{INK}"/><circle cx="73" cy="49" r="4" fill="{INK}"/>'+path('M52,63 L57,67 L62,61 M57,67 Q47,77 42,70 M57,67 Q66,76 73,69 M22,61 L-1,57 M24,72 L0,77 M84,60 L110,54 M84,72 L111,78',INK,2.5,cls='pencil')+'</g>'
def card(x,y,w,h,title,sub='',color=PAPER):
    return rect(x,y,w,h,color)+text(x+w/2,y+62,title,42,weight=600)+(text(x+w/2,y+h-30,sub,30) if sub else '')
def stars(x,y,color=YELLOW):
    return ''.join(path(f'M{x+dx},{y+dy-12} L{x+dx},{y+dy+12} M{x+dx-12},{y+dy} L{x+dx+12},{y+dy}',color,4) for dx,dy in [(0,0),(48,33),(-42,55)])
def axes(x=110,y=740,w=650,h=490,xlabel='误差 e',ylabel='扣分'):
    return arrow(x,y,x+w+35,y)+arrow(x,y,x,y-h-35)+text(x+w-15,y+65,xlabel,32)+text(x+45,y-h-22,ylabel,32)
def curve(fn,x0=-3,x1=3,maxy=9,x=110,y=740,w=650,h=490):
    pts=[]
    for i in range(121):
        e=x0+(x1-x0)*i/120;v=fn(e);pts.append((x+i*w/120,y-v/maxy*h))
    return 'M'+' L'.join(f'{a:.2f},{b:.2f}' for a,b in pts)
def g(cue,content,action='',id=''):
    return f'<g class="beat" data-cue="{escape(cue)}" data-action="{action}" {"id="+chr(34)+id+chr(34) if id else ""}>{content}</g>'
def artwork(kind):
    if kind=='hook':
        return g('让小机器人',bot(110,355,1.8)+text(225,640,'豆豆',36), 'hop')+g('它猜二十一度',card(375,95,370,145,'预测 21°C','机器人猜测',YELLOW))+g('实际二十度',card(375,285,370,145,'实际 20°C','温度计测量',TEAL))+g('只告诉它错了',path('M400,495 L470,565 M470,495 L400,565',RED,12)+text(600,550,'只知道“错了”',36))+g('我们得给它一把尺',rect(365,660,410,85,YELLOW)+''.join(path(f'M{385+i*35},665 L{385+i*35},{695 if i%2 else 715}',INK,2) for i in range(11)), 'ruler')+g('告诉它差多少',text(535,810,'差 1°C → 扣几分？',46,weight=600)+arrow(480,455,535,650,TEAL))
    if kind=='cancel':
        telescope=path('M170,160 L340,80 L370,145 L199,224 Z',INK,4,TEAL)+path('M255,200 L215,365 M255,200 L315,365 M215,330 L305,330',INK,4)+stars(670,140)
        return g('比人工智能古老',telescope+text(510,280,'很久以前的天体测量',37))+g('有人多报三',card(105,445,300,140,'+3','高估',RED),'left-to-center')+g('有人少报三',card(510,445,300,140,'−3','低估',TEAL),'right-to-center')+g('直接相加',text(455,635,'(+3) + (−3) = 0',48,weight=600),'underline')+g('却不代表测准了',bot(345,710,1.4,mood='sad')+text(595,775,'抵消 ≠ 准确',40,weight=600)+path('M575,803 Q682,791 794,802',RED,7))
    if kind=='square':
        cells=lambda x,y:''.join(rect(x+j*66,y+i*66,58,58,RED if x<400 else TEAL) for i in range(3) for j in range(3))
        return g('一八零五年',card(110,60,700,145,'1805 · Legendre','公开发表最小二乘法'))+g('把误差平方',cells(165,310)+cells(535,310)+text(259,570,'(+3)² = 9',42)+text(630,570,'(−3)² = 9',42),'cells')+g('再相加',text(452,652,'9 + 9 = 18',60,weight=600),'sum')+g('正负就不会抵消',path('M200,700 Q450,735 710,700',TEAL,8)+text(455,770,'误差 → 非负代价',42))+g('高斯后来',text(455,850,'1809 · Gauss：连接概率模型',32))
    if kind=='accuracy':
        return g('再看认猫',cat(395,70,1.3)+text(455,255,'真实答案：猫',38))+g('百分之四十九',card(85,325,330,215,'A · 猫 49%','狗 51% → 判狗',YELLOW))+g('百分之一',card(505,325,330,215,'B · 猫 1%','狗 99% → 判狗',RED))+g('都可能判错',text(455,640,'准确率：两台都错',47,weight=600)+path('M115,665 L795,664',INK,3))+g('更自信',arrow(455,720,715,720,RED)+text(455,790,'B 更狠地排除了正确答案',35))+g('更细的反馈',rect(165,830,580,60,TEAL)+text(455,872,'概率评分能看到细微改善',32))
    if kind=='loop':
        return g('记住三位伙伴',bot(110,75,1.1)+text(535,152,'从预测开始',42))+g('损失负责评分',card(235,295,450,120,'① 损失：评分',color=RED)+arrow(455,200,455,280)) +g('反向传播',card(235,470,450,120,'② 反向传播：求导',color=YELLOW)+arrow(455,425,455,455)) +g('优化器负责',card(235,645,450,120,'③ 优化器：更新',color=TEAL)+arrow(455,600,455,630)) +g('真实效果',text(455,855,'训练评分之外，还要独立考试',36)+path('M720,690 C850,685 860,90 340,120',TEAL,4),'flow')
    if kind=='curves':
        return g('大错该多扣多少',axes()+text(455,95,'误差 1 → 3',50,weight=600))+g('均方误差',path(curve(lambda e:e*e),RED,7)+text(270,195,'平方：1 → 9',43,INK), 'trace')+g('平均绝对误差',path(curve(abs),TEAL,7)+text(665,195,'绝对值：1 → 3',40,INK),'trace')+g('追赶大偏差',text(455,853,'越远离零点，平方惩罚越强',37)+bot(410,585,.8),'follow-curve')
    if kind=='outlier':
        balls=''.join(f'<g class="sample">'+f'<circle cx="{140+i*155}" cy="170" r="48" stroke="{INK}" stroke-width="3" fill="{RED if i==4 else YELLOW}"/>'+text(140+i*155,184,str(v),42)+'</g>' for i,v in enumerate([1,2,3,4,20]))
        ruler=path('M140,640 L770,640',INK,4)+''.join(path(f'M{x},630 L{x},655',INK,3)+text(x,698,label,30) for x,label in [(140,'0'),(455,'10'),(770,'20')])+f'<circle id="mean-marker" cx="218.75" cy="640" r="14" fill="{RED}" stroke="{INK}" stroke-width="3"/>'+text(455,755,'加入 20，平均数从 2.5 → 6',32)
        return g('同样的一',balls,'samples')+g('只能猜一个数',text(455,285,'同一数据，同一常数模型',36)+ruler)+g('平方规则选平均数六',card(100,370,315,195,'MSE → 6','平均数',RED)+text(258,490,'(1+2+3+4+20)/5',27),'pull-mean')+g('绝对值规则选中位数三',card(495,370,315,195,'MAE → 3','中位数',TEAL)+text(653,490,'排序后的中间值',30)+f'<circle cx="234.5" cy="640" r="10" fill="{TEAL}" stroke="{INK}" stroke-width="3"/>')+g('最好的答案也变了',bot(410,790,.7)+text(455,935,'换评分 → 换最优答案',40,weight=600))
    if kind=='huber':
        delta=1
        return g('一九六四年',text(455,75,'1964 · Peter J. Huber',40)+axes()+text(455,160,'污染数据，也要可靠',36))+g('小误差用平方',path(curve(lambda e:.5*e*e,maxy=4.5),RED,3,cls='draw ghost')+text(455,255,'小误差：½e²',40),'trace')+g('大误差改成直线',path(curve(lambda e:.5*e*e if abs(e)<=1 else abs(e)-.5,maxy=4.5),TEAL,8)+text(455,825,'大误差：δ(|e| − ½δ)',37),'trace')+g('导数不再越长越大',rect(650,290,135,80,YELLOW)+text(717,345,'限速',38)+bot(525,470,.8),'brake')+g('阈值决定',path('M327,740 L327,560 M543,740 L543,560',INK,3)+text(327,787,'−δ',32)+text(543,787,'δ',32))
    if kind=='ce':
        data=[(.9,.105,TEAL),(.5,.693,YELLOW),(.01,4.605,RED)]
        out=g('交叉熵',text(455,80,'真实类别概率 p → −ln p',46,weight=600))
        for i,(p,l,col) in enumerate(data):
            cue=['百分之九十','扣分约零点一','百分之一'][i]
            if i==1:cue='扣分约零点一'
            out+=g(cue,rect(95,180+i*200,720,165,PAPER)+cat(130,220+i*200,.65,col)+text(350,240+i*200,('90%' if i==0 else '50%' if i==1 else '1%'),46)+arrow(448,230+i*200,540,230+i*200)+text(680,247+i*200,f'{l:.3f}',56)+f'<path class="loss-bar" d="M280,{300+i*200} L{280+max(20,l/4.605*470)},{300+i*200}" stroke="{col}" stroke-width="24" stroke-linecap="round"/>','bar')
        return out+g('排除得太狠',text(455,865,'正确答案越不可能，扣分越大',36)+stars(745,830))
    if kind=='focal':
        easy=''.join(bot(95+(i%5)*115,145+(i//5)*118,.66,TEAL) for i in range(15))
        return g('海量容易背景',easy+text(338,565,'海量容易背景',39),'crowd')+g('困难目标',cat(685,245,1.1,RED)+text(745,470,'困难目标',33))+g('乘一个小权重',text(455,690,'Focal = CE × (1−p)ᵞ',42,weight=600)+rect(100,765,315,110,TEAL)+text(258,833,'p=.99 → .0001',32)+rect(505,765,315,110,RED)+text(662,833,'p=.2 → .64',32),'volume')+g('调低音量',path('M580,550 L635,525 L635,595 L580,570 Z',INK,3,YELLOW)+path('M650,535 Q680,557 650,580',INK,3), 'easy-down')+g('错标签',text(455,935,'难样本也可能是噪声',31))
    if kind=='smooth':
        return g('标签平滑',cat(390,60,1.2)+text(455,265,'三个类别的目标概率',38))+g('非黑即白',card(100,340,710,155,'原来： [1, 0, 0]','把全部概率放给猫',YELLOW))+g('留一点概率',arrow(455,530,455,595)+card(100,625,710,160,'平滑： [.933, .033, .033]','ε=.1，均匀混合',TEAL),'split-prob')+g('不保证',text(455,865,'少一点绝对；独立评估收益',36))
    if kind=='contrast':
        return g('谁和谁匹配',text(455,80,'从“答案”到“关系”',45,weight=600)+cat(340,390,1.0,YELLOW))+g('两种视图拉近',cat(110,220,.85,YELLOW)+path('M224,301 Q290,293 340,420',TEAL,5)+text(235,177,'正样本',37),'pull-positive')+g('不匹配的推开',bot(685,600,.9,TEAL)+path('M450,500 Q565,557 685,650',RED,5)+text(690,555,'负样本',37),'push-negative')+g('早期样本对',text(455,775,'2006 → 2018 → 2021',35)+text(455,835,'样本对 → InfoNCE → CLIP',38))+g('扩展到了关系',rect(210,890,490,70,TEAL)+text(455,938,'监督还可以来自配对',32))
    if kind=='dpo':
        return g('二零二三年',text(455,80,'2023 · DPO',46,weight=600)+bot(140,215,1.1))+g('更喜欢哪条回答',card(340,160,475,185,'回答 A：更喜欢','同一个问题',TEAL)+card(340,410,475,185,'回答 B：较不喜欢','组成一个偏好对',RED))+g('相对参考模型',rect(125,675,675,135,YELLOW)+text(460,730,'当前模型 ÷ 参考模型',42)+text(460,777,'比较 A、B 的相对概率变化',31),'relative')+g('不只是无限奖励',text(455,900,'偏好有噪声，参考模型有影响',36))
    if kind=='siglip':
        return g('三条研究线',text(455,80,'2025 · SigLIP 2',45,weight=600))+g('配对评分',rect(100,175,300,300,PAPER)+cat(190,255,1.25)+card(500,200,310,150,'一只小猫','图文配对',YELLOW)+arrow(410,290,485,290,TEAL))+g('局部学习',path('M175,235 L175,230 L315,230 L315,405 L175,405 L175,390',RED,5)+card(505,410,305,160,'猫的脸在哪里','描述与定位',RED),'zoom-local')+g('自蒸馏',bot(130,635,.9,TEAL)+bot(555,635,.9,YELLOW)+arrow(260,670,535,670,TEAL)+text(210,800,'全局老师',33)+text(635,800,'局部学生',33),'teach')+g('训练配方',text(455,920,'多个目标 + 数据 + 训练配方',34))
    if kind=='sequence':
        tiles=''.join(rect(90+i*118,220,105,125,YELLOW)+text(143+i*118,293,t,34) for i,t in enumerate(['这','道','题','的','答','案']))
        return g('整段回答怎么评分',text(455,80,'逐词更新？整段更新？',43,weight=600)+tiles,'tokens')+g('序列策略优化',path('M80,375 L80,395 L820,395 L820,375',TEAL,6)+text(455,470,'GSPO · 2025：序列层面',39),'bracket')+g('二零二六年',card(120,580,665,170,'VESPO · 2026','旧策略数据 → 新策略更新',TEAL),'old-data')+g('旧数据的权重',path('M195,815 L340,755 L470,850 L610,770 L740,810',RED,5)+path('M195,815 Q455,765 740,810',TEAL,7)+text(455,920,'软重塑权重，减少不稳定',35),'soften')
    if kind=='ending':
        return g('训练分数',text(455,75,'一个更低的 loss',47,weight=600)+card(95,170,325,165,'训练分数 ↓','改善了代理目标',YELLOW)+card(505,170,315,165,'任务成功？','还要独立检查',TEAL))+g('修复哪种失败',rect(145,435,620,85,PAPER)+text(455,490,'① 修复哪种失败？',42))+g('独立评测和消融',rect(145,565,620,85,PAPER)+text(455,620,'② 独立评测与消融？',40))+g('一种取舍',bot(125,745,1.1)+text(585,815,'你怎么扣分',54,weight=600)+text(585,885,'模型就朝哪里学',43)+stars(780,700),'celebrate')
    raise ValueError(kind)

INSIGHTS={
'hook':('先把“错了”变成可比较的代价','温度例子只展示评分；更新方向还需求导'),
'cancel':('正负抵消，不等于没有错误','先定义误差的代价，再谈谁拟合得更好'),
'square':('平方，让正负误差都留下痕迹','历史节点：1805 公开发表；1809 概率联系'),
'accuracy':('对错之外，还要看给真实答案多少概率','两台都判错，学习信号却不应一样'),
'loop':('评分 → 求导 → 更新 → 再预测','独立评估检查训练之外的真实效果'),
'curves':('不同规则，表达不同的大错代价','MSE / MAE 为对应单样本损失的平均'),
'outlier':('相同数据，换规则就可能换答案','20 是噪声还是重要事件，要由任务判断'),
'huber':('Huber 控制的是大残差的导数','阈值与目标单位有关；不解决所有异常'),
'ce':('交叉熵 = 真实类别概率的负对数','图中数值使用自然对数'),
'focal':('会的题小声说，难的题被听见','示例 α=1、γ=2；乘法权重并非梯度比例'),
'smooth':('改变目标分布，也能改变学习压力','这里采用包含真实类别的均匀平滑约定'),
'contrast':('匹配者靠近，不匹配者远离','二维示意；假负例仍会影响表示'),
'dpo':('把偏好写进相对参考模型的目标','Rafailov 等，2023；取决于偏好模型假设'),
'siglip':('全局配对，局部学习，多种目标互补','Tschannen 等，2025；模型收益来自整体配方'),
'sequence':('重新思考评分与更新的单位','Zheng 等，2025；Shen 等，2026'),
'ending':('损失函数，是一套可以检验的取舍','研究核验截至 2026-10-02；原文与阅读范围见文章')}
