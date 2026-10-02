"""Speech-cued author action clips, sampled from real generated sprite frames."""
import math

PLAYBACK={
 'talk':list(range(12)),
 'point-right':[0,1,2,3,4,5,6,7,6,7,6,7,8,9,10,11],
 'think':[0,1,2,3,4,5,6,7,7,7,8,9,10,11],
 'celebrate':list(range(12))+[11]*4,
 'wave':list(range(12)),
 'teach-pointer':[0,1,2,3,4,5,6,7,6,7,6,7,8,9,10,11],
 'think-question':[0,1,2,3,4,5,6,7,7,7,8,9,10,11],
}

def actor_clips(scene,beats,actor_index,start):
    kind=scene['kind'];end=scene['end']
    cue=lambda text:next((b['start'] for b in beats if b['cue']==text),end)
    default={'cancel':'think','curves':'point-right','outlier':'point-right','huber':'think','contrast':'think','ending':'celebrate','follow':'wave'}.get(kind,'talk')
    changes=[(start,default)]
    if kind=='hook':changes=[(start,'talk'),(cue('模型的答案就从六变成三'),'point-right'),(cue('为什么'),'think'),(cue('你怎么扣分'),'talk')]
    elif kind=='loop':changes=[(start,'talk'),(cue('反向传播'),'point-right'),(cue('真实效果'),'think')]
    elif kind=='huber':changes=[(start,'point-right'),(cue('阈值决定'),'think')]
    elif kind=='dpo':changes=[(start,'talk'),(cue('更喜欢哪条回答'),'point-right'),(cue('不只是无限奖励'),'think')]
    elif kind=='siglip':changes=[(start,'point-right' if actor_index==0 else 'talk')]
    elif kind=='ending':changes=[(start,'celebrate')]
    elif kind=='follow':changes=[(start,'wave'),(cue('开源项目'),'point-right'),(cue('我的深度学习之路'),'talk'),(cue('下个知识点见'),'wave')]
    # A cue may precede the actor's reveal; it still determines that entry pose.
    active=changes[0][1]
    for t,a in changes:
        if t<=start:active=a
    changes=[(start,active)]+[(t,a) for t,a in changes if start<t<end-.1]
    changes=sorted(changes)
    return [{'start':round(t,5),'end':round(changes[i+1][0] if i+1<len(changes) else end,5),'action':('think-question' if a=='think' else 'teach-pointer' if a=='point-right' and kind in ['curves','huber','siglip'] and (kind!='siglip' or actor_index==0) else a),'fps':10,'frames':PLAYBACK[a],'phase':actor_index*2 if kind=='focal' else 0,'blink_every_cycles':4 if a=='talk' else 1} for i,(t,a) in enumerate(changes)]

def sample_actor(actor,t):
    clip=next((c for c in reversed(actor['clips']) if c['start']<=t+1e-8),actor['clips'][0])
    steps=max(0,math.floor((t-clip['start'])*clip['fps']+1e-7))+clip['phase']
    sequence=clip['frames'];cycle=steps//len(sequence);frame=sequence[steps%len(sequence)]
    if clip['action']=='talk' and frame==5 and cycle%clip['blink_every_cycles']!=0:frame=6
    return {'id':actor['id'],'action':clip['action'],'sprite_frame':frame,'atlas_rect':[frame%4*384,frame//4*576,384,576]}
