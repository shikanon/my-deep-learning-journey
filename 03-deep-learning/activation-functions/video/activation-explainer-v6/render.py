#!/usr/bin/env python3
"""Editable 1080x1920 hand-drawn explainer. Every frame is a pure function of its index."""
import argparse
import bisect
import hashlib
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw
from runtime import BASE, ffmpeg, font
import motion

D = json.loads((BASE/'timeline.json').read_text())
W,H,FPS = D['width'],D['height'],D['fps']
PAPER='#fff7e6'; INK='#44382e'; TEAL='#246e65'; CORAL='#ae4937'; GOLD='#c59843'; GRID='#e7dac0'
M = json.loads((BASE/'assets/author-animation/manifest.json').read_text())
B = json.loads((BASE/'assets/doctor-pointer/manifest.json').read_text())
TEXT_LOG=[]; LOG_TEXT=False

def smooth(p):
    p=max(0,min(1,p));return p*p*(3-2*p)

def cue(s,k,t,span=.8):
    return smooth((t-s['beats'][k]['start'])/span)

def txt(draw,x,y,text,size=40,color=INK,center=False,max_width=None):
    if max_width:
        while size>25 and draw.textbbox((0,0),text,font=font(size))[2]>max_width:size-=1
    bounds=draw.textbbox((0,0),text,font=font(size))
    if center:x-=bounds[2]/2
    draw.text((int(x),int(y)),text,font=font(size),fill=color,anchor='lt')
    if LOG_TEXT:
        b=draw.textbbox((int(x),int(y)),text,font=font(size),anchor='lt')
        TEXT_LOG.append({'text':text,'size':size,'box':b,'color':color})

def wrap(draw,text,size,width):
    result=[]
    for paragraph in text.split('\n'):
        current=''
        for char in paragraph:
            if current and draw.textlength(current+char,font=font(size))>width:
                result.append(current);current=char
            else:current+=char
        if current:result.append(current)
    return result

def lines(draw,x,y,text,size=40,width=800,gap=12,color=INK,center=False):
    ls=wrap(draw,text,size,width)
    for i,value in enumerate(ls):txt(draw,x,y+i*(size+gap),value,size,color,center)
    return len(ls)*(size+gap)

def card(draw,box,fill=PAPER,radius=24,width=3):
    draw.rounded_rectangle(box,radius=radius,fill=fill,outline=INK,width=width)

def arrow(draw,start,end,color=INK,width=5):
    draw.line([start,end],fill=color,width=width)
    angle=math.atan2(end[1]-start[1],end[0]-start[0]);length=15+width
    wing1=(end[0]-length*math.cos(angle-.5),end[1]-length*math.sin(angle-.5))
    wing2=(end[0]-length*math.cos(angle+.5),end[1]-length*math.sin(angle+.5))
    draw.polygon([end,wing1,wing2],fill=color)

def dashed(draw,a,b,color=INK,width=3,dash=12):
    dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    for start in range(0,int(length),dash*2):
        u,v=start/length,min(start+dash,length)/length
        draw.line([(a[0]+dx*u,a[1]+dy*u),(a[0]+dx*v,a[1]+dy*v)],fill=color,width=width)

def badge(draw,x,y,value,fill='#e0ede3',width=180,size=36):
    card(draw,(x,y,x+width,y+68),fill,radius=16,width=2)
    txt(draw,x+width/2,y+17,value,size,center=True,max_width=width-20)

def chart(draw,box=(175,610,870,1000),xrange=(-3,3),yrange=(-1,3.3),ticks=True):
    x0,y0,x1,y1=box
    def X(x):return x0+(x-xrange[0])/(xrange[1]-xrange[0])*(x1-x0)
    def Y(y):return y1-(y-yrange[0])/(yrange[1]-yrange[0])*(y1-y0)
    for v in [xrange[0],0,xrange[1]]:
        draw.line([(X(v),y0),(X(v),y1)],fill=GRID,width=2)
        if ticks:txt(draw,X(v),y1+15,f'{v:g}',32,center=True)
    for v in [yrange[0],0,yrange[1]]:
        draw.line([(x0,Y(v)),(x1,Y(v))],fill=GRID,width=2)
        if ticks:txt(draw,x0-25,Y(v)-13,f'{v:g}',29,center=True)
    if yrange[0]<=0<=yrange[1]:arrow(draw,(x0,Y(0)),(x1+12,Y(0)),width=3)
    if xrange[0]<=0<=xrange[1]:arrow(draw,(X(0),y1),(X(0),y0-10),width=3)
    return X,Y

