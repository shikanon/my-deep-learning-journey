#!/usr/bin/env python3
"""Original SVG explanations. Coordinates for curves come from the stated formulas."""
import math
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / 'assets'
BG, PANEL, FG, MUTED, LINE = '#101F24', '#182F35', '#F3EDE1', '#B8CCC9', '#34545B'
GREEN, ORANGE, RED = '#A5E1C8', '#FFB56B', '#FF8B86'


def text(x, y, s, size=24, color=FG, weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(s)}</text>'


def rect(x, y, w, h, fill=PANEL, radius=18, stroke=LINE):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def line(x1,y1,x2,y2,color=LINE,width=2,dash=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'


def circle(x,y,r=7,color=GREEN):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'


def path(points,color=GREEN,width=4):
    d='M '+' L '.join(f'{x:.2f},{y:.2f}' for x,y in points)
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>'


def save(name,title,body,h=650):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{h}" viewBox="0 0 1200 {h}" role="img" aria-label="{escape(title)}"><title>{escape(title)}</title><rect width="1200" height="{h}" rx="24" fill="{BG}"/><g font-family="PingFang SC, Microsoft YaHei, system-ui, sans-serif">'+text(48,70,title,34,FG,700)+body+'</g></svg>\n'
    (OUT/name).write_text(svg,encoding='utf-8')


def axes(x,y,w,h,xmax,ymax,xticks,yticks,xmin=0):
    body=''
    for v in yticks:
        yy=y+h-v/ymax*h
        body+=line(x,yy,x+w,yy)+text(x-16,yy+8,str(v),20,MUTED,anchor='end')
    body+=line(x,y,x,y+h,MUTED)+line(x,y+h,x+w,y+h,MUTED)
    for v in xticks:
        xx=x+(v-xmin)/(xmax-xmin)*w
        body+=text(xx,y+h+32,str(v),20,MUTED,anchor='middle')
    return body


def main():
    OUT.mkdir(exist_ok=True)
    b=text(48,112,'损失定义扣分规则；梯度描述局部变化；优化器执行更新。',24,MUTED)
    for i,(n,sub,color) in enumerate([('模型预测','根据输入，输出数字或概率',GREEN),('损失函数','比较预测与目标，计算损失',ORANGE),('反向传播','沿计算图求参数梯度',GREEN),('优化器','根据梯度与状态更新参数',GREEN)]):
        x=48+i*288
        b+=rect(x,198,256,178)+text(x+22,249,f'0{i+1}',23,color,700)+text(x+22,298,n,32,FG,700)
        # Two lines keep labels readable.
        b+=text(x+22,339,sub[:9],20,MUTED)+text(x+22,365,sub[9:],20,MUTED)
        if i<3:
            b+=line(x+260,289,x+280,289,MUTED,3)+path([(x+274,282),(x+281,289),(x+274,296)],MUTED,3)
    b+=path([(1060,410),(1060,465),(170,465),(170,410)],GREEN,3)+text(600,507,'下一轮：用更新后的参数再作答',25,GREEN,anchor='middle')
    b+=rect(48,548,1104,60)+text(70,588,'独立验证集上的指标与真实任务效果，用来检查这套评分规则是否合适。',23,FG)
    save('training-loop.svg','AI 训练：四个角色，四种工作',b,650)

    b=text(48,113,'单样本误差 e 的三种罚分方式；δ = 1。纵轴保留真实数值。',24,MUTED)
    b+=axes(100,168,760,362,3,9,[-3,-2,-1,0,1,2,3],[0,3,6,9],-3)
    funcs=[(lambda e:e*e,ORANGE,'平方误差 e²',190),(lambda e:abs(e),GREEN,'绝对误差 |e|',255),(lambda e:.5*e*e if abs(e)<=1 else abs(e)-.5,RED,'Huber(e)，δ = 1',320)]
    for fn,color,label,yy in funcs:
        b+=path([(100+(e+3)/6*760,530-fn(e)/9*362) for e in [i*0.02 for i in range(-150,151)]],color)
        b+=line(905,yy-8,949,yy-8,color,4)+text(964,yy,label,21,color)
    b+=text(500,589,'误差 e（预测 − 真实值）',24,MUTED,anchor='middle')+text(100,146,'损失',22,MUTED)
    b+=text(902,400,'大误差：',25,FG,700)+text(902,436,'平方增长更快',22,ORANGE)+text(902,472,'Huber 转为线性',22,RED)
    b+=text(48,638,'曲线的高度是损失；曲线的斜率影响梯度。它们是不同的量。',22,MUTED)
    save('loss-curves.svg','错误有多大？不同规则，罚分不同',b,685)

    ys=[1,2,3,4,20]
    b=text(48,114,'所有输入都预测同一个数 c；数据为 [1, 2, 3, 4, 20]。',24,MUTED)
    for x,v in zip([135,310,485,660,1050],ys):
        b+=circle(x,176,24,ORANGE if v==20 else GREEN)+text(x,186,str(v),25,BG,700,anchor='middle')
    for j,(title,fn,best,color,maxy) in enumerate([('MSE：最小值在平均数 6',lambda c:sum((c-y)**2 for y in ys)/5,6,ORANGE,140),('MAE：最小值在中位数 3',lambda c:sum(abs(c-y) for y in ys)/5,3,GREEN,10)]):
        x=90+j*585
        b+=text(x,256,title,26,color,700)+axes(x,291,454,215,12,maxy,[0,3,6,9,12],[0,int(maxy/2),maxy])
        b+=path([(x+c/12*454,506-fn(c)/maxy*215) for c in [i/20 for i in range(241)]],color)
        b+=line(x+best/12*454,291,x+best/12*454,506,color,2,'5 7')+circle(x+best/12*454,506-fn(best)/maxy*215,9,color)
    b+=text(600,592,'异常值不是一定要忽略；先判断它是错误记录，还是你真正关心的罕见事件。',22,MUTED,anchor='middle')
    save('outlier-minima.svg','只换损失，最佳答案就从 6 变成 3',b,630)

    b=text(48,115,'p 是模型给真实类别的概率；使用自然对数 L = −ln(p)。',24,MUTED)
    b+=axes(105,175,692,345,1,5,[0,0.25,0.5,0.75,1],[0,1,2,3,4,5])
    b+=path([(105+p*692,520+math.log(p)/5*345) for p in [0.01+i*.005 for i in range(199)]],GREEN)
    for p in [.9,.5,.01]:
        b+=circle(105+p*692,520+math.log(p)/5*345,8,ORANGE)
    for i,(p,label) in enumerate([(.9,'比较有把握'),(.5,'拿不准'),(.01,'几乎排除了真实类别')]):
        yy=228+i*118
        b+=text(858,yy,f'p = {p:.2f}',26,MUTED)+text(858,yy+43,f'L = {-math.log(p):.3f}',34,ORANGE,700)+text(858,yy+78,label,21,MUTED)
    b+=text(450,575,'给真实类别的概率 p',24,MUTED,anchor='middle')
    b+=text(48,624,'比“答对 / 答错”更细，但模型可能依然过拟合或学到错误标签。',23,MUTED)
    save('cross-entropy.svg','交叉熵：越自信地错，罚得越重',b,660)

    b=text(48,115,'L = −αₜ (1 − pₜ)ᵞ ln(pₜ)；这里 αₜ = 1，γ = 2。',25,MUTED)
    for j,(name,p,color) in enumerate([('容易样本',.99,GREEN),('困难样本',.2,ORANGE)]):
        x=48+j*575
        b+=rect(x,158,530,340)+text(x+28,211,name,29,color,700)+text(x+28,266,f'pₜ = {p}',32,FG)
        b+=text(x+28,323,f'乘法权重 = {(1-p)**2:.4f}',30,color,700)+text(x+28,370,f'交叉熵 = {-math.log(p):.5f}',24,MUTED)
        b+=text(x+28,425,f'Focal loss = {-(1-p)**2*math.log(p):.6f}',27,color,700)
        b+=line(x+28,457,x+490,457,LINE,12)+line(x+28,457,x+28+462*(1-p)**2,457,color,12)
    b+=text(48,552,'让容易样本“调低音量”，把注意力留给还没学会的例子。',27,FG,700)
    b+=text(48,597,'这不是梯度按同一比例缩放；动态权重本身也随预测变化。',23,MUTED)
    b+=text(48,635,'难样本中若混入大量错标签，聚焦它们可能放大噪声。',23,MUTED)
    save('focal-weighting.svg','Focal Loss：简单样本别淹没难题',b,675)

    b=text(48,114,'原创二维示意，不是实测嵌入；颜色表示应匹配的样本关系。',23,MUTED)
    for j,label in enumerate(['训练前：关系混杂','训练后：匹配靠近']):
        x=48+j*576
        b+=rect(x,163,528,350)+text(x+28,212,label,28,FG,700)
        pts=[(100,112,GREEN),(358,210,GREEN),(180,255,ORANGE),(285,80,ORANGE)] if j==0 else [(155,148,GREEN),(188,170,GREEN),(369,248,ORANGE),(397,225,ORANGE)]
        for k,(px,py,c) in enumerate(pts):
            b+=circle(x+px,200+py,24,c)+text(x+px,209+py,'猫' if c==GREEN else '车',21,BG,700,anchor='middle')
    b+=text(48,565,'核心：奖励匹配关系，而不只是逐个预测类别。',27,GREEN,700)
    b+=text(48,607,'关系怎么定义、温度参数怎么设、负样本是不是“假负例”，都影响结果。',23,MUTED)
    save('contrastive.svg','对比学习：让关系成为学习信号',b,650)

    b=text(48,114,'这是问题驱动的知识地图；各分支并存，不是后者全面替代前者。',24,MUTED)
    nodes=[('1805 / 1809','Legendre / Gauss','把观测误差合并',GREEN),('1964','Peter J. Huber','控制异常值的影响',ORANGE),('1986','Rumelhart 等','损失驱动多层网络学习',GREEN),('2015 / 2017','标签平滑 / Focal','控制自信与样本权重',ORANGE),('2018–2021','InfoNCE / SimCLR / CLIP','学习视图和跨模态关系',GREEN),('2023–2026','DPO / GSPO / VESPO','偏好与策略更新的目标',ORANGE)]
    for i,(year,name,desc,color) in enumerate(nodes):
        yy=179+i*101
        b+=circle(80,yy+8,9,color)
        if i<5:b+=line(80,yy+20,80,yy+95,LINE,3)
        b+=text(118,yy+16,year,27,color,700)+text(345,yy+12,name,26,FG,700)+text(345,yy+49,desc,22,MUTED)
    b+=text(48,836,'最近检索：2026-10-02。论文版本、证据和开放问题见正文。',23,MUTED)
    save('history-map.svg','损失函数的演进：我们逐渐改变“什么算好”',b,880)


if __name__=='__main__': main()
