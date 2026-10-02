# V6 无二维码片尾 · 制作与验收记录

本次依据“视频最后一帧不要放二维码”的要求，从可编辑源工程移除片尾二维码和扫码文字，改为作者挥手、项目名称、GitHub 作者名与“点亮 Star，一起学习”的手绘文字卡片。星星轻弹呼应关注提示。整段视频重新渲染；解说、字幕和知识内容保持同一时间线。配音编码流 SHA-256 与上一版相同，没有新增图片或声音生成调用。

## 素材与复用

作者沿用根目录 `assets/手绘形象/shikanon-animation-v3/` 与工程 `assets/author-animation/` 的同一素材库。八组动作、192 张透明 PNG，每组 24 帧、20 fps、1.2 秒；统一画布与骨架锚点，固定闭嘴微笑，手、脚、头部与教棍保持运动。公共库和工程副本继续复用，不重新生成。

解说 944 个汉字对应 177 秒，实测每分钟 320 字；片尾另留两秒。知识主线约 30% / 50% / 20%，项目引导单独统计。17 小节、82 组图解和 101 组字幕保持一致。

## 当前成片验收

- 本次 Hyperframes 严格检查 23 个时刻，布局与运行错误为 0；98 项文字对比度通过。内置 motion 检查未启用，人物动作另由实际编码帧验证。
- H.264 / AAC，1080×1920，30 fps，179 秒，5,370 帧，17 个 MP4 章节，14,170,540 字节；完整解码零错误。
- 对整段片尾以 10 fps 检查 88 张实际画面，均未检出二维码；另通过尾部解码直到 EOF 得到实际最后一帧，1080×1920 原图也没有二维码。检测器先用上一版真实二维码画面做阳性对照，确认检测功能正常。
- 从本次新 MP4 解码 161 张人物画面，覆盖七种出镜动作；闭嘴与旧张嘴参考的误差比最高为 0.1861，身体稳定，手、头、脚与工具持续运动。另检查五组动作实际前后帧，均有清晰姿势变化。
- 公开的 [实际最后一帧](assets/ending-no-qr.jpg) 用于直接检查片尾文字和画面；原始验收结果留在 `qa/`。

当前 MP4 SHA-256：`3c129f1d4f95d9aad74da74ab8e93a457e7a7c54fb4ee32ca9e92b6bc7948729`。

## 云端发布

[观看无二维码版本 · 2 分 59 秒](https://qingjian-shikanon-media-sg-2026.oss-ap-southeast-1.aliyuncs.com/my-deep-learning-journey/knowledge-videos/loss-functions/3c129f1d4f95d9aa/loss-functions-v6.mp4)。匿名 HEAD 为 200，Range 为 206 / 1,024 字节；完整下载哈希与本地新成片一致。文章和播放器均切换到这份含内容哈希的新 URL，避免继续播放旧版。

云端文件以 1×、未静音从头连续播放到 179 秒，`ended=true`、`readyState=4`，无媒体或控制台错误。17 个小节、三个大章、实际拖动与键盘 End 均正常；手机 390×844 下页面无横向溢出。完整播放、章节与手机排版的证据见 [公开验收摘要](../validation.json)；公开 URL、大小和传输验收见 [publication.json](../publication.json)。

## 重建与归档

`index.html` 为带内嵌图集的构建产物，由 `build_composition.py` 生成，不重复提交 Git。配音、导出和详细 QA 留本地；文章、图解、字幕、可编辑源码与人物动作保留在仓库。使用具有 OpenCV、NumPy、Pillow 的 Python，以及 Node、sharp、FFmpeg。可用 `VIDEO_NODE`、`VIDEO_SHARP_MODULE`、`VIDEO_FFMPEG`、`VIDEO_FFPROBE` 指定当地依赖。

```bash
python3 build_composition.py
hyperframes check --samples 23 --strict
hyperframes render --output renders/loss-functions-v6-master.mp4 --quality high --fps 30 --workers 4 --gpu
ffmpeg -y -i renders/loss-functions-v6-master.mp4 -map 0:v -map 0:a -c:v libx264 -preset veryfast -crf 19 -threads 8 -pix_fmt yuv420p -c:a copy -movflags +faststart renders/loss-functions-v6.mp4
python3 embed_chapters.py --ffmpeg ffmpeg
python3 verify_delivery.py
python3 verify_encoded_stability.py
python3 verify_animation.py
python3 make_player.py
```

先前 11 个中间视频的清理记录见 [历史归档记录](../cleanup-report.json)。本次新版本完成云端播放验收后，已清理旧含二维码成片与新 master，共 2 个文件、127,530,851 字节，见 [本次清理记录](../cleanup-no-qr-report.json)。根目录 [制作 Skill](../../../../knowledge-video-production/SKILL.md) 已写入“成片默认不展示二维码”。
