# V6 制作与验收记录

本版依据“嘴不要动，主要是手、脚、头部与工具”的要求，固定整个脸部为同一张闭嘴微笑。沿用 V2 已配准的原手势，用确定性关节旋转增加轻微点头、歪头与左右脚重心运动。新增轻步动作，用于优化器更新参数。教棍随手掌运动，思考场景保留问号。V1–V5 的源码、分镜与原始素材保留，中间生成视频已清理；当前成片发布入口见 [video 索引](../README.md)。

## 素材与复用

公共库为根目录 `assets/手绘形象/shikanon-animation-v3/`，视频副本为 `assets/author-animation/`。八组动作、192 张透明 PNG，每组 24 帧、20 fps、1.2 秒循环；单帧 384 × 576，图集 6 列 × 4 行、2304 × 2304。嘴型没有动画，头部移动时嘴部随同一颗头整体移动。眼睛也不做表情切换。

`rig/` 保留固定微笑头部、嘴部参考、左右腿、中立身体和问号；`props/` 保留教棍和问号 SVG；`manifest.json` 记录每帧来源、关节矩阵、图集窗口和 SHA-256。222 个缓存文件与视频副本逐字节核对一致。后续视频直接复制 V3，无须重新生成。新增图片和配音生成调用均为 0。

配音原文件与 V3 完全一致，保留 Seed Audio 的作者参考音色和每分钟 320 字的节奏。知识主线按约 30% / 50% / 20% 排列，项目 CTA 单独计算；179 秒、17 小节、82 组图解和 101 组字幕的时间保持一致。

## 验收证据

- `qa/rig-validation.json`：192 张实际 PNG 嘴部像素与同一参考头部的对应变换一致，最大单通道差值 1/255；衣服主体像素差为 0；八组首尾一致，基础动作共用中立姿势；关节角度平滑，没有画布边缘裁切。手、头与脚的实际像素均发生变化。
- `qa/runtime-sprite-audit.json`：实际浏览器检查全部 5,370 帧和 6 次反向跳转，核对 6,093 个人物状态，帧号、图集窗口与动作均无不一致。共 27 个人物实例，七种动作在成片使用；不带问号的思考也留在素材库。
- `qa/check-final.json`：Hyperframes 严格检查 23 个时刻，布局与运行问题为 0，96 项文字对比度通过。内置 motion 检查未启用；人物动画用独立 PNG、浏览器时间轴与实际编码帧检查验证。

- `qa/encoded-stability.json`：从本次最终 MP4 解码 161 张实际画面，覆盖七种出镜动作；固定微笑与旧张嘴图作对照，所有画面都明显更接近固定微笑，闭嘴/张嘴参考误差比最高为 0.1861。身体区域在编码后保持稳定，手、头、脚与工具持续运动。
- `qa/animation-validation.json`：五组主体动作比较实际压缩前后画面，均检测到清晰的姿势变化；八个 WebP 均为 24 帧、1,200 ms。
- `qa/delivery-validation.json`：H.264 / AAC、1080 × 1920、30 fps、179 秒、5,370 帧、17 个 MP4 章节、14,175,132 字节，完整解码无错误；片尾二维码在原图与 540 × 960 下均能识别。

最终 MP4 SHA-256：`d443e69387d815f718cedfe242a77ccac5d16d513082488c9327c14fd853d8e7`。播放器以文件哈希标记媒体 URL，避免浏览器仍读取此前试片缓存。

- `qa/player-playback.json`：最终文件按哈希确认来源，以 1×、未静音从头连续播放，中途没有跳转；到达 179 秒、`ended=true`、`readyState=4`、媒体错误为空。随后用最新媒体验证 17 个小节与三个大章按钮，全部时间、标题及 `readyState=4` 正确；键盘 End 定位 179 秒。验收后回到开头暂停，浏览器无相关错误或警告。
- 八组动作按钮、24 帧滑块、1.5× 速度与背景控制均正常。390 × 844 下视频宽 352 px、动作预览宽 336 px，页面宽均为 390 px，无横向溢出；临时尺寸已恢复。

## 重建

使用具有 OpenCV、NumPy、Pillow 的 Python 与 FFmpeg。源手势读取保留的 V2 帧，不调用生成 API。

`index.html` 是带内嵌图集的构建产物，不重复提交 Git；先运行 `build_composition.py` 即可生成。文章、播放器和人物预览不依赖该构建产物。配音原始文件只留本地，迁移重建时需要准备已授权的配音。SVG 道具绘制通过 PATH 中的 Node 和 `sharp`；可用 `VIDEO_NODE`、`VIDEO_SHARP_MODULE` 指向当前机器的依赖。

```bash
python3 rig_author.py
python3 make_sprite_gallery.py
python3 verify_rig.py
python3 build_composition.py
python3 make_player.py
hyperframes check --samples 23 --strict
hyperframes render --output renders/loss-functions-v6-master.mp4 --quality high --fps 30 --workers 4 --gpu
ffmpeg -y -i renders/loss-functions-v6-master.mp4 -map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 19 -threads 8 -pix_fmt yuv420p -c:a copy -movflags +faststart renders/loss-functions-v6.mp4
python3 embed_chapters.py --ffmpeg ffmpeg
```

本机播放器为 `http://127.0.0.1:8770/video/loss-explainer-v6/watch.html`。本机已配置 Python、Node 与 FFmpeg 的完整路径；迁移到另一台机器时应配置对应依赖。大体积音视频和 QA 文件按项目规范留在本地，正文阅读不依赖视频。

## 发布与归档 · 2026-10-02

最终 V6 MP4 和封面发布到独立的 `my-deep-learning-journey/knowledge-videos/loss-functions/` 对象存储目录，以内容哈希区分文件。匿名 HEAD 为 200，Range 为 206 / 1,024 字节；完整下载 SHA-256 与上方本地最终文件一致。文章封面、视频链接和播放器均使用这份公开成片。

云端文件以 1×、未静音从头连续播放到 179 秒，没有中途跳转，`ended=true`、`readyState=4`，媒体错误为空，控制台无相关错误或警告。再核对 17 小节、三个大章、键盘 End 与实际拖动；手机 390×844 下页面宽 390 px，视频宽 352 px，无横向溢出。验收后回到开头暂停，临时尺寸已恢复。详见 [公开媒体信息](../publication.json) 与 [公开验收摘要](../validation.json)。

按照本次归档要求删除 11 个中间生成视频，共 869,353,263 字节（约 829 MiB），保留本地最终 V6 MP4、输入参考视频、工程、配音和公共人物素材。见 [清理记录](../cleanup-report.json)。Git 提交不含 MP4、原始音色、密钥或大型 QA；根目录 [制作 Skill](../../../../knowledge-video-production/SKILL.md) 收录流程与偏好。
