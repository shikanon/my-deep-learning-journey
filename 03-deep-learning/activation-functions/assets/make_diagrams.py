#!/usr/bin/env python3
"""Original SVG explanatory figures from exact activation formulas."""
from pathlib import Path
from html import escape
import math

BASE = Path(__file__).resolve().parent
INK, TEAL, CORAL, BG = "#40392f", "#237c75", "#c65c45", "#fff9ea"

def text(x, y, value, size=26, color=INK, anchor="start", weight="normal"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" font-weight="{weight}">{escape(value)}</text>'

def line(x1, y1, x2, y2, color=INK, width=3, extra=""):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}" {extra}/>'

def save(name, width, height, body, title, desc):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><rect width="100%" height="100%" rx="24" fill="{BG}"/><g font-family="PingFang SC,Hiragino Sans GB,Arial,sans-serif">{body}</g></svg>'
    (BASE / name).write_text(svg + "\n")

def xor():
    b = text(600, 55, "一条直线分不开，先把特征折一下", 36, anchor="middle", weight="bold")
    for left, title in [(70, "原空间 · 两类点交叉"), (720, "非线性特征空间")]:
        b += text(left + 210, 112, title, 27, anchor="middle")
        b += line(left+30, 480, left+420, 480) + line(left+30, 480, left+30, 175)
    b += text(455, 522, "x₁", 26) + text(74, 155, "x₂", 26)
    for x,y,lab,cls in [(0,0,"(0,0)",0),(0,1,"(0,1)",1),(1,0,"(1,0)",1),(1,1,"(1,1)",0)]:
        px,py=125+270*x,445-230*y
        b += f'<circle cx="{px}" cy="{py}" r="19" fill="{TEAL if cls else CORAL}"/>'
        b += text(px+28, py+8, lab, 23)
    b += line(140,240,380,425,"#8f8572",3,'stroke-dasharray="10 9"')
    b += text(280,562,"报警的两个点在对角",26,anchor="middle")
    b += text(600,300,"→",66,TEAL,anchor="middle")
    b += text(600,352,"两个 ReLU",24,anchor="middle")
    b += text(600,385,"组合",24,anchor="middle")
    b += text(1142,522,"s",26) + text(718,155,"h",26)
    b += line(750,330,1140,330,TEAL,3,'stroke-dasharray="9 7"') + text(980,315,"h = 0.5",22,TEAL)
    for s,h,lab,cls in [(0,0,"(0,0)",0),(1,1,"(0,1) / (1,0)",1),(2,0,"(1,1)",0)]:
        px,py=790+150*s,445-230*h
        b += f'<circle cx="{px}" cy="{py}" r="19" fill="{TEAL if cls else CORAL}"/>'
        b += text(px,py+77 if not cls else py+45,lab,21,anchor="middle")
    b += text(950,562,"同一类点现在可以被分开",26,anchor="middle")
    b += text(600,621,"s = x₁ + x₂      h = ReLU(s) − 2 ReLU(s − 1)",27,anchor="middle")
    save("xor-fold.svg",1200,670,b,"异或的非线性特征变换","原始四个点无法线性分开；两个 ReLU 组合后得到 h 为零、一、一、零。")

def curves():
    funcs = [("Sigmoid",lambda x:1/(1+math.exp(-x)),"输出压在 0 与 1 之间",CORAL), ("ReLU",lambda x:max(0,x),"负侧归零，正侧保留",TEAL), ("GELU",lambda x:x*(1+math.erf(x/math.sqrt(2)))/2,"z × 标准正态累积概率",TEAL), ("SiLU",lambda x:x/(1+math.exp(-x)),"z × Sigmoid(z)",CORAL)]
    b = text(600,55,"统一坐标看曲线：改变输出，也改变斜率",34,anchor="middle",weight="bold")
    for i,(name,fn,caption,col) in enumerate(funcs):
        left,top = 45+(i%2)*600,105+(i//2)*385
        gx,gy,w,h = left+65,top+75,450,220
        def px(x):return gx+(x+3)/6*w
        def py(y):return gy+h-(y+1)/4.3*h
        b += text(left+285,top+32,name,32,col,anchor="middle",weight="bold")
        for xv in [-3,0,3]:
            b+=line(px(xv),gy,px(xv),gy+h,"#e4dbc7",1)+text(px(xv),gy+h+29,str(xv),21,anchor="middle")
        for yv in [-1,0,1,3]:
            b+=line(gx,py(yv),gx+w,py(yv),"#e4dbc7",1)+text(gx-14,py(yv)+7,str(yv),21,anchor="end")
        b+=line(gx,py(0),gx+w,py(0),"#938675",2)+line(px(0),gy,px(0),gy+h,"#938675",2)
        pts=[(px(x),py(fn(x))) for x in [(-3+j*.02) for j in range(301)]]
        b+=f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in pts)}" fill="none" stroke="{col}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        b+=text(left+285,top+365,caption,24,anchor="middle")
    save("activation-curves.svg",1200,895,b,"激活函数的精确曲线","Sigmoid、ReLU、精确 GELU 和 SiLU 使用相同坐标：横轴 -3 到 3，纵轴 -1 到 3.3。")

def gating():
    b=text(600,55,"GLU：内容由另一条支路决定通过多少",34,anchor="middle",weight="bold")
    boxes=[(45,215,180,100,"输入 x",BG),(355,120,300,95,"内容 a = Wₐx + bₐ","#dceae2"),(355,330,300,95,"门 σ(Wgx + bg)","#f8ddcf"),(940,215,215,100,"输出 a ⊙ 门",BG)]
    for x,y,w,h,label,fill in boxes:
        b+=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="19" fill="{fill}" stroke="{INK}" stroke-width="3"/>'+text(x+w/2,y+58,label,26,anchor="middle")
    b+=line(225,265,290,265)+line(290,168,290,378)+line(290,168,355,168)+line(290,378,355,378)
    b+=line(655,168,805,168)+line(805,168,805,230)+line(655,378,805,378)+line(805,378,805,300)+line(840,265,940,265)
    b+=text(805,283,"×",65,TEAL,anchor="middle")
    b+=text(600,480,"一个通道：内容 4 × 门 0.25 = 1",29,anchor="middle")
    b+=text(600,530,"另一个输入：门变为 0.75，输出就变为 3",25,anchor="middle")
    save("gating.svg",1200,580,b,"门控的两个独立投影","输入同时产生内容和门，逐通道相乘；Sigmoid 门值介于零和一。")

if __name__ == "__main__":
    xor();curves();gating()
    print("Generated 3 original SVG figures with exact formulas.")
