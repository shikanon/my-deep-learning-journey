"""Deterministic vector handwriting and data-driven teaching motion."""
import json
import math
from functools import lru_cache
from PIL import Image, ImageDraw
from runtime import BASE

INK='#44382e'; TEAL='#246e65'; CORAL='#ae4937'; GOLD='#c59843'

def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)

def ellipse(cx,cy,rx,ry,n=36):
    return [(cx+rx*math.cos(i*2*math.pi/n),cy+ry*math.sin(i*2*math.pi/n)) for i in range(n+1)]

# Single-stroke glyphs: these are editable pen paths, not wipes over a text bitmap.
G={
 'z':[[(.07,.34),(.66,.34),(.08,1),(.7,1)]],
 'W':[[(.02,0),(.18,1),(.5,.38),(.78,1),(.97,0)]],
 'x':[[(.08,.34),(.65,1)],[(.66,.34),(.07,1)]],
 'b':[[(.1,0),(.1,1)],[(.1,.5),(.3,.33),(.58,.38),(.7,.63),(.64,.88),(.38,1),(.1,.87)]],
 'a':[ellipse(.35,.68,.27,.32),[(.62,.36),(.62,1)]],
 'd':[ellipse(.35,.68,.27,.32),[(.62,0),(.62,1)]],
 'e':[[(.08,.65),(.64,.65),(.58,.4),(.35,.33),(.13,.43),(.07,.68),(.17,.94),(.4,1),(.65,.88)]],
 'f':[[(.1,.33),(.65,.33)],[(.63,.04),(.42,0),(.3,.17),(.3,1)]],
 'g':[ellipse(.35,.65,.27,.31),[(.62,.35),(.62,1.13),(.5,1.27),(.22,1.25),(.08,1.15)]],
 'h':[[(.1,0),(.1,1)],[(.1,.58),(.28,.36),(.47,.33),(.63,.48),(.63,1)]],
 'i':[[(.32,.4),(.32,1)],[(.32,.1),(.33,.12)]],
 'L':[[(.1,0),(.1,1),(.75,1)]],
 'm':[[(.07,1),(.07,.34),(.07,.55),(.27,.34),(.43,.42),(.43,1)],[(.43,.55),(.65,.34),(.82,.43),(.82,1)]],
 'n':[[(.1,1),(.1,.34),(.1,.56),(.3,.34),(.5,.37),(.64,.53),(.64,1)]],
 'o':[ellipse(.36,.67,.29,.33)],
 'p':[[(.1,1.25),(.1,.34)],[(.1,.5),(.34,.34),(.59,.39),(.67,.64),(.59,.89),(.35,1),(.1,.87)]],
 'R':[[(.1,1),(.1,0),(.48,0),(.72,.15),(.68,.38),(.47,.5),(.1,.5)],[(.43,.5),(.79,1)]],
 'r':[[(.1,1),(.1,.34),(.1,.54),(.32,.34),(.63,.4)]],
 's':[[(.65,.4),(.43,.32),(.17,.37),(.09,.55),(.3,.65),(.56,.73),(.66,.88),(.52,1),(.23,1),(.08,.91)]],
 'S':[[(.76,.12),(.52,0),(.22,.03),(.07,.23),(.16,.43),(.57,.57),(.77,.76),(.68,.96),(.36,1),(.06,.88)]],
 't':[[(.35,.1),(.35,.86),(.44,1),(.63,.93)],[(.06,.38),(.67,.38)]],
 'u':[[(.1,.34),(.1,.81),(.25,1),(.44,1),(.64,.84)],[(.64,.34),(.64,1)]],
 'U':[[(.08,0),(.08,.76),(.23,.98),(.51,1),(.76,.78),(.76,0)]],
 'v':[[(.07,.34),(.35,1),(.67,.34)]],
 'w':[[(.05,.34),(.2,1),(.43,.55),(.66,1),(.84,.34)]],
 'y':[[(.06,.34),(.34,.95),(.68,.34)],[(.36,.88),(.2,1.25),(.06,1.3)]],
 'G':[[(.82,.15),(.6,0),(.25,.05),(.07,.3),(.05,.71),(.29,.97),(.67,1),(.83,.8),(.83,.55),(.52,.55)]],
 'E':[[(.76,0),(.1,0),(.1,1),(.79,1)],[(.1,.5),(.65,.5)]],
 '0':[ellipse(.4,.5,.32,.5)],
 '1':[[(.18,.18),(.4,0),(.4,1)],[(.1,1),(.7,1)]],
 '2':[[(.08,.17),(.24,.02),(.51,0),(.71,.16),(.68,.38),(.09,1),(.75,1)]],
 '3':[[(.1,.09),(.35,0),(.66,.1),(.7,.31),(.48,.48),(.26,.49)],[(.48,.48),(.72,.63),(.73,.83),(.53,1),(.2,.98),(.08,.87)]],
 '4':[[(.55,0),(.07,.68),(.8,.68)],[(.55,0),(.55,1)]],
 '5':[[(.74,0),(.13,0),(.1,.48),(.44,.4),(.69,.53),(.74,.8),(.54,1),(.22,1),(.08,.9)]],
 '6':[[(.7,.1),(.49,0),(.24,.14),(.08,.51),(.08,.82),(.28,1),(.55,1),(.74,.78),(.65,.53),(.36,.45),(.1,.6)]],
 '7':[[(.05,0),(.78,0),(.21,1)]],
 '8':[ellipse(.4,.24,.29,.24),ellipse(.4,.75,.32,.25)],
 '9':[ellipse(.39,.3,.3,.3),[(.69,.3),(.67,.77),(.5,.98),(.22,1)]],
 '(':[[(.5,0),(.27,.23),(.17,.57),(.23,.9),(.45,1.15)]],
 ')':[[(.1,0),(.33,.23),(.43,.57),(.37,.9),(.15,1.15)]],
 '+':[[(.06,.54),(.76,.54)],[(.41,.19),(.41,.88)]],
 '-':[[(.06,.54),(.76,.54)]],
 '−':[[(.06,.54),(.76,.54)]],
 '=':[[(.06,.38),(.76,.38)],[(.06,.72),(.76,.72)]],
 '≈':[[(.04,.35),(.22,.28),(.55,.42),(.78,.35)],[(.04,.67),(.22,.6),(.55,.74),(.78,.67)]],
 '≠':[[(.06,.38),(.76,.38)],[(.06,.72),(.76,.72)],[(.66,.1),(.16,1)]],
 '×':[[(.09,.22),(.7,.89)],[(.7,.22),(.09,.89)]],
 '⊙':[ellipse(.4,.56,.38,.38),ellipse(.4,.56,.05,.05,12)],
 '/':[[(.66,0),(.04,1.12)]],
 '^':[[(.08,.3),(.36,0),(.66,.3)]],
 ',':[[(.25,.9),(.13,1.13)]],
 '.':[[(.25,.95),(.27,.96)]],
 'Φ':[ellipse(.43,.5,.38,.35),[(.43,0),(.43,1)]],
 'σ':[ellipse(.35,.7,.28,.3),[(.34,.4),(.81,.4)]],
 'α':[[(.64,.35),(.2,.33),(.07,.6),(.11,.9),(.4,1),(.58,.68),(.69,.35)],[(.53,.55),(.65,1),(.8,.95)]],
 'β':[[(.1,1.25),(.1,.15),(.31,0),(.54,.02),(.65,.23),(.51,.46),(.2,.5),(.59,.56),(.74,.75),(.65,.95),(.39,1),(.1,.92)]],
 'γ':[[(.07,.33),(.32,.48),(.37,1.25),(.69,.33)]],
 '→':[[(.03,.55),(.82,.55)],[(.58,.27),(.84,.55),(.58,.83)]],
}

