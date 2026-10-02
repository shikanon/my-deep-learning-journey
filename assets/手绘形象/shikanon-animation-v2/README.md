# 作者手绘动作库 V2

本版修复 V1 的头部漂移、身体比例变化与动作切换跳动。人物共用一张透明底稿，头发轮廓、衣服主体和双脚保持固定；保留原动作中的嘴型、眨眼和手臂。另有教棍与头顶问号两个场景动作。

- [七组动作交互预览](preview.html)：播放 / 暂停、逐帧、速度、背景切换
- [完整动作配置](manifest.json)
- [统一人物底稿](registration/reference-neutral.png) · [配准参数与来源帧](registration/parameters.json)
- [独立问号 SVG](props/question.svg) · [独立教棍 SVG](props/teaching-pointer.svg)
- 生成来源为 V1，原图与提示词保存在仓库公共素材 `assets/手绘形象/shikanon-animation-v1/`。

| 动作 | 用途 | 图集 | 循环预览 |
| --- | --- | --- | --- |
| talk | 嘴型、开掌讲解、眨眼 | [PNG](atlases/talk.png) | [WebP](previews/talk.webp) |
| point-right | 徒手指向重点 | [PNG](atlases/point-right.png) | [WebP](previews/point-right.webp) |
| think | 托腮思考 | [PNG](atlases/think.png) | [WebP](previews/think.webp) |
| celebrate | 双手握拳、领悟 | [PNG](atlases/celebrate.png) | [WebP](previews/celebrate.webp) |
| wave | 挥手欢迎、片尾 | [PNG](atlases/wave.png) | [WebP](previews/wave.webp) |
| think-question | 头顶问号、提出疑问 | [PNG](atlases/think-question.png) | [WebP](previews/think-question.webp) |
| teach-pointer | 教棍讲解曲线、师生场景 | [PNG](atlases/teach-pointer.png) | [WebP](previews/teach-pointer.webp) |

每组 12 帧、10 fps，共 84 张透明 PNG。单帧为 384 × 576，图集为 4 列 × 3 行、1536 × 1728。每组第 0 与第 11 帧回到同一人物底稿，问号组保留头顶符号。所有帧均在固定画布中导出，使用者应直接按 `atlas_rect` 取帧，不再根据每帧的透明边界裁切或居中。嘴型属于节奏动画，没有逐音素对齐语音。

```js
const action = library.actions['teach-pointer'];
const frame = action.frames[index];
ctx.drawImage(atlas, ...frame.atlas_rect,
  x - 192, y - 548, 384, 576);
```

`x, y` 为固定画布的放置锚点。动作切换时保持位置和缩放相同；暂停或跳转使用目标时间算帧号。教棍在序列帧中已绘制，手掌会遮挡木杆，问号也已绘制，无需再次叠加。独立 SVG 供其他场景需要时使用。

修复使用现有 `image_gen` 动作素材做确定性配准和合成，新增绘图请求为 0。原始参考、生成图及提示词保留在 V1；V2 可以直接复用，无须重新生成。
