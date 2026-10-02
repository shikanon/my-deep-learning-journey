# 作者形象与参考音色版：制作记录

> 历史制作记录：此版生成的 MP4 已于 2026-10-02 清理，源码、分镜与素材保留。观看当前成片请访问 [V6 发布入口](../README.md)。

V3 使用作者提供的手绘形象和原声音频。开场改为同一组数据在两种损失下得到 6 与 3，之后用异常值图解说明原因。视频脚注为「我的深度学习之路」，新增 GitHub 项目片尾、完整地址与二维码。

成片为 1080 × 1920 竖屏、30 fps、179 秒（2 分 59 秒），包含 17 个小节、82 组逐词图解、101 组字幕和 17 个 MP4 章节标记。全部 5,370 帧从新的语音时间线重新渲染。

## 参考素材和声音

作者素材位于同仓库另一工作副本的 `assets/手绘形象/shikanon-儿童手绘-v1.png` 和 `assets/参考音频/shikanon声音.m4a`。原始 PNG 复制到本目录并保持完整，用 SVG 共享定义与 GSAP 纸片动画呈现，没有重新生成作者长相。共享定义内嵌一次原始图像，避免渲染器对大于 2 MB 的外部图片不进行内嵌而漏图。

作者原声约 13.29 秒，转为 24 kHz 单声道 WAV 后作为四段 Seed Audio 1.0 请求的同一参考。四个任务均成功，全部返回词级字幕。生成参数、原始结果、参考文件和校准音频均保留。详见 [参考音色与 402 记录](seed-audio-diagnosis.md)。

944 个汉字对应 177 秒配音，语速为每分钟 320 字，统计包括句间停顿、排除标点和结尾两秒留白。四段仅作保持音高的节奏校准，原声参考没有调整速度和音高。字幕使用实际返回词时间换算，服务字幕与汉字文案均匹配。另对最终配音执行真实本地 ASR，原始识别保留在 `qa/`，用于核对内容覆盖和音频起止。

## 内容与图解

知识主线共 905 个汉字，提出原因 267 字（29.50%）、思想演化 455 字（50.28%）、近期研究 183 字（20.22%），维持约 3 : 5 : 2。片尾引导另计 39 字。

先通过最优答案的反差引起兴趣，进入误差抵消、平方评分、概率反馈与训练职责，再串起 MSE / MAE、Huber、交叉熵、Focal、标签平滑、对比学习和 DPO。最后介绍目标组合、序列策略更新与独立评测。近期研究的出处和阅读范围仍见独立 Markdown 文章。

图解使用按公式计算的曲线、平方格子、可移动均值标记、概率扣分条、权重缩小、正负样本移动、局部框选和序列括号。动画按语音词时间揭示，动作与转场缩短以适应更快解说。作者以轻跳、转动、进场与位移作为讲解者，不遮挡数据和文字。

[分镜与逐帧规划](storyboard.md)、`storyboard.json` 与 `qa/frame-plan.jsonl` 记录动作窗口、曲线标记运动和全部帧的图解状态；[动画源文件](animation.js)定义具体插值。技术与视觉选择见 [设计说明](DESIGN.md)。

## 验收

严格检查通过 23 处布局采样、运行时及 96 处对比度检查，零错误、警告和提示。纸页横推的有意离屏标注为转场，另逐节检查正常画面的作者与文字边界。全部 17 个小节的人物与标签无遮挡；101 组字幕逐条随机跳到中点，均只显示对应字幕。首帧立即显示钩子标题。

媒体探测确认 H.264 / AAC、1080 × 1920、30 fps、5,370 帧和 17 个原生章节；全片解码无错误。17 小节实际成片抽帧保存在 `qa/contact-final.jpg`。片尾二维码同时从全分辨率成片帧与 540 × 960 缩小帧解码成功，目标均为项目 GitHub 地址。

实际播放器逐个点击 17 小节，确认时间与当前标题同步；物理拖动顶部滑块、键盘 End 到片尾均可定位。手机宽度 390 px 下页面无横向溢出，视频为 352 px 宽。以正常速度、未静音从头连续播放，之后没有跳转，最终 `ended=true`，到达 179 秒，第 17 小节正确显示，没有媒体错误。结束状态记录在 `qa/player-playback.json`；汇总媒体证据在 `qa/delivery-validation.json`。

## 再生成与渲染

工程使用 Python 3、Node.js、HyperFrames 0.8.78、FFmpeg / FFprobe。二维码与验收脚本另用 OpenCV、NumPy、Pillow；本次使用已有的工作区运行库。音频生成须通过已配置的 Seed Audio 工具调用，密钥不在工程中。音频、成片、参考和 QA 材料按仓库约定保留为本地交付，排除在 Git 之外。

从已保留的 Seed 原音频重建：

```bash
python3 build_timeline.py --ffmpeg ffmpeg --ffprobe ffprobe
python3 build_composition.py
python3 make_effects.py --ffmpeg ffmpeg
python3 make_player.py
npx --yes hyperframes@0.8.78 check --samples 23 --strict
npx --yes hyperframes@0.8.78 render --output renders/loss-functions-v3-master.mp4 --quality high --fps 30 --workers 4 --gpu
ffmpeg -y -i renders/loss-functions-v3-master.mp4 -map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 19 -threads 8 -pix_fmt yuv420p -c:a copy -movflags +faststart renders/loss-functions-v3.mp4
python3 embed_chapters.py --ffmpeg ffmpeg
ffmpeg -y -ss 6 -i renders/loss-functions-v3.mp4 -frames:v 1 -vf scale=540:-1 assets/poster.jpg
python3 serve_player.py --background
```

本机播放器入口为 `http://127.0.0.1:8770/video/loss-explainer-v3/watch.html`。已有的本主题播放器服务可以复用，启动脚本会检查后复用，避免占用同一端口。HTML 顶部滑块与章节按钮提供实际跳转，成片里的进度条用于显示当前位置。