FORMULAS={
 'xor':'z = W x + b',
 'collapse':'3(2x + 1) - 4 = 6x - 1',
 'fold':'h = ReLU(s) - 2ReLU(s - 1)',
 'gradient':'0.25^10 ≈ 0.000001',
 'sigmoid':'σ(z) = 1/(1 + exp(-z))',
 'saturation':'tanh(z)',
 'relu':'ReLU(z) = max(0,z)','leaky':'f(z) = max(z,a z)',
 'gelu':'GELU(z) = z Φ(z)','silu':'SiLU(z) = z σ(z)',
 'glu':'GLU = a × σ(g)','swiglu':'SwiGLU = a × SiLU(g)',
 'budget':'2dm = 3d(2m/3)','outliers':'t × SiLU(t) ≈ t × t',
 'sparse':'0.02 ≠ 0','hardware':'4 → 2',
 'dyt':'y = γ × tanh(αx) + β',
}

def diagram_reveal(kind,elapsed):
    return ease((elapsed-3.05)/.3) if kind in FORMULAS else 1

def hook_state(scene,t):
    start=next(w['start'] for w in scene['words'] if w['text']=='如')
    retreat=ease((t-start)/.9)
    network=ease((t-start)/.6)
    deep=ease((t-scene['beats'][1]['start'])/.8)
    depth=1+round(127*deep)
    labels=['输入',*[str(i) for i in range(1,depth+1)],'输出'] if depth<6 else [
        '输入','1','2','…',str(depth-2),str(depth-1),str(depth),'输出']
    return {'retreat':retreat,'retreat_end':start+.9,'network':network,
            'depth':depth,'layer_labels':labels,
            'points':ease((t-scene['beats'][2]['start'])/.55),
            'flow':max(0,t-start)*.85%1,'handwriting':False}

