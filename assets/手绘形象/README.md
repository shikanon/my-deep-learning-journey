# 作者手绘形象

- [作者原始手绘参考图](shikanon-儿童手绘-v1.png)

公共作者动画统一保存并读取透明 PNG 序列帧。先按服装与动作选择素材，再读取各自 manifest 的帧序、帧率、画布与锚点。

| 用途 | 素材 | PNG 序列规格 |
| --- | --- | --- |
| **教棍讲解优先使用** | [博士服教棍](博士服教棍-v1/README.md) · [预览](博士服教棍-v1/preview.html) | 16 帧，512×512，8 fps；教棍从右下举向右上再返回 |
| 公式书写 | [抱大铅笔写字](抱大铅笔写字-v2/README.md) · [预览](抱大铅笔写字-v2/preview.html) | 16 帧，512×512，8 fps；附笔尖配准元数据 |
| 思考、领悟、挥手、问号与轻步 | [日常服动作序列帧](日常服动作序列帧/README.md) · [预览](日常服动作序列帧/preview.html) | 8 组共 192 帧，384×576，20 fps；PNG 像素原样保留 |

`shikanon-animation-v1/v2/v3` 旧目录已退役。仍需要的动作迁为日常服 PNG 序列；历史工程需要的重建输入留在各自工程的 `assets/author-animation/source/`。迁移与删除记录见 [序列帧迁移报告](../sequence-frame-migration.json)。

## 存储与复用

```text
assets/手绘形象/<服装或形象-动作>/
  README.md
  manifest.json       # 顺序、帧率、画布、锚点、来源与哈希
  frames/             # 独立透明 PNG 原件
  preview.html        # 直接播放 PNG 序列
```

新动画按用途命名。透明 PNG 序列是正式素材，单张 `sequence.png` 可供查看或交换；不以 APNG、WebP 或运行时图集代替原件。已有参考图、来源图、提示词和输入压缩包保留其原始用途。

渲染器按 manifest 直接选择 PNG。固定画布与结构锚点，不按每帧的外接框重新居中。视频工程可以保留必要副本，核对 PNG 哈希后复用；公共原件保存于根目录 `assets/`。