def curve(draw,fn,X,Y,xrange=(-3,3),color=TEAL,width=7,reveal=1):
    count=240
    points=[(X(xrange[0]+i/count*(xrange[1]-xrange[0])),Y(fn(xrange[0]+i/count*(xrange[1]-xrange[0])))) for i in range(max(2,int(count*reveal))+1)]
    draw.line(points,fill=color,width=width,joint='curve')

def dot(draw,x,y,r=18,fill=TEAL):
    draw.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=INK,width=3)

def sigmoid(x):return 1/(1+math.exp(-x))
def gelu(x):return x*(1+math.erf(x/math.sqrt(2)))/2
def silu(x):return x*sigmoid(x)

@lru_cache(maxsize=32)
def background(index):
    s=D['scenes'][index];im=Image.new('RGB',(W,H),PAPER);dr=ImageDraw.Draw(im)
    # Deterministic pencil-like margin marks, clear of all teaching content.
    for y in range(195,1770,68):
        dr.line([(28,y),(38,y+9),(28,y+17)],fill=GRID,width=2)
    for k in range(8):dr.line([(1003,260+k*9),(1035,241+k*9)],fill='#ead4be',width=3)
    chapter=next((c for c in D['chapters'] if c['id']==s['chapter']),None)
    label=chapter['title'] if chapter else '一起学习'
    txt(dr,65,212,f'{index+1:02} / {len(D["scenes"]):02}   {label}',34,TEAL)
    card(dr,(64,470,954,1138),fill='#fffcf1',radius=30,width=4)
    dr.line([(112,487),(255,487)],fill=GOLD,width=6)
    # The full doctoral pointer has a dedicated lane; its sweep never crosses text.
    pointer=s['actor']=='doctor-pointer'
    left=550 if pointer else 375
    text_left=left+24
    text_width=954-text_left-25
    card(dr,(left,1202,954,1518),fill='#e1eee5',radius=25,width=3)
    # Provenance is concise on screen; full bibliography lives in the article.
    if s['kind']!='hook':lines(dr,82,1089,s['source'],size=26,width=850,gap=3,color=INK)
    txt(dr,65,1789,'我的深度学习之路',39)
    # Right label uses its own safe lane, left of the reserved platform edge.
    txt(dr,820,1794,'激活函数',30,TEAL)
    return im

