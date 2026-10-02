# shikanon · 手绘人物动作库

这套素材供“我的深度学习之路”视频重复使用。动作通过内置 `image_gen` 以作者原始手绘形象为参考生成；单帧改变嘴型、眼睛与手臂姿势。首次用于损失函数 V4。

- [播放与逐帧预览](preview.html)
- [动作配置与 SHA-256](manifest.json)
- [身份参考图](reference.png)

| 动作 | 文件名 | 用法 | PNG 帧数 |
| --- | --- | --- | ---: |
| 讲解 | `talk` | 嘴型变化、开掌讲解、眨眼 | 12 |
| 指向 | `point-right` | 指向图表、评分与回答卡片 | 12 |
| 思考 | `think` | 托腮、看向上方、思考问题 | 12 |
| 领悟 | `celebrate` | 双拳抬到脸侧，理解后的开心反馈 | 12 |
| 挥手 | `wave` | 手腕摆动，欢迎或项目片尾 | 12 |

每帧为 **384 × 576 的透明 PNG**。默认按 10 fps 播放，4 列 × 3 行图集为 1536 × 1728。脚底锚点统一为 `(192, 548)`，切换动作时使用相同的锚点与缩放。讲解嘴型是节奏动画，未逐音素对齐配音。

原始生成图放在 `atlases/*-generated.png`，可直接消费的图集为 `atlases/<动作>.png`，单帧为 `frames/<动作>/000.png` 至 `011.png`，循环预览为 `previews/<动作>.webp`。`prompts/` 保留全部提示词，`manifest.json` 记录来源、实际裁切位置、帧尺寸、锚点与文件哈希。

“思考”初稿中途换手，保留为 `atlases/think-generated-draft.png`，不在活动动作配置中。修正版仍有一张回落帧使用另一只手，编排时用该组第 3 张源姿势替换回落过渡。因此这组 12 张导出帧有 11 张独立图像，五组共 60 张 PNG、59 张独立图像。全部活动动作保持同一只手完成其主要手势。

## 下次视频直接使用

复制整个文件夹到新视频工程的 `assets/author-animation/`，读取配置，按动作名称选图集和帧。文件路径均相对于本文件夹，预览页可以直接打开，无需生成服务或联网。

```javascript
const action = manifest.actions['point-right'];
const frame = action.frames[frameIndex % action.frame_count];
// atlas 已加载为 HTMLImageElement，x、y 为人物脚底位置。
ctx.drawImage(atlas, ...frame.atlas_rect, x - 192, y - 548, 384, 576);
```

动画切换最好安排在回落或自然停顿处；讲解循环可减少眨眼帧出现频率。视频工程使用 SVG 图集视口与 GSAP 的离散帧选择，拖动和导出使用同一时间轴，避免预览与成片不同步。

本次视频内的副本位于 `03-deep-learning/loss-functions/video/loss-explainer-v4/assets/author-animation/`。制作脚本 `register_sprite.py` 每次把接受的素材先写入本素材库，再同步到视频工程；以后新增动作应保留新名称或新版本，避免覆盖已使用的素材。
