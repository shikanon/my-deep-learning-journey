# shikanon · 儿童手绘抱大铅笔写字

作者 Q 版形象，双手抱着与全身高度接近、直径约等于躯干宽度的超粗大铅笔，笔尖从左向右划动，再回到左侧。沿用白色卫衣、手写 shikanon 与 ♓、黑色头发及半框眼镜的儿童彩铅蜡笔风格。

- `frames/001.png` 至 `016.png`：16 帧 512×512 RGBA 透明图。
- `sequence.png`：2048×2048 透明序列图，4×4，先行后列。
- `animation-loop.apng` / `animation-once.apng`：8 fps，2 秒；循环 / 单次。
- `character.png`：第一帧主形象。
- `key-poses/`：8 个不同关键姿势。
- `preview.html`：离线播放与拖动帧序；总览 `overview.png` 带浅色底，仅供查看。
- `manifest.json` / `validation.json`：帧序、固定脚底锚点、裁切位置及解码检查。
- `source-swing.png` / `source-intermediate.png`：内置 image_gen 生成的选定原图。
- `*.prompt.txt`：原始及修正提示词；未使用 CLI/API 生成。

同教棍组的编排，8 个 AI 手绘姿势 + 倒序回摆组成 16 帧，第 8/9 帧停顿，16/1 首尾一致。固定 512 画布脚底锚点 (256,456)，统一每张原始序列图的缩放比例，未独立缩放每帧或绘制插帧。

透明通道、边距、APNG 每帧与 PNG 像素一致性、首尾/倒序一致性及笔杆倾角单调变化已验证。左右扫动的最大相邻倾角变化约 17°；手绘头部、轮廓与握笔细节仍有轻微变化，适合视频生成参考，精细动画可继续补间。

使用 [preview.html](preview.html) 查看当前序列帧。视频笔尖配准见 [video-registration.json](video-registration.json)。制作视频时直接读取现有 PNG 和 manifest 中的帧率。

此版按用户要求加粗铅笔并重绘双臂抱笔，使用原始手绘素材导出全部帧。