@lru_cache(maxsize=48)
def pen_paths(text,height=44,max_width=660):
    x=0;paths=[];superscript=False
    for char in text:
        if char=='^':superscript=True;continue
        if char==' ':x+=.4;superscript=False;continue
        if char not in G:raise ValueError('Missing pen glyph: '+char)
        k=.58 if superscript else 1;dy=-.36 if superscript else 0
        for path in G[char]:paths.append([(x+px*k,py*k+dy) for px,py in path])
        x+=(max(px for path in G[char] for px,py in path)+.23)*k
    scale=min(height,max_width/max(.1,x))
    paths=[[(px*scale,py*scale) for px,py in path] for path in paths]
    return paths,x*scale,scale

def stroke_segments(paths):
    return [(a,b,math.dist(a,b)) for path in paths for a,b in zip(path,path[1:])]

def writing_state(kind,elapsed,duration=2.0):
    if kind not in FORMULAS:return None
    paths,width,height=pen_paths(FORMULAS[kind])
    segments=stroke_segments(paths);total=sum(v for a,b,v in segments)
    p=max(0,min(1,(elapsed-.3)/duration))
    remaining=total*p;visible=[];tip=segments[0][0]
    for a,b,length in segments:
        if remaining>=length:
            visible.append((a,b));tip=b;remaining-=length
        elif remaining>0:
            q=remaining/length;tip=(a[0]+q*(b[0]-a[0]),a[1]+q*(b[1]-a[1]))
            visible.append((a,tip));break
        else:break
    return {'segments':visible,'tip':tip,'width':width,'progress':p,
            'opacity':ease((elapsed-.2)/.18)*(1-ease((elapsed-2.3)/.35)),
            'total_length':total,'visible_length':total*p}

WRITER=json.loads((BASE/'assets/pencil-writer/manifest.json').read_text())
REGISTRATION=json.loads((BASE/'assets/pencil-writer/video-registration.json').read_text())

@lru_cache(maxsize=16)
def writer_image(index):
    return Image.open(BASE/'assets/pencil-writer'/WRITER['frames'][index]).convert('RGBA').resize(
        tuple(REGISTRATION['display_size']),Image.Resampling.LANCZOS)

def writing_origin(kind,width,elapsed):
    # Leave room for the full character above the graphite tip. Once it has
    # faded out, settle the complete formula before revealing the diagram.
    target=512
    settle=ease((elapsed-2.65)/.4)
    return 471+38*settle-width/2,820+(target-820)*settle

