# 大语言模型：架构、预训练与推理

[返回总索引](../README.md)

## 二级知识点

### 文本表示与模型架构

| 知识点 | 子主题范围 |
| --- | --- |
| [Tokenizer 与文本切分](tokenizer/README.md) | 字符、词与子词、BPE、WordPiece、Unigram、SentencePiece、Byte-level、特殊 Token、无固定词表建模 |
| [Embedding 与表示空间](embeddings/README.md) | Token Embedding、位置表示、输入输出权重绑定、语义空间、上下文化表示 |
| [位置编码](positional-encoding/README.md) | 正弦与可学习绝对位置、相对位置、RoPE、ALiBi、旋转频率、位置与顺序建模 |
| [自注意力与 QKV](self-attention/README.md) | Q、K、V 的含义、缩放点积、Mask、张量维度、加权聚合 |
| [注意力机制](attention-mechanisms/README.md) | 加性与点积注意力、Self 与 Cross Attention、多头注意力、因果与双向注意力、注意力的作用与边界 |
| [Transformer 架构](transformer/README.md) | Encoder、Decoder、Encoder-Decoder、Attention 与 FFN、残差路径、架构演进 |
| [MQA、GQA 与 MLA](gqa-and-mla/README.md) | 共享 KV 头、多查询与分组查询、潜在注意力、质量、缓存与带宽的权衡 |
| [混合专家模型（MoE）](mixture-of-experts/README.md) | 稀疏激活、路由、Top-k 专家、负载均衡、容量、专家并行、总参数与激活参数 |
| [稀疏注意力与线性注意力](efficient-attention/README.md) | 局部与滑窗、块稀疏、线性化、递归状态、质量与复杂度、与精确注意力的区别 |
| [状态空间模型与混合架构](state-space-models/README.md) | SSM、S4、Mamba、选择性状态、Transformer 混合、表达能力与硬件效率 |
| [扩散语言模型](diffusion-language-models/README.md) | 离散去噪、Masked Diffusion、并行生成、重掩码、自回归与扩散的比较 |

### 预训练与规模规律

| 知识点 | 子主题范围 |
| --- | --- |
| [预训练目标](pretraining-objectives/README.md) | 自回归语言建模、Masked Language Modeling、去噪目标、因果 Mask、训练目标与能力 |
| [预训练数据与数据配比](pretraining-data/README.md) | 清洗与去重、质量筛选、领域配比、课程学习、数据质量与数量、数据合成 |
| [缩放定律（Scaling Laws）](scaling-laws/README.md) | 模型、数据与算力、Kaplan Scaling、Chinchilla、Compute-optimal、数据质量、训练与推理预算 |

### 生成、上下文与推理

| 知识点 | 子主题范围 |
| --- | --- |
| [解码与采样](decoding-and-sampling/README.md) | Greedy、Beam Search、Temperature、Top-k 与 Top-p、重复惩罚、约束解码、随机性与可复现性 |
| [长上下文外推](long-context-extrapolation/README.md) | 训练长度与推理长度、位置插值、NTK-aware Scaling、YaRN、长文本续训、检索与真实长程理解 |
| [上下文学习与 Prompting](in-context-learning/README.md) | Zero-shot 与 Few-shot、示例选择、指令格式、Prompt 敏感性、上下文学习与参数学习 |
| [推理与 Chain-of-Thought](reasoning/README.md) | 中间步骤、Self-Consistency、任务验证、推理轨迹、可解释性边界、推理与记忆 |
| [推理时计算与 Test-time Scaling](test-time-compute/README.md) | 长推理、Best-of-N、搜索与验证器、预算分配、质量、延迟与成本 |
| [多 Token 预测（MTP）](multi-token-prediction/README.md) | 多步训练目标、辅助预测头、联合学习、与推测解码的联系、接受率与训练成本 |
| [幻觉、事实性与依据对齐](hallucination-and-grounding/README.md) | 事实错误、信息缺失、记忆与生成、证据引用、拒答与不确定性、知识更新、事实性评估 |

<!-- new-note-index -->