def illustration(im,s,t):
    dr=ImageDraw.Draw(im)
    kind=s['kind'];p=[cue(s,i,t) for i in range(len(s['beats']))];local=t-s['start']
    if kind=='hook':
        q=motion.hook_state(s,t)
        if q['network']>0:
            layer=Image.new('RGB',(W,H),'#fffcf1');ld=ImageDraw.Draw(layer)
            # Draw the network into a copy of the board, then reveal it as the
            # narrator says "if each layer". The dots are signal-flow cues.
            labels=q['layer_labels'];xs=[156+i*684/(len(labels)-1) for i in range(len(labels))]
            nodes=[[(x,y) for y in ([721,761] if i in [0,len(labels)-1] else [671,711,751,791])]
                   for i,x in enumerate(xs)]
            txt(ld,509,516,'每层只做加权求和',38,TEAL,center=True)
            txt(ld,509,571,f"{q['depth']} 层" if q['depth']<128 else '堆到 128 层',54,CORAL,center=True)
            for a,b in zip(nodes,nodes[1:]):
                for u in a:
                    for v in b:ld.line([u,v],fill='#c4d5bf',width=2)
                u=a[int(local*.65)%len(a)];v=b[int(local*.8)%len(b)];phase=q['flow']
                dot(ld,u[0]+(v[0]-u[0])*phase,u[1]+(v[1]-u[1])*phase,6,GOLD)
            for i,row in enumerate(nodes):
                for x,y in row:dot(ld,x,y,15,TEAL if i<len(nodes)-1 else CORAL)
                txt(ld,xs[i],823,labels[i],25,TEAL,center=True)
            # Only the known network pixels are composited; paper outside the
            # whiteboard and the narrator's cards stay unchanged.
            crop=layer.crop((112,505,901,854))
            paper=Image.new('RGB',crop.size,'#fffcf1')
            im.paste(Image.blend(paper,crop,q['network']),(112,505))
        if q['points']>0:
            data=motion.xor_values(local);X=lambda v:317+377*v;Y=lambda v:1038-137*v
            rect=[(-.1,-.1),(1.1,-.1),(1.1,1.1),(-.1,1.1)]
            poly=motion.clipped_half_plane(rect,data['W'],data['b'])
            if len(poly)>2:dr.polygon([(X(x),Y(y)) for x,y in poly],fill='#e1eee5')
            segment=motion.boundary_segment(data['W'],data['b'],(-.1,-.1,1.1,1.1))
            if len(segment)==2:dr.line([(X(x),Y(y)) for x,y in segment],fill=INK,width=4)
            for point in data['points']:
                x,y=point['x'];col=TEAL if point['target'] else CORAL
                if point['wrong']:
                    r=27+2*math.sin(local*3);dr.ellipse((X(x)-r,Y(y)-r,X(x)+r,Y(y)+r),outline=GOLD,width=4)
                dot(dr,X(x),Y(y),max(1,round(22*q['points'])),col)
                if q['points']>.7:txt(dr,X(x),Y(y)-42,f'({x},{y})',25,col,center=True)
            if q['points']>.8:
                txt(dr,839,923,'仍然分错',32,CORAL,center=True)
                txt(dr,839,972,f"{data['errors']} / 4",43,GOLD,center=True)
        if t>=q['retreat_end']:lines(dr,82,1089,s['source'],size=26,width=850,gap=3,color=INK)
    elif kind=='xor':
        data=motion.xor_values(t-s['beats'][3]['start'])
        X=lambda v:270+485*v;Y=lambda v:1000-221*v
        if local>2.7:
            txt(dr,509,578,'颜色表示目标；绿色区域预测 1',28,center=True)
            badge(dr,94,616,f"W = ({data['W'][0]:+.2f}, {data['W'][1]:+.2f})",width=405,size=30)
            badge(dr,516,616,f"b = {data['b']:+.2f}",width=190,size=29)
            badge(dr,722,616,f"错 {data['errors']} / 4",fill='#f8ddcf',width=199,size=32)
        rect=[(-.12,-.12),(1.12,-.12),(1.12,1.12),(-.12,1.12)]
        if p[3]>.02:
            poly=motion.clipped_half_plane(rect,data['W'],data['b'])
            if len(poly)>2:dr.polygon([(X(x),Y(y)) for x,y in poly],fill='#e1eee5')
            seg=motion.boundary_segment(data['W'],data['b'],(-.12,-.12,1.12,1.12))
            if len(seg)==2:dr.line([(X(x),Y(y)) for x,y in seg],fill=INK,width=5)
        arrow(dr,(211,1027),(829,1027),width=3);arrow(dr,(211,1027),(211,745),width=3)
        txt(dr,842,1014,'x₁',29);txt(dr,168,740,'x₂',29)
        for point in data['points']:
            x,y=point['x'];xx,yy=X(x),Y(y);col=TEAL if point['target'] else CORAL
            if p[3]>.1 and point['wrong']:
                r=37+3*math.sin(local*3)
                dr.ellipse((xx-r,yy-r,xx+r,yy+r),outline=GOLD,width=5)
            dot(dr,xx,yy,26,col)
            txt(dr,xx,yy-68,f'({x},{y})',29,col,center=True)
            if p[3]>.1:txt(dr,xx,yy+49,f"z = {point['z']:+.2f}",27,CORAL if point['wrong'] else TEAL,center=True)
    elif kind=='collapse':
        labels=['输入 x','× 2 + 1','× 3 − 4']
        value=round(1.5+1.2*math.sin(local*.75),2);values=[value,2*value+1,6*value-1]
        for i,label in enumerate(labels):
            x=130+i*272;card(dr,(x,652,x+230,790),'#f7ead4',radius=20)
            txt(dr,x+115,675,label,35,center=True)
            txt(dr,x+115,735,f'{values[i]:.2f}',34,TEAL,center=True)
            if i<2:
                arrow(dr,(x+233,723),(x+265,723),width=4)
                dot(dr,x+233+32*((local/1.2)%1),723,7,TEAL)
        if local>2.7:txt(dr,509,580,'两层计算，合成一层',36,center=True)
        if p[2]>.1:
            arrow(dr,(500,823),(500,865),TEAL,width=5)
            card(dr,(200,886,800,1010),'#dceae2',radius=22)
            txt(dr,500,912,f"6 × {value:.2f} − 1 = {values[-1]:.2f}",43,TEAL,center=True)
            txt(dr,500,1040,'合并前后使用同一个 x',31,center=True)
    elif kind=='fold':
        if local>2.7:txt(dr,500,581,'s = 灯一 + 灯二',36,center=True)
        arrow(dr,(178,960),(866,960),width=4);arrow(dr,(178,960),(178,612),width=4)
        txt(dr,155,579,'h',34);txt(dr,860,986,'s',34)
        lift=p[2]
        for value,hh,lab,cls in [(0,0,'00',0),(1,1,'01 / 10',1),(2,0,'11',0)]:
            x=230+280*value;y=928-245*hh*lift
            dot(dr,x,y,28,TEAL if cls else CORAL);txt(dr,x,y+41,lab,33,center=True)
        if p[2]>.1:
            dr.line([(230,928),(510,928-245*lift),(790,928)],fill=TEAL,width=6)
        if p[3]>.1:
            dashed(dr,(190,806),(843,806),CORAL,4);txt(dr,848,787,'0.5',30,CORAL)
        if p[2]>.95:
            cases=[(0,0),(0,1),(1,0),(1,1)]
            x1,x2=cases[int(max(0,t-s['beats'][3]['start'])/1.2)%4]
            ss=x1+x2;hh=max(0,ss)-2*max(0,ss-1)
            xx,yy=230+280*ss,928-245*hh
            dr.ellipse((xx-41,yy-41,xx+41,yy+41),outline=GOLD,width=5)
            txt(dr,500,1030,f'输入 ({x1},{x2}) → s = {ss} → h = {hh}',33,TEAL,center=True)
    elif kind=='gradient':
        if local>2.7:txt(dr,500,580,'学习信号向前面的层传回',35,center=True)
        for i in range(6):
            x=830-i*118
            radius=max(7,32*(.65**i))
            dot(dr,x,759,radius,TEAL if i<2 else GOLD)
            if i<5:arrow(dr,(x-radius-7,759),(x-118+max(7,radius*.65)+7,759),TEAL,width=max(3,13-i*2))
            txt(dr,x,840,['1','¼','1/16','1/64','…','很弱'][i],34,center=True)
        step=int(max(0,local-2.5)/.85)%11
        badge(dr,182,945,f"经过 {step} 层：0.25^{step} {'≈' if step>=4 else '='} {0.25**step:.6f}",width=636,size=33)
        travel=(max(0,local-2.5)/.85)%5
        dot(dr,830-118*travel,759,max(5,21*(.5**travel)),CORAL)
        txt(dr,500,1035,'仅示意激活因子；完整梯度还含权重',29,center=True)
    elif kind in ('sigmoid','saturation','relu','leaky','gelu','silu'):
        title={'sigmoid':'硬阈值 → Sigmoid','saturation':'Sigmoid / Tanh：两端都会饱和','relu':'负侧归零，正侧原样通过','leaky':'负侧留一点斜率','gelu':'按累积概率平滑加权','silu':'用 Sigmoid 调节通过比例'}[kind]
        if local>2.7:txt(dr,500,578,title,33,center=True,max_width=810)
        yrange=(-1,1.3) if kind in ('sigmoid','saturation') else (-1,3.3)
        X,Y=chart(dr,(168,640,872,955),(-3,3),yrange)
        if kind=='sigmoid':
            u=p[1];curve(dr,lambda z:(1-u)*(0 if z<0 else 1)+u*sigmoid(z),X,Y,color=TEAL)
            txt(dr,500,1025,'1986 · 反向传播学习隐藏表征',31,center=True)
        elif kind=='saturation':
            curve(dr,sigmoid,X,Y,color=CORAL)
            if p[2]>.1:curve(dr,math.tanh,X,Y,color=TEAL,reveal=p[2])
            xx=motion.live_input(s,t);yy=sigmoid(xx);slope=yy*(1-yy)
            dot(dr,X(xx),Y(yy),13,CORAL)
            dr.line([(X(xx-.45),Y(yy-.45*slope)),(X(xx+.25),Y(yy+.25*slope))],fill=CORAL,width=5)
            txt(dr,500,1025,'零中心 ≠ 不饱和',38,center=True)
        elif kind=='relu':
            curve(dr,lambda z:max(0,z),X,Y,reveal=max(.05,.5*p[0]+.5*p[1]))
            if p[1]>.1:txt(dr,760,708,'斜率 1',34,TEAL,center=True)
            if p[0]>.1:txt(dr,260,906,'梯度 0',34,CORAL,center=True)
            txt(dr,500,1025,'−2, −1, 0, 1, 2 → 0, 0, 0, 1, 2',30,center=True)
        elif kind=='leaky':
            curve(dr,lambda z:max(0,z),X,Y,color='#b0a48d',width=4)
            a=round((.12+.13*(.5+.5*math.sin(local*.85)))*p[1],2)
            curve(dr,lambda z:z if z>=0 else a*z,X,Y,color=TEAL)
            txt(dr,265,852,f'负斜率 a = {a:.2f}',29,TEAL,center=True)
            txt(dr,500,1025,'示意斜率；实际 PReLU 由训练学习',30,center=True)
        elif kind=='gelu':
            curve(dr,lambda z:max(0,z),X,Y,color='#b0a48d',width=4)
            curve(dr,gelu,X,Y,reveal=max(.05,p[1]))
            if p[2]>.1:
                dot(dr,X(-1),Y(gelu(-1)),14,CORAL)
                txt(dr,255,807,'−0.1587',35,CORAL,center=True)
            txt(dr,500,1025,'Φ 是累积概率；计算结果是确定的',31,center=True)
        elif kind=='silu':
            curve(dr,silu,X,Y,reveal=max(.05,p[0]))
            if p[2]>.1:dot(dr,X(2),Y(silu(2)),14,CORAL)
            txt(dr,500,1025,'Swish 的 β = 1  →  SiLU',37,center=True)
        trace_ready=p[1]>.95 if kind in ('sigmoid','relu','gelu') else True
        if local>2.8 and trace_ready:
            z=round(motion.live_input(s,t),2)
            fn={'sigmoid':sigmoid,'saturation':sigmoid,'relu':lambda q:max(0,q),'leaky':lambda q:q if q>=0 else a*q,'gelu':gelu,'silu':silu}[kind]
            value=fn(z);dot(dr,X(z),Y(value),12,CORAL)
            dashed(dr,(X(z),Y(0)),(X(z),Y(value)),GOLD,2,6)
            desc=f'z = {z:+.2f} → 输出 {value:+.2f}'
            if kind=='saturation':desc+=f'  导数 {value*(1-value):.3f}'
            txt(dr,500,612,desc,27,TEAL,center=True)
    elif kind in ('glu','swiglu'):
        if local>2.7:txt(dr,509,581,'内容和门，各有一组权重',33,center=True)
        card(dr,(399,636,619,704),'#f7ead4',radius=18);txt(dr,509,653,'同一输入 x',31,center=True)
        growth=p[1]
        if growth>.01:
            arrow(dr,(425,709),(425+(286-425)*growth,709+56*growth),width=4)
            arrow(dr,(590,709),(590+(748-590)*growth,709+56*growth),width=4)
            card(dr,(121,847-72*growth,439,847+72*growth),'#dceae2',radius=max(2,round(22*growth)))
            card(dr,(586,847-72*growth,900,847+72*growth),'#f8ddcf',radius=max(2,round(22*growth)))
        if growth>.8:
            txt(dr,280,790,'内容支路 a',33,TEAL,center=True)
            txt(dr,743,790,'门支路 g',33,CORAL,center=True)
        if kind=='glu':
            if growth>.9:txt(dr,280,844,'4',53,TEAL,center=True)
            if p[2]>.8:txt(dr,743,850,'σ(g) = 0.25',33,CORAL,center=True)
            val=1
        else:
            gg=-1+3*p[2];gate=silu(gg);val=4*gate
            if growth>.9:
                txt(dr,280,844,'4',53,TEAL,center=True)
                txt(dr,743,850,f'SiLU(g) = {gate:.2f}',30,CORAL,center=True)
        if p[2]>.01:
            q=p[2]
            arrow(dr,(280,927),(280+(471-280)*q,927+57*q),TEAL,width=4)
            arrow(dr,(743,927),(743+(544-743)*q,927+57*q),CORAL,width=4)
            txt(dr,509,946,'⊙',48,center=True)
        if p[min(3,len(p)-1)]>.1 or (kind=='swiglu' and growth>.95):
            card(dr,(290,1004,730,1072),'#dceae2',radius=20)
            txt(dr,510,1017,f'输出 = {val:.2f}' if kind=='swiglu' else '4 × 0.25 = 1',37,TEAL,center=True)
        # Deterministic travelling dots explain how the two branches feed the product.
        phase=((t-s['start'])%2)/2
        for a,b,col in ([((425,709),(286,765),TEAL),((590,709),(748,765),CORAL)] if growth>.95 else [])+([((280,927),(471,984),TEAL),((743,927),(544,984),CORAL)] if p[2]>.95 else []):
            dot(dr,a[0]+(b[0]-a[0])*phase,a[1]+(b[1]-a[1])*phase,8,col)
    elif kind=='budget':
        if local>2.7:txt(dr,500,581,'同一参数预算，比较才公平',35,center=True)
        txt(dr,135,642,'普通 FFN',36)
        for i in range(2):
            card(dr,(140+i*270,708,400+i*270,792),'#f7ead4',radius=12);txt(dr,270+i*270,730,'d × 3072',33,center=True)
        txt(dr,135,839,'门控 FFN',36)
        u=p[1];bw=246-(246-164)*u
        for i in range(3):
            x=140+i*(bw+12);card(dr,(x,906,x+bw,990),'#dceae2',radius=12)
            txt(dr,x+bw/2,932,'d × '+str(round(3072+(2048-3072)*u)),29,center=True,max_width=bw-10)
        txt(dr,500,1034,'宽度 3072 → 2048（约 ⅔）',35,TEAL,center=True)
    elif kind=='outliers':
        if local>2.7:txt(dr,500,581,'两支路相同的大正值示意：a = g = t',29,center=True)
        X,Y=chart(dr,(165,646,850,976),(0,64),(0,4200))
        def power(x):return 0 if x<=0 else x**(1+3/(math.sqrt(x)+1))*sigmoid(x)
        curve(dr,lambda z:z*z*sigmoid(z),X,Y,(0,64),CORAL,reveal=max(.1,p[1]))
        if p[2]>.1:curve(dr,power,X,Y,(0,64),TEAL,reveal=p[2])
        txt(dr,416,586,'SwiGLU',33,CORAL,center=True);txt(dr,701,586,'PowLU · m=3',33,TEAL,center=True)
        txt(dr,500,1030,'增长曲线示意；不是训练损失曲线',30,center=True)
        if p[2]>.95:
            xx=32+28*math.sin(local*.68);q=xx*xx*sigmoid(xx)
            dot(dr,X(xx),Y(q),12,CORAL);dot(dr,X(xx),Y(power(xx)),12,TEAL)
            dashed(dr,(X(xx),Y(q)),(X(xx),Y(power(xx))),GOLD,3,7)
    elif kind=='sparse':
        if local>2.7:txt(dr,500,580,'小数值，是“可少算”的候选',33,center=True)
        values=[.02,1.3,.08,.04,1,.015,1.1,.05]
        for i,value in enumerate(values):
            x=167+i*89;hh=value/1.3*284
            col='#d8d0bd' if value<.1 and p[1]>.5 else TEAL
            dr.rounded_rectangle((x,961-max(10,hh),x+53,961),radius=6,fill=col,outline=INK,width=2)
            txt(dr,x+26,982,str(i+1),31,center=True)
            if value<.1 and p[1]>.5:dashed(dr,(x,636),(x+53,636),CORAL,2,6)
        if local>2.7:txt(dr,500,622,'示意输出幅值 · 贡献大小仍需检验',27,center=True)
        n=int(max(0,local-2.7)*1.5)%8;x=167+n*89
        dr.rounded_rectangle((x-7,658,x+60,965),radius=9,outline=GOLD,width=3)
        txt(dr,500,1040,'稀疏率 → 计算路径 → 实测时间',34,center=True)
    elif kind=='hardware':
        if local>2.7:txt(dr,500,581,'每四个位置，保留两个',36,center=True)
        masks=[[1,0,1,0],[0,1,0,1],[1,1,0,0]]
        for j,row in enumerate(masks):
            for i,bit in enumerate(row):
                x,y=250+i*139,643+j*109
                active=bool(bit) or p[1]<.5
                card(dr,(x,y,x+92,y+84),'#dceae2' if active else '#e7dfd0',radius=13,width=3)
                txt(dr,x+46,y+21,'1' if active else '0',43,TEAL if active else INK,center=True)
        row=int(max(0,local-2.6)/.9)%3
        dr.rounded_rectangle((237,633+row*109,773,739+row*109),radius=18,outline=GOLD,width=4)
        txt(dr,500,1027,'FFN 内核最高约 1.3×；整模型仍需实测',29,center=True)
    elif kind=='dyt':
        if local>2.7:txt(dr,500,581,'替换的是归一化的位置',35,center=True)
        for y,label,fill in [(665,'归一化','#f7ead4'),(805,'Dynamic Tanh','#dceae2')]:
            txt(dr,150,y+22,'x',42,center=True)
            arrow(dr,(195,y+42),(302,y+42),width=4)
            card(dr,(310,y,680,y+88),fill,radius=16)
            txt(dr,495,y+21,label,36,center=True)
            arrow(dr,(688,y+42),(790,y+42),width=4);txt(dr,850,y+28,'后续层',30,center=True)
            phase=(local/1.4)%1
            dot(dr,197+600*phase,y+43,8,TEAL if label=='Dynamic Tanh' else GOLD)
        if p[1]>.8:
            alpha=round(.5+.5*(.5+.5*math.sin(local*.8)),2);x=round(2.7*math.sin(local*.85),2)
            txt(dr,500,948,f'x = {x:+.2f}  α = {alpha:.2f} → tanh(αx) = {math.tanh(alpha*x):+.2f}',28,TEAL,center=True)
        txt(dr,500,1006,'可学习的尺度 + 非线性压缩',36,center=True)
    elif kind=='follow':
        txt(dr,509,517,'每次看懂一个知识点',52,TEAL,center=True)
        for x,label in [(143,'图解'),(420,'论文'),(697,'实验')]:
            card(dr,(x,653,x+219,834),'#f7ead4',radius=20)
            # Three simple vector objects, not a raster or QR pattern.
            if label=='图解':
                dr.line([(x+38,763),(x+87,707),(x+170,769)],fill=TEAL,width=6)
                for dx,dy in [(38,763),(87,707),(170,769)]:dot(dr,x+dx,dy,8,TEAL)
            elif label=='论文':
                dr.rectangle((x+68,691,x+150,784),outline=INK,width=4)
                for yy in [714,738,762]:dr.line([(x+82,yy),(x+136,yy)],fill=TEAL,width=4)
            else:
                txt(dr,x+110,709,'</>',60,TEAL,center=True)
            txt(dr,x+110,862,label,41,center=True)
        txt(dr,509,956,'GitHub · shikanon',47,center=True)
        txt(dr,509,1023,'点亮 Star，一起学习',43,CORAL,center=True)
        if p[2]>.05:
            size=32*(.7+.3*p[2]);pts=[]
            for i in range(11):
                a=-math.pi/2+i*math.pi/5;r=size if i%2==0 else size*.45
                pts.append((897+r*math.cos(a),540+r*math.sin(a)))
            dr.line(pts[:max(2,round(11*p[2]))],fill=GOLD,width=5,joint='curve')

