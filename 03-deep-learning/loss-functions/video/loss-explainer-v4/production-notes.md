# 作者序列帧版 V4：制作与复用

> 历史制作记录：此版生成的 MP4 已于 2026-10-02 清理，源码、分镜与素材保留。观看当前成片请访问 [V6 发布入口](../README.md)。

本版为作者制作五组透明动作，并重新渲染完整视频。人物会说话、眨眼、伸手指向、托腮、开心握拳和挥手。内容与作者参考音色沿用 V3；原配音的每分钟 320 字节奏保持一致，V4 没有新增语音生成请求。

## 素材与动画

内置 `image_gen` 共六次生成：五组动作，以及一次思考动作连续性修正。有效动作库共 60 张透明 PNG、59 张独立图像，每帧 384 × 576，默认 10 fps；图集 4 列 × 3 行，1536 × 1728。思考组的第 10 张源姿势出现另一只手，编排时使用本组第 3 张源姿势完成同一只手的回落，12 张导出帧中有一张复用。初稿与修正版原图都保存，预览与视频使用经过编排的活动图集。

所有被接受的动作首先缓存到项目根目录 `assets/手绘形象/shikanon-animation-v1/`，再同步到本视频 `assets/author-animation/`。可复用内容包括原始参考、原始生成图、图集、单帧、WebP 预览、提示词、便携预览页和 `manifest.json`。每张帧图与图集记录 SHA-256；录像内副本与缓存逐文件核验一致。

[素材预览](assets/author-animation/preview.html)支持播放、暂停、速度调整、逐帧拖动与深色背景；[配置](assets/author-animation/manifest.json)给出帧坐标、脚底锚点与来源。[人物动作编排](author_motion.py)把动作切换映射到实际语音词时间。27 个人物实例在开场、公式比较、异常值、Huber、Focal、对比学习、DPO、自蒸馏、总结与片尾中使用动作。原来只对整张 PNG 轻跳、转动的装饰动作已由姿势帧替代。

## 本版核验

严格检查 23 个布局采样与 96 处文字对比度，零布局问题、运行错误和对比度警告。原全局 SVG 样式会误把嵌套人物视口放大，已将样式限定到图解根 SVG，并重新验证实际开场和片尾画面。

通过真实浏览器时间轴检查全部 5,370 帧，另做 12 次反向跳转；核对 6,116 个可见人物状态，动作名称、帧编号与 SVG 图集窗口零不一致。每个人物至少出现 8 种姿势。另在 186 个运动时刻检查 301 个人物边界，人物未超出画面、未覆盖可见图解文字。透明帧均留有安全边距，缓存与视频副本一致。详见 `qa/runtime-sprite-audit.json` 与 `qa/character-geometry-audit.json`。

新成片为 H.264 / AAC、1080 × 1920、30 fps、179 秒，5,370 帧与 17 个原生章节；大小 15,531,619 字节，完整解码零错误。分别从新 MP4 的固定人物区域抽取五组动作前后帧，确认嘴型、眼睛和手势真实改变；本地 实际动作对比（`qa/animation-contact.jpg`）来自本次新成片。五个缓存 WebP 均为 12 帧、1,200 ms 循环。成片二维码在全分辨率及 540 × 960 下均可识别。

实际播放器逐个验证 17 个小节和 3 个大章按钮，时间与标题匹配，均为 `readyState=4`；物理拖动定位至 149.54 秒，键盘 End 定位 179 秒。以 1×、未静音从头连续播放，中途未跳转，最终 `ended=true`、时间 179 秒、媒体错误为空。390 × 844 下播放器无横向溢出，视频宽 352 px；动作库无横向溢出，Canvas 宽 336 px。五组动作切换、逐帧、速度、暂停继续与背景切换均验证，浏览器没有相关控制台错误或警告。检查后清除临时手机尺寸，视频回到开头暂停。

媒体、动作与播放结果分别记录在 `qa/delivery-validation.json`、`qa/animation-validation.json` 和 `qa/player-playback.json`。验收基于新导出的 MP4，原版视频文件保留。

## 重渲染

使用现有 Python、Node.js、HyperFrames 0.8.78 和 FFmpeg。OpenCV、NumPy、Pillow 仅用于帧定位、元数据与验收。已缓存素材和已保留配音可直接渲染，无需再次调用生成服务。

```bash
python3 sync_author_library.py
python3 build_composition.py
python3 make_player.py
npx --yes hyperframes@0.8.78 check --samples 23 --strict
npx --yes hyperframes@0.8.78 render --output renders/loss-functions-v4-master.mp4 --quality high --fps 30 --workers 4 --gpu
ffmpeg -y -i renders/loss-functions-v4-master.mp4 -map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 19 -threads 8 -pix_fmt yuv420p -c:a copy -movflags +faststart renders/loss-functions-v4.mp4
python3 embed_chapters.py --ffmpeg ffmpeg
ffmpeg -y -ss 3.15 -i renders/loss-functions-v4.mp4 -frames:v 1 -vf scale=540:-1 assets/poster.jpg
python3 serve_player.py --background
```

本机入口为 `http://127.0.0.1:8770/video/loss-explainer-v4/watch.html`。配音、成片与 QA 按仓库规范保留为本地媒体；V1、V2、V3 未覆盖。知识点文章独立阅读体验保持完整。

## 后续视频直接取用

```bash
python3 sync_author_library.py --destination /新视频目录/assets/author-animation
```

此命令先核对缓存哈希，再复制完整动作包并逐文件核对，不调用任何生成 API。若产生新动作，应使用新的动作名称或素材库版本，保留旧素材。`register_sprite.py` 用于接受新生成图，自动缓存和同步；原始生成图优先保留，帧不能被名义网格边界截断。
