# 固定微笑人物动画的复用

V3 保持作者的彩铅手绘身份，整张脸共用一张闭嘴微笑头部图。嘴型与眼睛不做逐帧变形；头部围绕领口轻点、歪头，手势、脚步及持有的教棍承担主要动作。

八组动作：`talk` 讲解手势、`point-right` 徒手指向、`think` 托腮思考、`celebrate` 领悟握拳、`wave` 挥手、`think-question` 思考问号、`teach-pointer` 持教棍、`step` 轻步。`talk` 保留旧标识以兼容使用方，表示讲解手势，不含口型动画。

每组 24 帧、20 fps、1.2 秒循环；单帧 384 × 576 RGBA 真透明，图集 6 列 × 4 行，2304 × 2304。`frames/` 为全部 192 张 PNG，`atlases/` 为八张图集，`previews/` 为八个 WebP。`rig/` 保留固定头部、嘴部参考、左右腿、人物底稿与问号图层。`props/` 保留教棍和问号 SVG。

人物放置锚点统一为 `[192, 548]`。身体和人物比例固定，头部旋转幅度不超过 2.5°；脚部围绕腿的关节做小幅重心和抬脚动作。这些是配置明确、可重现的动作，不按各帧的外包围框重新居中。每组首尾一致，基础动作共用同一中立姿势；思考问号额外保留顶部道具。

```javascript
const action = manifest.actions['teach-pointer'];
const index = Math.floor(timeSeconds * action.fps) % action.frame_count;
const frame = action.frames[index];
ctx.drawImage(atlas, ...frame.atlas_rect, x - 192, y - 548, 384, 576);
```

先绘制透明帧，再按实际场景安排位置。不同动作可以用同一个画布坐标和锚点切换。若需要连续场景切换，优先在首尾中立帧切换；不要给每张帧图另算包围框中心。嘴部随整颗头移动，但表情和形状始终来自同一张参考图。

来源为 V2 已配准的手绘素材，使用确定性关节变换和透明合成，无新增图片生成调用。重建脚本为仓库 `03-deep-learning/loss-functions/video/loss-explainer-v6/rig_author.py`。后续视频直接复制此文件夹，不必重新生成；`sync_author_library.py --destination <新视频素材目录>` 会同时核对 SHA-256。

全帧验收包括：实际嘴部像素与同一参考头部变换后的像素一致、身体纹理固定、关节角度连续、循环首尾一致、无边缘裁切，以及公共库和视频副本逐文件一致。结果位于视频工程 `qa/rig-validation.json`。
