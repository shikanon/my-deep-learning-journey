# V5 制作与验收记录

> 历史制作记录：此版生成的 MP4 已于 2026-10-02 清理，源码、分镜与素材保留。观看当前成片请访问 [V6 发布入口](../README.md)。

本版修复作者序列帧抖动，新增教棍和头顶问号，并重新渲染完整视频。内容与配音复用 V3，作者参考音色与每分钟 320 字的节奏保持不变。本次新增图像、音频生成调用均为 0。

## 为什么上一版会抖动

V4 仅按鞋底位置统一各帧。原始姿势中，头部相对鞋底的位置、尺寸与身体比例仍会变化。用同一头部特征区域估计，讲解组的头部横向跨度约 12.8 px，指向组约 46.5 px，思考组约 38.9 px，挥手组约 36.1 px。这些数值包含原图的转头与尺度差异；只统一导出画布或在配置里写同一个锚点，不能修复它们。

V5 使用同一张透明人物底稿，对已有图进行确定性配准与合成。头发轮廓、衣服主体与双脚固定；嘴型、眨眼与原手势继续变化。身体变换受腰部宽度和领口高度约束，避免思考手势遮挡衣服后导致错误的拉伸或倾斜。前景托腮手与双手握拳保留在人物前方。五组基础动作第 0、11 帧共用相同底稿，动作切换时保持统一比例。

## 可复用素材

公共库位于仓库根目录 `assets/手绘形象/shikanon-animation-v2/`，视频副本位于 `assets/author-animation/`。七组动作、84 张透明 PNG，每组 12 帧、10 fps，单帧为 384 × 576，图集为 1536 × 1728。七个 WebP 均为 12 帧、1,200 ms 循环。另存道具 SVG、参考底稿、配准参数、来源帧号、SHA-256、便携动作预览页和复用说明。106 个文件逐字节核对一致。V1 原始图、提示词与 V4 成片保留。

曲线、Huber 与 SigLIP 2 老师使用教棍；疑问、阈值和研究取舍使用头顶问号。教棍随手掌转动，被手掌遮挡；问号固定在头顶。视频里的 27 个人物实例使用六种活动片段，动作库额外保留不带问号的思考片段，方便其他视频使用。嘴型是节奏动画，未逐音素对齐配音。

## 实际验证

- 原始帧图：检查全部 84 张 PNG 的头发、衣服主体与双脚三个区域，像素内容一致，模板匹配实测位移为 0 px；没有贴画布边缘的裁切。见 `qa/registration-validation.json`，以及本地 修复前后循环对比（`qa/registration-before-after.webp`）。
- 时间轴：实际浏览器检查全部 5,370 帧与 6 次反向跳转，核对 6,096 个人物状态，动作、帧号与图集窗口零不一致。见 `qa/runtime-sprite-audit.json`。
- 编码成片：从本次新 MP4 解码 129 张帧图，覆盖讲解、思考、指向、领悟与挥手；固定头发、衣服主体、双脚区域均测得 0 px 位移。另比较五种动作的前后帧，手势与嘴型仍有明显像素变化，避免用静止人物掩盖抖动。见 `qa/encoded-stability.json` 与本地 实际动作对比（`qa/animation-contact.jpg`）。
- 完整文件：H.264 / AAC，1080 × 1920，30 fps，179 秒，5,370 帧，17 个原生章节，13,566,783 字节；完整解码零错误。片尾二维码在原始分辨率与 540 × 960 下均可识别。见 `qa/delivery-validation.json`。
- 布局：Hyperframes 23 个抽样画面，严格检查通过；布局问题与运行错误为 0，96 项文字对比度检查通过。工具内置 motion 检查未启用，人物运动由独立 PNG、时间轴和编码帧检查验证。
- 浏览器：17 个小节和三个大章按钮全部跳到正确时间及标题、`readyState=4`；实际拖动定位 148.41 秒，键盘 End 定位 179 秒。七组动作切换、帧滑块、速度与背景控制均正常。390 × 844 下播放器宽 352 px、动作预览宽 336 px，均无横向溢出。临时尺寸已恢复。随后以 1×、未静音从头连续播放，中途未跳转，正常到达 179 秒、`ended=true`、`readyState=4`、媒体错误为空；浏览器无相关错误或警告。验收后视频回到开头暂停，见 `qa/player-playback.json`。

新成片 SHA-256：`2b4683f8d50ae7ee2eb24602fff85f982f5517af5af1dfef85ccb606281ccf41`。

## 重建

使用具有 OpenCV、NumPy、Pillow 的 Python 与 FFmpeg。SVG 道具用已配置的 Node / sharp 渲染；`svg_raster.py` 当前指向本机已提供的依赖路径，可在另一台机器上配置对应路径。重新配准读取保留的 V1 帧图；后续视频直接复制 V2 库即可，无须再次配准或生成。

```bash
python3 stabilize_author.py
python3 make_sprite_gallery.py
python3 build_composition.py
python3 make_player.py
python3 verify_registration.py
npx --yes hyperframes@0.8.78 check --samples 23 --strict
npx --yes hyperframes@0.8.78 render --output renders/loss-functions-v5-master.mp4 --quality high --fps 30 --workers 4 --gpu
ffmpeg -y -i renders/loss-functions-v5-master.mp4 -map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 19 -threads 8 -pix_fmt yuv420p -c:a copy -movflags +faststart renders/loss-functions-v5.mp4
python3 embed_chapters.py --ffmpeg ffmpeg
```

本机播放器为 `http://127.0.0.1:8770/video/loss-explainer-v5/watch.html`。配音、成片与 QA 按仓库规范保留为本地媒体；文章正文独立阅读不依赖视频文件。
