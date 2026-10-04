"""Build a deterministic, model-driven teaching composition from accepted word times."""
import base64
import hashlib
import json
import re
from pathlib import Path

B = Path(__file__).resolve().parent
ROOT = B.parents[3]
# Accepted speech, subtitles and libraries are local inputs of the final project.
for name in ('timeline.json', 'narration.json', 'captions.srt', 'research.md',
             'chapters.ffmetadata', 'hyperframes.json', 'assets/gsap.min.js'):
    if not (B / name).exists():
        raise FileNotFoundError(f'Missing retained project input: {name}')
for folder in ('assets', 'audio', 'qa', 'renders'):
    (B / folder).mkdir(exist_ok=True)
D = json.loads((B / 'timeline.json').read_text())

# Every action answers one question and is bound to an actual spoken phrase.
PLAN = [
('参数那么多，怎样一起算？', '为什么一遍反传能得到多个参数的梯度？', [
 ('many', '上亿个参数', '参数共同进入一次模型计算'),
 ('trial', '逐个拧一下', '逐个试探需要重复运行模型'),
 ('reuse', '反着走一遍', '沿共同计算的原路径返回多个梯度'),
 ('example', '一道能手算的小题', '缩小为两个参数，接着亲手计算')]),
('前向：把数值算出来', '损失 4.5 是怎样从输入 2 得到的？', [
 ('input', '输入是二', '先给出输入与目标'),
 ('structure', '模型用权重', '固定计算图中的变量位置'),
 ('params', '权重是一', '把 w=1、x=2 送入乘法'),
 ('prediction', '预测就是二', '乘法结果与 b=0 相加得到预测 2'),
 ('residual', '与目标相差负三', '预测 2 减目标 5 得到误差 −3'),
 ('loss', '把误差平方', '−3 平方得到 9，再除以 2 得到 4.5'),
 ('cache', '中间结果记下来', '在原节点旁保存本次前向的值'),
 ('responsibility', '责任并不相同', '同一损失连接不同的参数路径')]),
('梯度：小步改变会怎样？', '负梯度为什么提示增加参数？', [
 ('base', '错了多少', '用同一模型生成损失曲线和当前点'),
 ('direction', '朝哪边动', '在 w=1 处画局部切线'),
 ('gradient', '梯度是负六', '切线斜率与解析梯度一致'),
 ('small', '小幅增加权重', '沿曲线把 w 从 1 移到 1.2，损失随模型降到 3.38'),
 ('local', '局部路标', '展示大步越过最低点，不能保证下降'),
 ('sensitivity', '不同参数', '比较该位置的两项梯度大小')]),
('差分：真的重跑两次', '两个邻近损失怎样近似给出梯度？', [
 ('perturb', '加减一点', '放大 w=1 附近，运行 w−ε 与 w+ε 两次'),
 ('quotient', '近似算出斜率', '先形成损失差，再除以参数间距'),
 ('cost', '每个参数都重跑', '三个参数各做两次前向，总数从 2 增到 6'),
 ('epsilon', '步子太大', '标出步长控制的两种误差来源'),
 ('reuse', '复用共同的计算', '提出复用共同图的下一步')]),
('链式法则：影响沿路相乘', '损失的影响怎样先到达误差节点？', [
 ('graph', '拆成计算图', '沿用同一张前向图'),
 ('rules', '自己的求导规则', '局部规则附在对应运算与边上'),
 ('product', '相邻影响相乘', '把上游影响与这一段局部导数相乘'),
 ('seed', '损失对误差', '从 ∂L/∂L=1 开始，乘 r=−3'),
 ('residual', '先传回负三', '梯度 −3 沿损失到误差的原边返回')]),
('反向：沿原图返回梯度', '为什么偏置是 −3，权重却是 −6？', [
 ('prediction', '预测加一', '误差对预测的局部导数为 1，−3 返回预测'),
 ('bias', '偏置加一', '沿偏置支路乘 1，得到偏置梯度 −3'),
 ('weight', '权重加一', '沿乘法支路乘输入 2，得到权重梯度 −6'),
 ('summary', '几次小乘法', '两个参数都收到来自同一个损失的影响')]),
('更新：梯度变成参数变化', '减去负梯度后，参数与损失怎样变？', [
 ('gradients', '只算梯度', '保持原参数，显示反传结果'),
 ('optimizer', '减去学习率', '单独启动优化器，代入 η=0.1'),
 ('parameters', '权重变成一点六', '用减法公式生成 w=1.6、b=0.3'),
 ('prediction', '重新预测', '重新代入参数计算预测 3.5 与误差 −1.5'),
 ('loss', '损失降到', '以相同刻度把损失条从 4.5 缩到 1.125'),
 ('sign', '减去负数', '突出减去负梯度对应的正方向位移')]),
('分支：两条贡献回到同一变量', 'x²+x 的两条影响为什么要相加？', [
 ('graph', '走了两条路', '一个 x 分流到平方与直接相加'),
 ('forward', '输入是二', '前向分别得到 4 与 2，合为输出 6'),
 ('square', '平方这条路', '输出影响沿平方原路径返回 2x=4'),
 ('identity', '直接相加', '沿另一条原路径返回 1'),
 ('sum', '汇总就是五', '两份贡献进入同一个 x，4+1=5'),
 ('complete', '必须相加', '保持输出 6 与导数 5 的区别')]),
('误差如何指导隐藏层？', '隐藏层怎样收到来自输出的误差信号？', [
 ('program', '早期自动微分', '先说明局部规则来自程序运算'),
 ('paper', '一九八六年', '给出 1986 年经典应用的出处'),
 ('hidden', '隐藏单元', '展示输入、隐藏单元和输出的固定结构'),
 ('learning', '误差指导', '误差信号沿连接返回可训练权重，指导内部表示')]),
('模式：变化往哪边传播？', '很多输入、一个损失时，哪种传播更省重复？', [
 ('forward', '前向模式', '从输入方向 (1,0,0) 向前传播变化'),
 ('reverse', '反向模式', '从一个输出种子 1 反向得到全部三个偏导'),
 ('dimensions', '很多参数', '并排比较本例 3 个输入方向与 1 个输出'),
 ('rules', '按规则计算导数', '说明两种模式都执行求导规则')]),
('框架：把梯度放进缓冲区', '第二次 backward 后为什么会变成 −12？', [
 ('code', '标记参数', '逐行对应 requires_grad、前向和 backward'),
 ('read', '读出梯度', '同一例子读出 w.grad=−6、b.grad=−3'),
 ('batch', '新批次', '每个批次重新前向，产生自己的计算图'),
 ('accumulate', '累计到梯度缓冲区', '两次 −6 依次进入同一个缓冲区，0→−6→−12'),
 ('clear', '先清空', '独立更新前清零，下一批重新得到 −6'),
 ('mean', '分批累计', '两批等大小、参数不变，loss/2 后各贡献 −3'),
 ('scale', '正确缩放损失', '平均目标的梯度为 −3+(−3)=−6')]),
('闭环：每一步各做什么？', '数值、梯度与更新分别发生在哪一步？', [
 ('forward', '前向算数值', '从固定参数得到损失 4.5'),
 ('reverse', '反向算梯度', '同图反向得到 −6 与 −3'),
 ('update', '优化器更新参数', '优化器把参数变为 1.6 与 0.3'),
 ('check', '梯度检查', '将差分结果与自动微分结果对照')]),
('检查点：缺少的值怎样找回？', '少保存的激活，在反传需要时从哪里来？', [
 ('need', '中间值', '示例链路产生 a₁=4、a₂=5、a₃=25、输出 5'),
 ('all', '保存的激活', '逐步装入四个保存槽，显示占用增加'),
 ('checkpoint', '只保留部分信息', '保留输入 a₀=2，清除其他保存槽'),
 ('recompute', '重新计算', '反传需要 a₂ 时，从 a₀ 重算两步，恢复 a₂=5'),
 ('trade', '额外计算', '对照本例的保存槽与新增运算次数')]),
('选择性保存：重算便宜操作', '保存矩阵乘法后，怎样重建后续激活？', [
 ('policy', '哪些保存', '先显示同一条含昂贵和便宜操作的链'),
 ('expensive', '昂贵运算', '计算矩阵乘法 [4,−5] 并保存结果'),
 ('cheap', '便宜的逐元素操作', '前向 ReLU 得到 [4,0]，该激活允许丢弃'),
 ('compiler', '联合分析', '反向需要 ReLU 输出，从缓存重算 [4,0]，再求 2a'),
 ('measure', '依赖模型和硬件', '用同一模型与硬件测显存、吞吐、质量')]),
('保留、重算、压缩：怎样取舍？', '压缩减少存储时，为什么还要检查误差？', [
 ('research', '二零二五年', '给出 Adacc 研究与三种选择'),
 ('choices', '同一套选择', '追踪同一张量在保留、重算与压缩后的不同状态'),
 ('error', '可能引入误差', '用舍入示意原值与恢复值的可见差异'),
 ('quality', '训练质量', '把误差、速度与存储放在同一比较条件下'),
 ('objective', '一起衡量', '强调同一目标与设置的比较'),
 ('mechanism', '链式法则', '返回原图，梯度规则不变，改变存储与执行')]),
('继续一起学懂下一步', '观众在哪里继续学习？', [
 ('project', '开源项目', '显示可读的项目地址'),
 ('content', '文章', '显示文章、原始论文和实验代码'),
 ('star', '点亮星标', '作者挥手，项目文字卡静止收尾')]),
]