@lru_cache(maxsize=256)
def sprite(action,index):
    if action=='doctor-pointer':
        return Image.open(BASE/'assets/doctor-pointer'/B['frames'][index]).convert('RGBA')
    frame=M['actions'][action]['frames'][index]
    return Image.open(BASE/'assets/author-animation'/frame['file']).convert('RGBA').resize((290,435),Image.Resampling.LANCZOS)

def state(frame):
    t=frame/FPS
    index=max(0,bisect.bisect_right([s['start'] for s in D['scenes']],t)-1)
    s=D['scenes'][index]
    entry=B if s['actor']=='doctor-pointer' else M['actions'][s['actor']]
    actor_index=int(max(0,t-s['start']-.12)*entry['fps'])%len(entry['frames'])
    cap=next((i for i,c in enumerate(D['captions']) if c['start']<=t<c['end']),None)
    return t,index,s,actor_index,cap

def notes_motion(dr,s,t):
    local=t-s['start'];u=smooth((local-.05)/.65)
    # The title settles into place once; no independent random wiggle.
    lines(dr,64+14*(1-u),275+18*(1-u),s['title'],size=68,width=876,gap=15)
    if s['kind']=='hook':local=max(0,local-motion.hook_state(s,t)['retreat_end'])
    pointer=s['actor']=='doctor-pointer';left=550 if pointer else 375
    x=left+24;width=954-x-25;size=42 if pointer else 47
    insight=wrap(dr,s['insight'],size,width)
    for row,line in enumerate(insight):
        q=max(0,min(1,(local-.25-row*.18)/.7))
        text=line[:round(len(line)*q)]
        if text:txt(dr,x,1235+row*(size+10),text,size,TEAL)
    detail=wrap(dr,s['detail'],33 if pointer else 36,width)
    for row,line in enumerate(detail):
        q=max(0,min(1,(local-1.05-row*.3)/.55))
        text=line[:round(len(line)*q)]
        if text:txt(dr,x,1258+len(insight)*(size+10)+row*(45 if pointer else 48),text,33 if pointer else 36)
    active=max([i for i,b in enumerate(s['beats']) if t>=b['start']] or [0])
    phase=smooth((t-s['beats'][active]['start'])/.7)
    dr.line([(x,1494),(x+width,1494)],fill='#bfd4c5',width=3)
    if phase>0:dr.line([(x,1494),(x+width*phase,1494)],fill=GOLD if active%2 else TEAL,width=5)

