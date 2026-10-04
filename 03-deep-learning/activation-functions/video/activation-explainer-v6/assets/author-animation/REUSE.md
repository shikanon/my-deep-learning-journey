# 日常服动作序列帧

儿童彩铅手绘作者的日常服动作，使用同一闭嘴微笑。公共素材以透明 PNG 序列帧保存，播放与渲染直接读取 PNG，不依赖图集或 WebP。

- [八组动作预览](preview.html)
- [帧顺序、锚点与 SHA-256](manifest.json)
- [迁移来源与像素保留记录](migration-provenance.json)

| 动作 ID | 用途 |
| --- | --- |
| talk | 开掌讲解与点头；不含口型动画 |
| point-right | 徒手指向重点 |
| think | 托腮思考 |
| celebrate | 领悟握拳 |
| wave | 挥手欢迎或片尾 |
| think-question | 带问号的思考 |
| teach-pointer | 保留已有视频的日常服教棍动作；新视频教棍优先使用博士服素材 |
| step | 轻步与重心移动 |

每组 24 张 PNG，共 192 张；384×576 RGBA、20 fps、1.2 秒循环。脚底锚点统一为 `[192, 548]`。`frames/<动作>/000.png` 至 `023.png` 是原件，各组首尾一致。`rig/` 中的 PNG 参考图用于核对已有帧的头部和身体稳定性，不是图集。

```javascript
const action = manifest.actions['wave'];
const index = Math.floor(timeSeconds * action.fps) % action.frame_count;
const frame = action.frames[index];
// image 为 frame.file 指向的透明 PNG，x/y 是脚底位置。
ctx.drawImage(image, x - 192, y - 548, 384, 576);
```

本次迁移没有重新生成图片，没有修改序列帧像素；逐帧 SHA-256 与原件一致。旧公共版本目录已经删除。历史损失函数工程的必要配准输入保存在该工程本地，重建不会重新创建旧公共目录。
