# 手绘版制作与验收记录

> 历史制作记录：此版生成的 MP4 已于 2026-10-02 清理，源码、分镜与素材保留。观看当前成片请访问 [V6 发布入口](../README.md)。

## 本版交付

内容与画面重做为暖色儿童手绘课堂；采用用户给定的本地 `../loss-explainer/assets/video.mp4` 作为画风参考。原参考视频保持原样，新版全部材料存放在这个文件夹中。

成片为 1080 × 1920、30 fps、334 秒（5 分 34 秒）。解说 910 个汉字；按包含句间停顿、排除标点与结尾一秒留白的口径为 164 字 / 分钟。为容纳完整的概念、演化和前沿，本版时长从早先约四分钟增加到五分半。全版使用 `generate_audio` 的 Seed Audio 1.0，四个生成任务、原音频、校准系数与字幕证据保存在 `audio/`、`timeline.json` 和 `qa/speech-rate.json`。

正文主线汉字占比为 29.9% / 49.2% / 20.9%，解说占比为 29.89% / 50.00% / 20.11%，对应“提出原因 / 思想演化 / 近期研究”。统计包含主线图注与表格文字，排除 URL、文末自测与运行附录；见 `qa/content-allocation.json`。近期研究按一手论文核验至 2026-10-02，版本、阅读范围与适用边界写在文章中。

## 图解不是装饰

共 16 个小节、77 组逐词触发的图解、104 组字幕。温度猜测用尺子建立评分；正负观测靠拢后仍保留误差；误差三通过两组九格解释平方；准确率与概率反馈对照；训练职责依次连通。后半段用真实函数曲线、异常值移动平均数、Huber 限速、交叉熵长短条、Focal 降低容易样本的音量、平滑目标分布、正负关系拉近推远、DPO 参考模型、局部与全局配对、整段回答权重说明思想。

图解为原创 SVG，曲线和数轴按公式计算；纸边略有铅笔感，数值坐标不添加随机抖动。HTML/CSS 管理文字与纸页，GSAP 的暂停时间线重建每一帧。没有需要三维摄像机或真实空间模拟的内容，SVG 更便于准确描线和修改公式，因此本次没有使用 Three.js / WebGL。全工程不依赖实时随机数、无限循环或屏幕录制。

[分镜](storyboard.md)按每个词的实际时间安排图解关键帧；`storyboard.json` 保存动作区间，`qa/frame-plan.jsonl` 逐行规划全部 10,020 帧的当前小节、字幕和图解状态。具体位置与插值由 [动画时间线](animation.js)定义。

## 配音、字幕和 402

详见 [Seed Audio 核查](seed-audio-diagnosis.md)。本轮四次 Seed Audio 生成全部成功，控制台相应资源包仍有余量，旧 402 没有复现。旧适配器没有保存业务错误正文，所以不能追溯确切原因，也不能将其直接归为“额度不足”。没有替换密钥或更换账户。

第一段没有服务字幕，本地中文 ASR 对实际校准音频生成时间证据；后面三段采用服务返回词时间。原始 ASR 与对齐差异保存，不把文本脚本冒充识别结果。另一次 ASR 检查了最终完整配音的起止与各节内容。第一段重复减速的参数问题已通过保持音高的速度校准解决；字幕同步换算。

画面角注只保留课堂名和主题句，没有“AI 合成解说”等字样。制作记录保留配音来源。

## 播放与跳转

视频画面顶部持续显示三段内容比例、16 小节进度和当前标题。成片另有 16 个 MP4 章节元数据；播放器是否展示原生章节取决于播放器本身。

[交互播放器](watch.html)在视频上方提供真正的拖动滑块、三大章按钮和 16 个小节跳转按钮，时间与同一份 `timeline.json` 同步。键盘支持 Home / End、左右键。全屏模式仍保留上方的交互进度。视频文件的画面条用于提示进度；拖动跳转由这个 HTML 播放器提供。播放器不需要外部 CDN，HTTP 模式有字节范围请求支持，也可本地打开。

## 复用和重新渲染

需要 Node.js、HyperFrames 0.8.78、FFmpeg / FFprobe。校准与分镜脚本只依赖 Python 标准库；从无字幕音频重新做 ASR 时，另需中文 faster-whisper 模型和对应运行库。生成新的原音频必须调用配置好的 `generate_audio`，本工程不保存密钥。原音频与输出遵循仓库规范，只作为此次本地交付保留。

在此目录运行：

```bash
python3 build_timeline.py --ffmpeg ffmpeg --ffprobe ffprobe
python3 build_composition.py
python3 make_effects.py --ffmpeg ffmpeg
python3 make_player.py
npx --yes hyperframes@0.8.78 check --samples 23 --strict
npx --yes hyperframes@0.8.78 render --output renders/loss-functions-v2-final-master.mp4 --quality high --fps 30 --workers 4 --gpu
ffmpeg -y -i renders/loss-functions-v2-final-master.mp4 -map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 19 -threads 8 -pix_fmt yuv420p -c:a copy -movflags +faststart renders/loss-functions-v2.mp4
python3 embed_chapters.py --ffmpeg ffmpeg
ffmpeg -y -ss 18 -i renders/loss-functions-v2.mp4 -frames:v 1 -vf scale=540:-1 assets/poster.jpg
python3 serve_player.py --background
```

`serve_player.py` 只监听本机 127.0.0.1:8770，服务此知识点目录；默认播放器地址为 `http://127.0.0.1:8770/video/loss-explainer-v2/watch.html`。运行状态与日志写在 `qa/`。

## 验收证据

严格检查已通过 23 处布局采样、运行时检查和 81 处对比度检查，零错误、警告与提示，见 `qa/check-final.json`。CLI 本轮没有启用 motion 检测，动效另外检查注册时间线、随机跳帧、16 小节与 104 组字幕互斥。图解运动另核对实际位置与方向，见 `qa/character-motion-audit.json`。初次画面抽查发现 SVG 的绝对平移覆盖原坐标，已修正起点并从动画源文件重新捕获全部帧，没有把有问题的初次成片作为最终交付。

最终媒体探测确认 1080 × 1920、30 fps、10,020 帧、334 秒、H.264 / AAC 和 16 个 MP4 章节。最终成片约 17.8 MB，全片解码零错误，16 小节实际成片抽帧见 `qa/contact-final.jpg`。

交互播放器已实际点击小节与三大章、物理拖动顶部滑块、键盘到片尾，并在 390 × 844 手机宽度检查无横向溢出。正常速度、未静音从头连续播放，未再跳转，最后 `ended=true`、时间 334 秒、标题为第 16 小节，无媒体错误。完整证据汇总在 `qa/delivery-validation.json` 与 `qa/player-playback.json`。QA 截图和音频不混入文章插图目录。