def actor_geometry(s,t):
    if s['actor']=='doctor-pointer':return (22,1040),sprite(s['actor'],0).size
    if s['kind']=='hook':
        q=motion.hook_state(s,t)['retreat']
        return (round(309-239*q),round(500+657*q)),(round(400-110*q),round(600-165*q))
    return (70,1157),(290,435)

def frame_image(frame):
    t,index,s,actor_index,cap=state(frame)
    im=background(index).copy();dr=ImageDraw.Draw(im)
    notes_motion(dr,s,t)
    reveal=motion.diagram_reveal(s['kind'],t-s['start'])
    if reveal>0:
        diagram=im.copy()
        illustration(diagram,s,t)
        im=diagram if reveal==1 else Image.blend(im,diagram,reveal)
    motion.handwriting(im,s,t)
    actor=sprite(s['actor'],actor_index)
    position,size=actor_geometry(s,t)
    if actor.size!=size:actor=actor.resize(size,Image.Resampling.LANCZOS)
    im.paste(actor,position,actor)
    dr=ImageDraw.Draw(im)
    # Current chapter and subsection progress use the same engineering time.
    x=65
    for c in D['chapters']:
        width=878*c['share'];dr.rounded_rectangle((x,130,x+width-7,172),radius=10,fill='#e6dbc5')
        fraction=max(0,min(1,(t-c['start'])/(c['end']-c['start'])))
        if fraction>0:dr.rounded_rectangle((x,130,x+(width-7)*fraction,172),radius=10,fill=TEAL)
        txt(dr,x+width/2,89,{'motivation':'为什么','evolution':'演化','frontier':'前沿'}[c['id']],31,center=True)
        x+=width
    dr.rounded_rectangle((65,186,944,194),radius=4,fill='#ded0b7')
    frac=max(0,min(1,(t-s['start'])/(s['end']-s['start'])))
    if frac>0:
        dr.rounded_rectangle((65,186,65+879*frac,194),radius=4,fill=CORAL)
        dr.ellipse((65+879*frac-6,184,65+879*frac+6,196),fill=CORAL)
    if cap is not None:
        c=D['captions'][cap]
        card(dr,(65,1588,954,1740),fill='#fffdf5',radius=22,width=3)
        caption=wrap(dr,c['text'],49,827)
        if len(caption)>2:raise ValueError(f'Caption overflow: {c}')
        yy=1607 if len(caption)>1 else 1640
        for j,value in enumerate(caption):
            y=yy+j*62;txt(dr,510,y,value,49,center=True)
            # Highlight only a word whose actual narration cue is active.
            for beat in s['beats']:
                term=D['display_terms'].get(beat['cue'],beat['cue'])
                if beat['start']<=t<beat['end'] and term in value:
                    full=dr.textbbox((0,0),value,font=font(49))[2]
                    x=510-full/2+dr.textlength(value.split(term)[0],font=font(49))
                    txt(dr,x,y,term,49,TEAL)
                    length=dr.textlength(term,font=font(49))*smooth((t-beat['start'])/.45)
                    dr.line([(x,y+54),(x+length,y+54)],fill=GOLD,width=3)
    return im

