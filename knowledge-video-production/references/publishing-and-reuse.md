# 归档、对象存储与仓库发布

## 目录安排

```text
knowledge-video-production/           # 根目录 skill 与通用辅助脚本
assets/手绘形象/                      # 可跨知识点复用的作者图像/动作
<分类>/<知识点>/
  README.md                          # 导航
  001-introduction.md                # 可独立阅读的文章
  assets/                            # 正文插图
  examples/                          # 可运行的知识实验
  video/
    README.md
    publication.json                # 公开 URL、哈希与传输验收
    validation.json                 # 可公开的播放与制作验收摘要
    cleanup-report.json             # 若本次授权清理
    <工程>/                         # 分镜、时间线、源码、播放器、素材副本
      audio/                        # 本地配音/原始参考，Git 忽略
      renders/                      # 本地导出，Git 忽略
      qa/                           # 本地详细验收，Git 忽略
```

公共动作库是用户明确要求复用的材料，需要版本、来源、序列帧和 manifest。可编辑工程与必要图解进入 Git；大型 MP4、原始声音、私密生成响应、凭据和系统字体不进入 Git。图片或图集变大时先检查仓库限制和实际复用需求，不随意删掉历史原始底稿。

## 上传已授权的最终文件

先读取当前成片、SHA 与 ffprobe。复用本机已配置且本次可用的对象存储，配置文件由参数传入，不复制密钥进本项目。为项目设置独立前缀，例如 `my-deep-learning-journey/knowledge-videos/<topic>/<sha16>/final.mp4`，不继承其他项目的前缀。

使用永久公开对象 URL，与内容哈希一起记录。视频需要正确 `video/mp4`、匿名可读和 HTTP Range；静态封面可同时上传。不要公开原始作者声音、上传整份项目 ZIP 或删除旧云对象，除非用户另有要求。

本 skill 的发布脚本只适用于阿里 OSS；用户配置其他存储时使用对应 SDK/工具，保留相同验收契约。Node ≥22、ffprobe、`ali-oss` 是脚本依赖。可在 skill 目录 `npm install`，或通过 `--sdk-root` 复用本地已有 SDK。

```bash
node knowledge-video-production/scripts/publish_video.mjs \
  --video '<topic>/video/<project>/renders/final.mp4' \
  --poster '<topic>/video/<project>/assets/poster.jpg' \
  --topic '<topic-slug>' --prefix 'my-deep-learning-journey/knowledge-videos' \
  --output '<topic>/video/publication.json' --dry-run
```

确认本次已授权发布，再移除 `--dry-run` 并提供 `--env-file '<ignored-local-config>'`、可选 `--sdk-root '<existing-node-project>'` 和 `--ffprobe '<executable>'`。脚本拒绝覆盖存在但哈希不符的对象；匹配对象复用并重新验证。失败时不连续重复上传，先确定错误；日志只输出公开 URL 和脱敏错误。

脚本通过匿名 HEAD、1024 字节 Range 206、全量下载哈希后才保存 manifest。随后还需浏览器真实播放云端文件；保存播放器来源、1×完整播放结束、手机尺寸和章节跳转证据。

## Markdown 和播放器

知识点文章在正文前或适当位置增加可点击封面、永久 MP4 链接、时长与工程入口。GitHub Markdown 可点图访问 MP4，不依赖 HTML `<video>` 的渲染。文章图片可用已提交的相对路径；云端媒体使用 HTTPS 永久 URL。

播放器读取同一 `publication.json` 的 URL；发布前可以使用本地哈希媒体。公开后即使 clone 没有 `renders/`，播放器仍能加载云端成片。下载按钮与播放源一致，出错提示说明检查网络/媒体来源，不误导用户寻找已删除的文件。

## 清理只发生在验证之后

用户要求删除中间生成视频时，列出知识点 `video/` 中实际生成物；保留最终 MP4，保留 `assets/` 中的输入参考以及动画/源码/配音等材料。不能以“旧版本”之名递归删除全部工程。

```bash
python3 knowledge-video-production/scripts/cleanup_generated_videos.py \
  --video-root '<topic>/video' --keep '<topic>/video/<project>/renders/final.mp4' \
  --publication '<topic>/video/publication.json' \
  --report '<topic>/video/cleanup-report.json'
```

默认仅预览。确认上传/云端播放都通过且用户已授权清理后，加 `--apply`。执行要求 manifest 中最终哈希一致，并且有全量下载哈希通过记录；清理报告列出删除文件和回收空间。同步修改旧 MP4 导航到当前公开版本或旧制作说明。历史记录使用过去时，清楚标注其生成视频已清理。

## 推送代码仓库

只在本次明确授权发布仓库后提交/推送。按相关路径选择性暂存，保留无关改动。检查凭据、生成请求和参考音频没有进入暂存区，检查文件大小/许可和 Markdown 链接。运行仓库 `python3 scripts/check_notes.py`、skill 的 `quick_validate.py` 以及本次修改对应的发布/播放器检查。

遵守现有分支/贡献约定，默认新分支 `codex/` 前缀；需要创建 PR 时附上工具要求的 PR artifact。直接发布 main 必须符合用户授权、远端能安全快进及仓库约定。不要 force push。推送后读远端 SHA 和文章/skill 内容，区分本地提交、远端发布与云端视频验收。

最终报告给文章、skill 与视频链接，说明清理数量和远端提交；没有真实完成的环节明确留下，不用源码能力或任务提交成功冒充结果。
