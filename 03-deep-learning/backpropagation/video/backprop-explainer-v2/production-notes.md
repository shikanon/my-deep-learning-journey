# 反向传播与自动微分 · 过程优化版

制作开始：2026-10-03；成片验收：2026-10-04。使用根目录 [knowledge-video-production Skill](../../../../knowledge-video-production/SKILL.md) 的程序化解释方法。保留已验收的口播、实际逐词时间与字幕，重做 16 个小节的教学画面。最终文件、章节播放器和验收记录统一指向本工程的 V2 成片。

## 改进范围

旧版主要用静态结论卡片、独立箭头和揭示动画讲解。新版让观众追踪对象与中间步骤：

- 前向、链式法则和反传共用同一张图。w、x、乘法结果、偏置、预测、目标、误差和损失保持位置。
- 前向数值沿蓝绿箭头进入运算节点；反向梯度沿同一条边返回。明确显示局部导数 1、输入因子 2 与损失对误差的导数 −3。
- 曲线上移动的点、损失条长度和参数变化都从同一数值模型计算。小步下降与越过最低点的大步分开演示。
- x²+x 的两条原路径各自返回 4 与 1，最终汇总到同一个 x。箭头尖端停在节点边界外；反向时撤去本路径的前向箭头，保证传播方向可见。输出 6 与导数 5 分开显示。
- 前向模式与反向模式用一个可核对的三参数函数对照。导数种子与实际扰动参数分开标识。
- 梯度缓冲区依次出现 0、−6、−12；清零与两批等大小的平均目标另外演示。
- 检查点清除中间值后，反传明确提出需要 a₂。从保留的输入重算两步，找回同名变量 a₂=5，再执行局部求导。
- 选择性保存示例先缓存矩阵乘法的 [4,−5]，反向从缓存重算 ReLU 的 [4,0]，得到求导需要的 2a=[8,0]。

82 个语义步骤都绑定实际口播词时间。复杂步骤保留中间状态，当前步骤以 phase 文案与作者旁的解释指明。删除无关的文字跳动、整卡脉冲、弹跳和循环粒子。

## 模型与表达边界

手算示例仍是 x=2、y=5、w=1、b=0，预测 2、损失 4.5，梯度为 −6 与 −3。学习率 0.1 后参数变为 1.6 与 0.3，预测 3.5、损失 1.125。

前向模式示例为 L=w₁²+2w₂+w₃，在 (1,1,1) 处的梯度是 (2,2,1)。输入方向 (1,0,0) 对应输出方向导数 2。比较全部偏导时，本例需要三个输入方向或一个标量输出。

激活检查点用 a₀=2 → a₁=4 → a₂=5 → a₃=25 → 输出 5 展示机制。保存槽表示示意的中间值数量，不代表真实显存字节。图中的完整保存策略与检查点策略仅用于解释。重算恢复值使用完后可释放。

压缩用保留两位小数的舍入展示数值恢复误差；最大绝对误差为 0.0034。它是机制示例，未复现 Adacc 的论文压缩配置，也未给出实际性能测量。网络历史画面展示误差信号的传播路径，不伪装成训练结果。论文与框架依据见 [research.md](research.md)。

## 人物与声音

教棍讲解直接读取根目录 `assets/手绘形象/博士服教棍-v1` 的 16 张透明 PNG，按 manifest 的 8 fps 选帧。每小节只在一个解释关键点做一次抬棍动作，其他时间保持静止。片尾挥手读取 `日常服动作序列帧` 的 24 张 PNG。源码构建读取根资产，HTML 构建产物内嵌相同 PNG；没有回退到旧 shikanon-animation 库，也不使用 atlas、WebP 或 APNG。帧哈希和来源在 [asset-provenance.json](asset-provenance.json)。博士服源帧存在原有手绘轮廓差异；验收检查忠实复用及合成位置。

本次没有新增 TTS 请求。`audio/narration.m4a` 从 V1 最终成片提取 AAC，再直接封装到新视频中，没有重编码或二次响度处理。验收对照 V1 与 V2 的 AAC 包数据和解码 PCM 哈希，继承的读音检查与本次一致性检查分别记录。声音来源见 [audio-provenance.json](audio-provenance.json)。

## 复现

依赖 Python 3.10 或更新版本、NumPy、Pillow、OpenCV、Node、Hyperframes 0.8.78、FFmpeg 和 FFprobe。中文字体使用 macOS 的 Hiragino Sans GB。源码使用环境变量指定当地工具路径；其他字体环境需重新验收布局。