def writer_state(kind,elapsed):
    q=writing_state(kind,elapsed)
    if not q:return None
    x,y=writing_origin(kind,q['width'],elapsed)
    index=min(WRITER['frameCount']-1,int(max(0,elapsed-.3)*WRITER['fps']))
    anchor=REGISTRATION['tip_anchors'][index]
    sx=REGISTRATION['display_size'][0]/WRITER['frameSize']['width']
    sy=REGISTRATION['display_size'][1]/WRITER['frameSize']['height']
    tip=[x+q['tip'][0],y+q['tip'][1]]
    position=[round(tip[0]-anchor[0]*sx),round(tip[1]-anchor[1]*sy)]
    return {**q,'origin':[x,y],'frame_index':index,'source_tip_anchor':anchor,
            'tip_absolute':tip,'position':position,'source_frame':WRITER['frames'][index],
            'placed_tip':[position[0]+anchor[0]*sx,position[1]+anchor[1]*sy],
            'formula':FORMULAS[kind]}

def handwriting(im,s,t):
    q=writer_state(s['kind'],t-s['start'])
    if not q:return None
    x,y=q['origin']
    dr=ImageDraw.Draw(im)
    for a,b in q['segments']:
        dr.line([(x+a[0],y+a[1]),(x+b[0],y+b[1])],fill=TEAL,width=4)
    if q['opacity']>0:
        writer=writer_image(q['frame_index']).copy()
        writer.putalpha(writer.getchannel('A').point(lambda v:int(v*q['opacity'])))
        im.paste(writer,tuple(q['position']),writer)
    return q

def xor_values(elapsed):
    # All displayed numbers are rounded first, then reused by the line and classifications.
    u=max(0,elapsed)/2.1;index=int(u)%4;p=ease(u-int(u))
    angles=[45,135,225,315,405];bias=[-.5,-.45,.4,-.3,-.5]
    theta=math.radians(angles[index]+90*p)
    w1=round(math.sqrt(2)*math.cos(theta),2)
    w2=round(math.sqrt(2)*math.sin(theta),2)
    b=round(bias[index]+(bias[index+1]-bias[index])*p,2)
    points=[]
    for x1,x2,target in [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]:
        z=round(w1*x1+w2*x2+b,2);pred=int(z>=0)
        points.append({'x':[x1,x2],'target':target,'z':z,'prediction':pred,'wrong':pred!=target})
    return {'W':[w1,w2],'b':b,'points':points,'errors':sum(v['wrong'] for v in points)}

def clipped_half_plane(poly,w,b):
    out=[]
    for a,c in zip(poly,poly[1:]+poly[:1]):
        za=w[0]*a[0]+w[1]*a[1]+b;zc=w[0]*c[0]+w[1]*c[1]+b
        if za>=0:out.append(a)
        if (za>=0)!=(zc>=0):
            p=za/(za-zc);out.append((a[0]+p*(c[0]-a[0]),a[1]+p*(c[1]-a[1])))
    return out

def boundary_segment(w,b,box=(-.18,-.18,1.18,1.18)):
    xmin,ymin,xmax,ymax=box;points=[]
    if abs(w[1])>1e-9:
        for x in (xmin,xmax):
            y=-(w[0]*x+b)/w[1]
            if ymin-1e-8<=y<=ymax+1e-8:points.append((x,y))
    if abs(w[0])>1e-9:
        for y in (ymin,ymax):
            x=-(w[1]*y+b)/w[0]
            if xmin-1e-8<=x<=xmax+1e-8:points.append((x,y))
    unique=[]
    for point in points:
        if not any(math.dist(point,x)<1e-6 for x in unique):unique.append(point)
    return unique[:2]

def live_input(s,t):
    u=max(0,t-s['start']-2.6)
    return -2.7*math.cos(u*1.02)

def color_mix(a,b,p):
    p=max(0,min(1,p))
    return '#'+''.join(f'{round(int(a[i:i+2],16)*(1-p)+int(b[i:i+2],16)*p):02x}' for i in (1,3,5))
