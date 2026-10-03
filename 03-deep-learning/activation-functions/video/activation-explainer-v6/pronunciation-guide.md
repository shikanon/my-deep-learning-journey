# 激活函数 V6：术语与公式读音

[观看与下载](../README.md) · [发音稿](narration.json) · [实际口播时间](storyboard.md)

沿用 V4 对全部 19 个小节的口播和主要公式的检查结果。函数名使用英文全称或准确的中文概念名称；字幕继续显示标准缩写。删除旧稿中的中文谐音写法，英文词也参与逐词时间对齐。

| 画面术语 | 本版实际朗读 | 处理 |
| --- | --- | --- |
| GELU | Gaussian Error Linear Unit | 英文全称，逐词发音 |
| ReLU | Rectified Linear Unit | 英文全称，逐词发音 |
| SiLU | Sigmoid Linear Unit | 英文全称，逐词发音；也称 sigmoid-weighted linear unit |
| Sigmoid | Sigmoid | 英语发音，清楚读出末尾 moyd |
| Swish | S W I S H | 逐个读英文字母，避免合成时误读为 Switch |
| SwiGLU | S W I S H Gated Linear Unit | Swish 逐个读英文字母，后半部分读英文全称 |
| β | 贝塔 | 保留正确的中文希腊字母名称；字幕显示 β |
| Tanh | 双曲正切 | 保留正确的中文概念名称 |
| Leaky / PReLU | 泄漏版本 / 参数化版本 | 用语义讲解固定负斜率和可学习斜率 |
| GLU | 门控、两条独立支路、逐项相乘 | 用中文语义解释门控线性单元的计算 |
| PowLU | 幂线性单元 | 保留中文概念名称 |
| Dynamic Tanh | 动态双曲正切 | 保留中文概念名称 |
| squared ReLU | 平方整流函数 | 保留中文概念名称 |
| XOR | 异或 | 保留正确中文名 |
| LLaMA | Llama | 用英语发音；字幕显示 LLaMA |

V6 的 17 处公式覆盖：加权求和、仿射层合并、异或特征构造、梯度连乘、Sigmoid、Tanh、ReLU、负半轴斜率、GELU、SiLU、GLU、SwiGLU、门控计算预算、增长与稳定性、接近零的贡献、2:4 稀疏和 Dynamic Tanh。口播中的乘、加、减、等于、四分之一以及“零、一、一、零”与画面计算一致。

W、x、z、b、σ、Φ、α、γ、幂次、导数和逐项相乘符号在画面展示；解说用其计算含义讲清过程，没有逐个念符号。β 在口播中出现，因此保留正确的中文名称“贝塔”。不把未朗读的符号虚报为发音错误，也不为了读完公式而增加一段术语清单。

英文名称核对：[GELU 原论文](https://arxiv.org/abs/1606.08415)、[Swish 原论文与 ReLU 全称](https://arxiv.org/abs/1710.05941)、[SiLU 原论文](https://arxiv.org/abs/1702.03118)、[GLU 与 SwiGLU 公式](https://arxiv.org/html/2002.05202v1)。SwiGLU 是 Swish 与 GLU 的组合名，本版将 Swish 的字母与 Gated Linear Unit 的英文名称连读。

原始 Seed Audio 字幕与编辑字幕分别保存。独立本地 Whisper 从实际音频的术语片段或完整上下文识别英文，不提供目标文本、热词或提示稿；结果保存在 qa/pronunciation-asr.json。本次仅替换画面；verify_audio_continuity.py 从 V6 实际 MP4 提取 AAC 数据和解码音轨，与已验收的 V4 逐字节比较。确认两者完全一致后继承这 11 次识别结果，并保存 V4 原始报告；本次没有重新运行 ASR。短词的拼写变体需要与发音区别，例如 Llama 与 lama 的拼写差异不能证明读音有误。
