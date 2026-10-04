"""Build a portable preview that reads the cached PNG sequence directly."""
import argparse
import json
import shutil
from pathlib import Path

B = Path(__file__).resolve().parent
L = B.parents[3] / 'assets/手绘形象/日常服动作序列帧'
parser = argparse.ArgumentParser()
parser.add_argument('--no-sync', action='store_true')
args = parser.parse_args()
M = json.loads((L / 'manifest.json').read_text())
preview = {
    'frame_size': M['frame_size'],
    'actions': {key: {'fps': item['fps'], 'frame_count': item['frame_count'],
                      'frames': [frame['file'] for frame in item['frames']]}
                for key, item in M['actions'].items()},
}
page = r'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>日常服动作序列帧</title>
<style>
*{box-sizing:border-box}body{margin:0;color:#46392f;background:#fff7e4;font-family:system-ui,-apple-system,sans-serif}main{max-width:950px;margin:30px auto;padding:0 22px}h1{font-size:29px;margin:0 0 12px}p{line-height:1.7;color:#66574a}a{color:#46392f}.layout{display:grid;grid-template-columns:minmax(260px,340px) 1fr;gap:36px}.stage{border:2px solid #46392f;border-radius:16px;overflow:hidden;background-color:#fffcf3;background-image:linear-gradient(45deg,#eee6d7 25%,transparent 25%),linear-gradient(-45deg,#eee6d7 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#eee6d7 75%),linear-gradient(-45deg,transparent 75%,#eee6d7 75%);background-size:24px 24px;background-position:0 0,0 12px,12px -12px,-12px 0}.stage.dark{background:#25313b}canvas{display:block;width:100%;height:auto}.controls,.actions{display:flex;flex-wrap:wrap;gap:9px;margin:16px 0}button,select{font:inherit;font-size:14px;border:1.5px solid #46392f;border-radius:9px;padding:9px 12px;background:#fffcf3;color:#46392f;cursor:pointer}button[aria-pressed=true]{background:#edcd74}input{width:100%;accent-color:#ed826a}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #73a6a3;outline-offset:3px}.info{border:1px solid #d2c7ae;border-radius:14px;background:#fffcf3;padding:20px}.status{display:flex;justify-content:space-between;font-size:14px;margin:12px 0}.error{color:#a13c27}@media(max-width:680px){main{padding:0 18px}.layout{grid-template-columns:1fr;gap:24px}.preview{width:100%;max-width:340px;margin:auto}h1{font-size:25px}}
</style></head><body><main><h1>日常服动作序列帧</h1><p>固定闭嘴微笑 · 八组透明 PNG 动作<br><a href="README.md">复用说明</a> · <a href="manifest.json" download>下载帧序清单</a></p>
<div class="layout"><section class="preview"><div class="stage" id="background"><canvas id="stage" width="384" height="576" aria-label="作者 PNG 序列帧预览"></canvas></div><div class="controls"><button id="play">暂停</button><label>速度 <select id="speed" aria-label="播放速度"><option value="0.5">0.5×</option><option value="1" selected>1×</option><option value="1.5">1.5×</option></select></label><button id="theme">深色背景</button></div><label for="frame">拖动查看每一帧</label><input id="frame" aria-label="动画帧" type="range" min="0" max="23" step="1" value="0"><div class="status"><span id="counter">加载中</span><span id="fps"></span></div><a id="download" download>下载当前 PNG</a></section>
<section><nav class="actions" aria-label="动作选择"></nav><article class="info"><h2 id="name"></h2><p id="purpose"></p><p>每组 24 帧 · 384×576 · 20 fps<br>脚底锚点：192, 548<br>教棍新场景优先选择博士服素材。</p></article><p id="error" class="error" hidden></p></section></div></main><script>
const LIB=__MANIFEST__;
const labels={talk:['讲解','开掌讲解与轻微点头。'], 'point-right':['指向','徒手指向图表与重点。'],think:['思考','托腮思考与轻轻歪头。'],celebrate:['领悟','握拳抬至脸侧，表示理解后的反馈。'],wave:['挥手','用于欢迎和项目片尾。'],'think-question':['思考问号','用头顶问号提示当前疑问。'],'teach-pointer':['日常服教棍','保留已有视频的教棍动作。'],step:['轻步','左右脚交替轻抬与重心移动。']};
const canvas=document.getElementById('stage'),ctx=canvas.getContext('2d'),slider=document.getElementById('frame'),play=document.getElementById('play');
const cache={};let action='talk',index=0,playing=true,ready=false,origin=performance.now(),rate=1;
function draw(){if(!ready)return;const m=LIB.actions[action];ctx.clearRect(0,0,...LIB.frame_size);ctx.drawImage(cache[action][index],0,0);slider.value=index;document.getElementById('counter').textContent='帧 '+String(index+1).padStart(2,'0')+' / '+m.frame_count;document.getElementById('download').href=m.frames[index];canvas.dataset.action=action;canvas.dataset.frame=index;}
async function choose(key){action=key;index=0;ready=false;slider.max=LIB.actions[key].frame_count-1;document.getElementById('fps').textContent=LIB.actions[key].fps+' fps · 循环';document.getElementById('name').textContent=labels[key][0];document.getElementById('purpose').textContent=labels[key][1];document.getElementById('counter').textContent='加载中';document.querySelectorAll('.actions button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.action===key));try{if(!cache[key])cache[key]=await Promise.all(LIB.actions[key].frames.map(async file=>{const image=new Image();image.src=file;await image.decode();return image;}));if(action!==key)return;ready=true;canvas.dataset.loaded=cache[key].length;origin=performance.now();draw();}catch(error){document.getElementById('error').hidden=false;document.getElementById('error').textContent='PNG 帧未加载，请保留完整 frames 文件夹。';}}
for(const key of Object.keys(LIB.actions)){const button=document.createElement('button');button.type='button';button.dataset.action=key;button.textContent=labels[key][0];button.onclick=()=>choose(key);document.querySelector('.actions').append(button);}
play.onclick=()=>{playing=!playing;play.textContent=playing?'暂停':'播放';origin=performance.now()-index/LIB.actions[action].fps/rate*1000;};
slider.oninput=()=>{playing=false;play.textContent='播放';index=Number(slider.value);draw();};
document.getElementById('speed').onchange=e=>{rate=Number(e.target.value);origin=performance.now()-index/LIB.actions[action].fps/rate*1000;};
document.getElementById('theme').onclick=e=>{document.getElementById('background').classList.toggle('dark');e.target.textContent=document.getElementById('background').classList.contains('dark')?'浅色背景':'深色背景';};
function tick(now){if(playing&&ready){index=Math.floor(Math.max(0,now-origin)/1000*LIB.actions[action].fps*rate)%LIB.actions[action].frame_count;draw();}requestAnimationFrame(tick);}choose('talk');requestAnimationFrame(tick);
</script></body></html>'''
(L / 'preview.html').write_text(page.replace('__MANIFEST__', json.dumps(preview, ensure_ascii=False).replace('<', '\\u003c')))
if not args.no_sync:
    shutil.copytree(L, B / 'assets/author-animation', dirs_exist_ok=True)
print('PNG sequence preview saved' + (' and synced' if not args.no_sync else ''))
