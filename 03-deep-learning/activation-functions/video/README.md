# 激活函数 · 竖屏手绘解说

[返回文章](../001-introduction.md) · [返回知识点索引](../README.md)

最新版 V6 从“你知道吗？如果每层只做加权求和，哪怕把神经网络堆到一百层以上……”切入。演进按旧方法的困难、改进思想与新的取舍衔接，口播只保留有代表性的历史人物。教学场景使用博士服教棍动画。沿用 V4 对函数名读音的修订：GELU、ReLU、SiLU 使用英文全称，Swish 采用英文字母拼读；字幕和动画按实际中英文语音重新对齐。V6 开场先呈现问号人物思考，说到“如果每层”时展开多层神经网络，再用异或四点说明分类困境。公式从下一小节的讲解开始书写，z = W x + b 只写一次。17 处公式沿用用户指定的“抱大铅笔写字 V2”原始序列帧，笔尖与实际笔画同步；写完淡出、公式归位，再展开图解。

## 观看与下载

[![打开激活函数 V6 播放器](activation-explainer-v6/assets/poster.jpg)](activation-explainer-v6/watch.html)

- [18 秒开场与首次书写预览](activation-explainer-v6/renders/opening-preview.mp4)：从实际成片截取，展示问号人物、网络层数、异或四点和讲解中的首次书写。
- [最终 MP4](activation-explainer-v6/renders/activation-functions-v6.mp4)：约 4 分钟，1080×1920，30 fps，H.264 / AAC；含烧录字幕、章节进度和结尾 GitHub 引导。
- [章节播放器](activation-explainer-v6/watch.html)：支持三部分导航、19 个小节、进度拖动，以及左右键跳转 5 秒。
- [手机预览](activation-explainer-v6/mobile-preview.html) · [独立字幕](activation-explainer-v6/captions.srt) · [分镜脚本](activation-explainer-v6/storyboard.md)

以上成片和配音保存在本地工作区，沿用仓库的大媒体文件忽略约定；GitHub 浏览器不会直接播放本地文件。下载到包含音频、成片的完整工程后，可以运行：

```bash
python3 03-deep-learning/activation-functions/video/activation-explainer-v6/serve_player.py --port 8784
```

然后打开 <http://127.0.0.1:8784/video/activation-explainer-v6/watch.html>。服务器仅监听本机。

## 编辑与复用

工程位于 `activation-explainer-v6/`，制作方法、事实校准说明和验收记录见 [production-notes.md](activation-explainer-v6/production-notes.md)。

| 文件 | 用途 |
| --- | --- |
| [narration.json](activation-explainer-v6/narration.json) | 讲稿、章节、作者动作、每个动画的口播触发词 |
| [timeline.json](activation-explainer-v6/timeline.json) | 按真实配音字级时间对齐的字幕和动画 |
| [motion.py](activation-explainer-v6/motion.py) | 单线字形、序列帧笔尖配准与数值计算 |
| [animation-plan.json](activation-explainer-v6/animation-plan.json) | 全部 19 个场景的分层动作 |
| [render.py](activation-explainer-v6/render.py) | 可编辑的公式、曲线、示意图、字体与布局 |
| [build_timeline.py](activation-explainer-v6/build_timeline.py) | 保留服务端原始字幕，校准语速并建立时间线 |
| [make_player.py](activation-explainer-v6/make_player.py) | 生成桌面与手机章节播放器 |
| [verify_delivery.py](activation-explainer-v6/verify_delivery.py) | 检查最终编码、公式、随机跳帧、文字边界与作者动画 |
| [pronunciation-guide.md](activation-explainer-v6/pronunciation-guide.md) | 本版全部公式与术语读音表 |
| [verify_audio_continuity.py](activation-explainer-v6/verify_audio_continuity.py) | 从实际编码视频核对音轨字节一致，继承 V4 合格读音 |
| [verify_motion.py](activation-explainer-v6/verify_motion.py) | 书写笔尖、所有原始人物帧与实际编码画面核对 |
| [verify_opening.py](activation-explainer-v6/verify_opening.py) | 核对开场口播与画面顺序、没有开场公式且首次讲解只书写一次 |
| [make_opening_preview.py](activation-explainer-v6/make_opening_preview.py) | 从最终成片制作 18 秒开场与首次书写预览 |
| [validation.json](activation-explainer-v6/validation.json) | 最终文件哈希与验收摘要 |

公式书写复用[抱大铅笔 V2](../../../assets/手绘形象/抱大铅笔写字-v2/README.md)的原始 16 帧、8 fps 透明序列。现有图解采用可计算的折线、曲线与支路动画，作者讲解复用仓库 V3 闭嘴动作缓存与用户指定的[博士服教棍 V1](../../../assets/手绘形象/博士服教棍-v1/README.md)。配音使用既有作者音色参考生成，目标节奏为每分钟约 320 个等效发音单位；加入英文完整读法后，实测约 297.4 汉字 / 分钟，包含英文和停顿。完整讲解的动机、演化、前沿比例约为 29% / 53% / 19%。

修改文字后须重新生成相应配音、对齐字幕与动画；只调整图形、配色、布局时可沿用当前时间线。音色参考与配音请求、原始返回、成片及详细验收材料分别保存在工程的 `audio/`、`renders/`、`qa/` 中。

## 本地保留内容

本目录只保留最新 V6 工程及其必要素材、配音来源与验收记录。V1–V5 和废弃草稿已清理。最终成片与当前预览均位于 V6 的 renders/。

依赖与音频核验依据已保存在 V6 内。工程重建和验收不依赖历史目录。清理明细见 [cleanup-projects-report.json](cleanup-projects-report.json)。