def norm(t):
    return ''.join(re.findall(r'[\u4e00-\u9fff]', t))

for scene, (title, question, steps) in zip(D['scenes'], PLAN, strict=True):
    scene['title'] = title
    scene['question'] = question
    scene['steps'] = []
    source = norm(scene['text'])
    for key, cue, meaning in steps:
        assert norm(cue) in source, (scene['id'], cue)
        idx = source.index(norm(cue))
        start = scene['words'][idx]['start']
        scene['steps'].append(dict(id=key, cue=cue, start=start, meaning=meaning))
    for i, step in enumerate(scene['steps']):
        nxt = scene['steps'][i + 1]['start'] if i + 1 < len(scene['steps']) else scene['end']
        step['duration'] = round(max(.25, min(1.15, (nxt - step['start']) * .75)), 5)
        step['frame_start'] = round(step['start'] * D['fps'])
        step['frame_end'] = round((step['start'] + step['duration']) * D['fps'])

definitions = []
packs = [('doctor', ROOT / 'assets/手绘形象/博士服教棍-v1'),
         ('wave', ROOT / 'assets/手绘形象/日常服动作序列帧')]
sources = []
for key, pack in packs:
    m = json.loads((pack / 'manifest.json').read_text())
    if key == 'doctor':
        frames = m['frames']; width = m['frameSize']['width']; height = m['frameSize']['height']
        anchor = [m['anchor']['x'], m['anchor']['y']]; fps = m['fps']
    else:
        frames = [f['file'] for f in m['actions']['wave']['frames']]
        width, height = m['frame_size']; anchor = m['anchor']; fps = m['actions']['wave']['fps']
    record = dict(id=key, path=str(pack.relative_to(ROOT)), canvas=[width,height],
                  anchor=anchor, fps=fps, frames=[])
    for i, f in enumerate(frames):
        raw = (pack / f).read_bytes()
        record['frames'].append(dict(file=f,sha256=hashlib.sha256(raw).hexdigest()))
        definitions.append(f'<image id="{key}-{i}" width="{width}" height="{height}" href="data:image/png;base64,{base64.b64encode(raw).decode()}"/>')
    sources.append(record)