```bash
python3 build.py
npx --yes hyperframes@0.8.78 check --samples 32 --strict
node verify_source.mjs
python3 verify_content.py
python3 render.py
python3 verify_delivery.py
python3 make_player.py
python3 serve_player.py --background
```

`VIDEO_NODE`、`VIDEO_HYPERFRAMES_CLI`、`VIDEO_FFMPEG`、`VIDEO_FFPROBE`、`VIDEO_PLAYWRIGHT_MODULE`、`VIDEO_SHARP_MODULE`、`VIDEO_CHROME_PATH` 可指定当地依赖。Hyperframes 的工具覆盖变量另为 `HYPERFRAMES_FFMPEG_PATH` 和 `HYPERFRAMES_FFPROBE_PATH`。`render.py --mux-only` 可复用已经导出的纯画面轨道。

重建只读取本工程保存的 `audio/narration.m4a`、GSAP、字幕与时间线，以及根目录人物资产；不读取历史工程。已验收的音轨和原始语音 QA 都保留在本工程内，来源与哈希见 `audio-provenance.json`。生成 HTML、配音输入、渲染结果和详细 QA 保留本地。Git 克隆不包含私人参考声音；缺少音轨时，可从下面的公开最终 MP4 提取已验收 AAC，不需要重新生成声音。

## 验收证据

[validation.json](validation.json) 汇总最终文件标识、内容、布局、编码、音轨一致性、实际 PNG 合成和浏览器播放结果。详细源画面检查包含 246 个步骤状态、2,829 帧过渡与 10 个随机跳转。步骤状态还检查可见箭头是否穿过文字；不把被不透明方框遮住的底层线段算作可见遮挡。成片检查保存每小节的编码截图，以及 21 个关键机制的前、中、后三帧。预览片段从最终 MP4 截取。

最终成片为 240.213 秒、1080×1920、30 fps、7,206 帧，文件大小 12,323,945 字节。SHA256 为 `6b8d998cb383525656b87432f9a430783aa76c2f25b48051e6c9e5550208b18d`。全片解码无错误；AAC 包与解码 PCM 均与 V1 相同，响度为 −16.0 LUFS。

本地章节播放器使用最终文件，已按 1×、有声从 0 秒连续播放到 `ended=true`。事件记录没有跳转或等待事件，媒体与控制台无错误。另行核对 16 个小节与 3 个主章节跳转、真实拖动、Home / End / 左右键、空格播放暂停和从头播放。1440×1050 与 390×844 布局没有横向溢出，临时视口已恢复。内置浏览器没有进入原生全屏，因此“放大观看”使用铺满窗口的视图，按钮与 Esc 都可退出；不宣称已经验收浏览器原生全屏。

44 秒预览截取最终成片的链式法则、反传与参数更新三个小节，保留同一例子的连续过程。历史 V1 工程已删除，当前播放器及根目录验收入口均指向 V2。清理移除了 3,787 个文件，回收 1,071,139,703 字节。旧目录移出期间，重新生成的 HTML、时间线、字幕和人物输入哈希均未改变；复用已编码画面轨道进行独立封装，最终 MP4 哈希与已上传文件一致。此清理步骤没有重新渲染全部画面。

## 对象存储发布

[最终 MP4](https://qingjian-shikanon-media-sg-2026.oss-ap-southeast-1.aliyuncs.com/my-deep-learning-journey/knowledge-videos/backpropagation/6b8d998cb3835256/backpropagation-v2.mp4) 已发布为 `video/mp4`；封面也已上传。[publication.json](../publication.json) 记录对象地址、16 个章节和文件哈希。匿名 HEAD、Range 与完整下载哈希均已通过。文章、播放器和下载入口使用同一地址。清理结果见 [cleanup-projects-report.json](../cleanup-projects-report.json)。

缺少本地音轨时，在本工程目录下先下载最终 MP4，核对上述 SHA256，再提取 AAC：

```bash
mkdir -p audio
ffmpeg -i backpropagation-v2.mp4 -map 0:a:0 -c:a copy -map_metadata -1 -map_chapters -1 audio/narration.m4a
```

原始 AAC 包与 PCM 哈希保存在 `audio-provenance.json`，可用 `verify_delivery.py` 核对。私人参考声音不参与画面重建或已验收音轨的封装。

对象存储文件已通过章节播放器的 1×有声连续播放验收，到达 `ended=true`，没有媒体、控制台、等待或跳转错误。随后再次核对全部 16 个小节，跳转后均为 readyState=4。此结果独立记录在最终验收报告的 `published_playback` 与 `published_player_controls` 中。