def preview():
    global LOG_TEXT
    LOG_TEXT=True;TEXT_LOG.clear();images=[]
    for i,s in enumerate(D['scenes']):
        sample=min(s['end']-.12,s['beats'][-1]['start']+1.1)
        f=round(sample*FPS);im=frame_image(f)
        path=BASE/'qa'/f'{s["id"]}-preview.jpg';im.save(path,quality=94)
        small=im.resize((270,480),Image.Resampling.LANCZOS);images.append(small)
    contact=Image.new('RGB',(270*4,480*math.ceil(len(images)/4)),PAPER)
    for i,im in enumerate(images):contact.paste(im,((i%4)*270,(i//4)*480))
    contact.save(BASE/'qa/storyboard-contact.jpg',quality=95)
    violations=[t for t in TEXT_LOG if t['box'][0]<60 or t['box'][2]>985 or t['box'][1]<65 or t['box'][3]>1855]
    # Zero-length footer text is ignored. Current visual content reserves a right and bottom platform lane.
    violations=[t for t in violations if t['text']]
    report={'text_boxes':len(TEXT_LOG),'safe_bounds':[60,65,985,1855],'violations':violations}
    (BASE/'qa/text-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'previews':len(images),'text_bounds_violations':len(violations),'violations':violations},ensure_ascii=False))

def render(output):
    count=round(D['duration']*FPS);output.parent.mkdir(exist_ok=True)
    command=[ffmpeg(),'-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(BASE/'audio/narration.m4a'),'-f','ffmetadata','-i',str(BASE/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','libx264','-preset','veryfast','-crf','19','-threads','8','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-t',f'{D["duration"]:.12f}','-movflags','+faststart',str(output)]
    with (BASE/'qa/render.log').open('w') as log:
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
        try:
            for f in range(count):
                process.stdin.write(frame_image(f).tobytes())
                if f%600==0:print(json.dumps({'frame':f,'total_frames':count,'progress':round(f/count,3)}),flush=True)
            process.stdin.close();code=process.wait()
        except BaseException:
            process.kill();raise
    if code:raise RuntimeError((BASE/'qa/render.log').read_text())
    poster=frame_image(round(min(D['scenes'][0]['end']-.1,6)*FPS))
    poster.save(BASE/'assets/poster.jpg',quality=96)
    print(json.dumps({'output':str(output),'frames':count,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--output',type=Path,default=BASE/'renders/activation-functions-v6.mp4');args=parser.parse_args()
    if args.preview:preview()
    else:render(args.output)