D['actor_sources'] = sources
(B / 'timeline.json').write_text(json.dumps(D, ensure_ascii=False, indent=2) + '\n')
(B / 'timeline-data.js').write_text('window.VIDEO_DATA=' + json.dumps(D,ensure_ascii=False,separators=(',',':'))+';\n')
(B / 'asset-provenance.json').write_text(json.dumps(dict(storage='transparent-png-sequence',direct_root_reads=True,packs=sources),ensure_ascii=False,indent=2)+'\n')

html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>反向传播与自动微分 · 过程优化版</title><link rel="stylesheet" href="style.css"></head><body><div id="main" data-composition-id="main" data-start="0" data-duration="{D['duration']}" data-width="1080" data-height="1920" data-fps="30"><svg class="definitions" data-layout-ignore aria-hidden="true"><defs>{''.join(definitions)}</defs></svg><div class="paper-edge" data-layout-ignore></div><div id="rail"></div><div id="scene-count"></div><h1 id="title"></h1><div id="phase"></div><svg id="diagram" viewBox="0 0 950 1000" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="当前知识点的计算过程"></svg><svg id="author" viewBox="0 0 512 512" aria-hidden="true"><use id="author-frame" href="#doctor-0"/></svg><div id="insight"><strong></strong><p></p></div><div id="captions"><span></span></div><footer><span>我的深度学习之路</span><span>蓝绿：前向数值 · 珊瑚：反向梯度</span></footer></div><script src="assets/gsap.min.js"></script><script src="timeline-data.js"></script><script src="animation.js"></script></body></html>'''
# No audio processing in the renderer: mux the accepted final AAC without re-encoding.
html=html.replace('<script src="animation.js"></script>', '<script>\n'+(B/'animation.js').read_text()+'\n</script>')
html=html.replace('蓝绿：前向数值 · 珊瑚：反向梯度','前向看数值，反向看影响')
(B / 'index.html').write_text(html)
story = dict(fps=D['fps'],duration=D['duration'],frame_count=round(D['duration']*D['fps']),
             model='Deterministic scalar/vector computation; time sampled at frame / fps; data drives positions, values and paths.',
             sources=sources,scenes=[{k:s[k] for k in ('id','title','kind','start','end','question','steps')} for s in D['scenes']])
(B / 'storyboard.json').write_text(json.dumps(story,ensure_ascii=False,indent=2)+'\n')
rows=['# 优化版分镜','', '每个过程都绑定现有配音逐词时间。相同变量在前向和反向保持位置。梯度沿实际运算边返回；输出、导数和参数更新分开标识。', '', '| 小节 | 理解问题 | 可观察过程 |', '| --- | --- | --- |']
for s in story['scenes']:
    rows.append(f'| {s["id"]} {s["title"]} | {s["question"]} | '+'；'.join(f'{st["start"]:.2f}s：{st["meaning"]}' for st in s['steps'])+' |')
(B / 'storyboard.md').write_text('\n'.join(rows)+'\n')
print(json.dumps(dict(scenes=len(D['scenes']),steps=sum(len(s['steps']) for s in D['scenes']),frames=story['frame_count'],actor_frames=sum(len(s['frames']) for s in sources)),ensure_ascii=False))
