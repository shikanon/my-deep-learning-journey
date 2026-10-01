# 我的深度学习之路

深度学习、大模型、RL 与 Agent 学习笔记索引。按兴趣选择任意二级知识点；目录编号仅用于分类。当前建立 **121 个二级知识点目录**，各目录的 README 列出可继续展开的子主题。

[数学基础](#01-math-foundations) · [机器学习](#02-machine-learning) · [深度学习基础](#03-deep-learning) · [大语言模型与序列架构](#04-large-language-models) · [后训练与对齐](#05-post-training-and-alignment) · [强化学习](#06-reinforcement-learning) · [Agent 与知识系统](#07-agents) · [多模态与生成模型](#08-multimodal-and-generative-models) · [训练与推理工程](#09-training-and-inference-engineering) · [评估与研究方法](#10-evaluation-and-research)

<a id="01-math-foundations"></a>

## 数学基础

- [线性代数与张量](01-math-foundations/linear-algebra/README.md)
- [矩阵分解与低秩近似](01-math-foundations/matrix-factorization/README.md)
- [微积分与链式法则](01-math-foundations/calculus/README.md)
- [概率分布与条件概率](01-math-foundations/probability/README.md)
- [信息论](01-math-foundations/information-theory/README.md)
- [约束优化](01-math-foundations/constrained-optimization/README.md)
- [随机估计与蒙特卡洛](01-math-foundations/monte-carlo/README.md)
- [数值稳定性与浮点表示](01-math-foundations/numerical-stability/README.md)

<a id="02-machine-learning"></a>

## 机器学习

- [学习范式与归纳偏置](02-machine-learning/learning-paradigms/README.md)
- [最大似然与贝叶斯学习](02-machine-learning/likelihood-and-bayes/README.md)
- [泛化、过拟合与正则化](02-machine-learning/generalization/README.md)
- [数据划分与交叉验证](02-machine-learning/data-splits/README.md)
- [线性模型与核方法](02-machine-learning/linear-and-kernel-models/README.md)
- [评估指标与阈值选择](02-machine-learning/metrics/README.md)
- [表示学习与迁移学习](02-machine-learning/representation-learning/README.md)

<a id="03-deep-learning"></a>

## 深度学习基础

- [反向传播与自动微分](03-deep-learning/backpropagation/README.md)
- [损失函数](03-deep-learning/loss-functions/README.md)
- [激活函数](03-deep-learning/activation-functions/README.md)
- [归一化](03-deep-learning/normalization/README.md)
- [优化器](03-deep-learning/optimizers/README.md)
- [学习率与调度策略](03-deep-learning/learning-rate-schedules/README.md)
- [初始化与梯度稳定性](03-deep-learning/initialization-and-gradients/README.md)
- [残差连接与网络深度](03-deep-learning/residual-networks/README.md)
- [MLP 与前馈网络](03-deep-learning/mlp-and-ffn/README.md)
- [卷积与 CNN](03-deep-learning/convolution/README.md)
- [RNN、LSTM 与 GRU](03-deep-learning/recurrent-networks/README.md)
- [深度网络正则化](03-deep-learning/regularization-techniques/README.md)
- [训练循环与调试](03-deep-learning/training-loop/README.md)

<a id="04-large-language-models"></a>

## 大语言模型与序列架构

- [自注意力与 QKV](04-large-language-models/self-attention/README.md)
- [注意力机制](04-large-language-models/attention-mechanisms/README.md)
- [Transformer 架构](04-large-language-models/transformer/README.md)
- [Tokenizer 与文本切分](04-large-language-models/tokenizer/README.md)
- [Embedding 与表示空间](04-large-language-models/embeddings/README.md)
- [位置编码](04-large-language-models/positional-encoding/README.md)
- [预训练目标](04-large-language-models/pretraining-objectives/README.md)
- [预训练数据与数据配比](04-large-language-models/pretraining-data/README.md)
- [缩放定律（Scaling Laws）](04-large-language-models/scaling-laws/README.md)
- [解码与采样](04-large-language-models/decoding-and-sampling/README.md)
- [MQA、GQA 与 MLA](04-large-language-models/gqa-and-mla/README.md)
- [混合专家模型（MoE）](04-large-language-models/mixture-of-experts/README.md)
- [稀疏注意力与线性注意力](04-large-language-models/efficient-attention/README.md)
- [状态空间模型与混合架构](04-large-language-models/state-space-models/README.md)
- [长上下文外推](04-large-language-models/long-context-extrapolation/README.md)
- [上下文学习与 Prompting](04-large-language-models/in-context-learning/README.md)
- [推理与 Chain-of-Thought](04-large-language-models/reasoning/README.md)
- [推理时计算与 Test-time Scaling](04-large-language-models/test-time-compute/README.md)
- [多 Token 预测（MTP）](04-large-language-models/multi-token-prediction/README.md)
- [扩散语言模型](04-large-language-models/diffusion-language-models/README.md)

<a id="05-post-training-and-alignment"></a>

## 后训练与对齐

- [监督微调（SFT）](05-post-training-and-alignment/supervised-finetuning/README.md)
- [LoRA 与参数高效微调](05-post-training-and-alignment/lora-and-peft/README.md)
- [奖励模型与偏好数据](05-post-training-and-alignment/reward-modeling/README.md)
- [RLHF 与 RLAIF](05-post-training-and-alignment/rlhf/README.md)
- [DPO 与直接偏好优化](05-post-training-and-alignment/dpo-and-preference-optimization/README.md)
- [RLVR、GRPO 与推理后训练](05-post-training-and-alignment/rlvr-and-grpo/README.md)
- [知识蒸馏](05-post-training-and-alignment/distillation/README.md)
- [合成数据与自改进](05-post-training-and-alignment/synthetic-data/README.md)
- [持续学习与遗忘](05-post-training-and-alignment/continual-learning/README.md)
- [安全对齐与奖励投机](05-post-training-and-alignment/safety-alignment/README.md)
- [知识编辑与模型更新](05-post-training-and-alignment/knowledge-editing/README.md)

<a id="06-reinforcement-learning"></a>

## 强化学习

- [MDP、状态与动作](06-reinforcement-learning/mdp/README.md)
- [回报、价值函数与 Bellman 方程](06-reinforcement-learning/returns-and-bellman/README.md)
- [动态规划与策略迭代](06-reinforcement-learning/dynamic-programming/README.md)
- [Monte Carlo 与 TD Learning](06-reinforcement-learning/monte-carlo-and-td/README.md)
- [Q-Learning 与 DQN](06-reinforcement-learning/q-learning-and-dqn/README.md)
- [Policy Gradient 与 REINFORCE](06-reinforcement-learning/policy-gradient/README.md)
- [Actor-Critic](06-reinforcement-learning/actor-critic/README.md)
- [优势估计与 GAE](06-reinforcement-learning/advantage-estimation/README.md)
- [PPO 与 TRPO](06-reinforcement-learning/ppo-and-trpo/README.md)
- [探索与奖励设计](06-reinforcement-learning/exploration/README.md)
- [离线强化学习](06-reinforcement-learning/offline-rl/README.md)
- [基于模型的强化学习](06-reinforcement-learning/model-based-rl/README.md)

<a id="07-agents"></a>

## Agent 与知识系统

- [ReAct 与工具反馈循环](07-agents/react/README.md)
- [Agent 与 Workflow](07-agents/agent-and-workflow/README.md)
- [工具调用与 Function Calling](07-agents/tool-use/README.md)
- [MCP 与工具协议](07-agents/mcp-and-tool-protocols/README.md)
- [规划、搜索与反思](07-agents/planning-and-search/README.md)
- [上下文工程](07-agents/context-engineering/README.md)
- [Agent 记忆](07-agents/memory/README.md)
- [检索增强生成（RAG）](07-agents/rag/README.md)
- [检索与重排序](07-agents/retrieval-and-reranking/README.md)
- [多 Agent 协作](07-agents/multi-agent/README.md)
- [Agent Harness、Skills 与执行框架](07-agents/harness-and-skills/README.md)
- [浏览器与计算机使用 Agent](07-agents/computer-use/README.md)
- [Agent 学习与轨迹优化](07-agents/agent-learning/README.md)

<a id="08-multimodal-and-generative-models"></a>

## 多模态与生成模型

- [变分自编码器（VAE）](08-multimodal-and-generative-models/vae/README.md)
- [生成对抗网络（GAN）](08-multimodal-and-generative-models/gan/README.md)
- [扩散模型](08-multimodal-and-generative-models/diffusion/README.md)
- [Flow Matching 与 Rectified Flow](08-multimodal-and-generative-models/flow-matching/README.md)
- [CLIP 与多模态对比学习](08-multimodal-and-generative-models/clip-and-contrastive-learning/README.md)
- [视觉语言模型（VLM）](08-multimodal-and-generative-models/vision-language-models/README.md)
- [图像生成与可控编辑](08-multimodal-and-generative-models/image-generation/README.md)
- [语音与音频模型](08-multimodal-and-generative-models/audio-models/README.md)
- [视频理解与生成](08-multimodal-and-generative-models/video-models/README.md)
- [世界模型](08-multimodal-and-generative-models/world-models/README.md)
- [视觉语言动作模型（VLA）](08-multimodal-and-generative-models/vision-language-action/README.md)

<a id="09-training-and-inference-engineering"></a>

## 训练与推理工程

- [KV Cache](09-training-and-inference-engineering/kv-cache/README.md)
- [Quantization（量化）](09-training-and-inference-engineering/quantization/README.md)
- [推测解码](09-training-and-inference-engineering/speculative-decoding/README.md)
- [FlashAttention 与高效算子](09-training-and-inference-engineering/flashattention/README.md)
- [分布式并行总览](09-training-and-inference-engineering/distributed-parallelism/README.md)
- [数据并行与梯度同步](09-training-and-inference-engineering/data-parallelism/README.md)
- [ZeRO 与 FSDP](09-training-and-inference-engineering/zero-and-fsdp/README.md)
- [张量并行](09-training-and-inference-engineering/tensor-parallelism/README.md)
- [流水线并行](09-training-and-inference-engineering/pipeline-parallelism/README.md)
- [序列并行与上下文并行](09-training-and-inference-engineering/sequence-and-context-parallelism/README.md)
- [专家并行](09-training-and-inference-engineering/expert-parallelism/README.md)
- [显存优化](09-training-and-inference-engineering/memory-optimization/README.md)
- [激活检查点与重计算](09-training-and-inference-engineering/activation-checkpointing/README.md)
- [混合精度与低精度训练](09-training-and-inference-engineering/mixed-precision/README.md)
- [推理服务与调度](09-training-and-inference-engineering/serving-and-scheduling/README.md)
- [前缀缓存与请求复用](09-training-and-inference-engineering/prefix-caching/README.md)
- [数据管道与训练恢复](09-training-and-inference-engineering/data-pipeline-and-checkpointing/README.md)

<a id="10-evaluation-and-research"></a>

## 评估与研究方法

- [论文阅读与研究问题](10-evaluation-and-research/paper-reading/README.md)
- [模型基准与能力评估](10-evaluation-and-research/benchmarks/README.md)
- [基线、消融与实验设计](10-evaluation-and-research/ablation-and-experiments/README.md)
- [数据污染与评测泄漏](10-evaluation-and-research/data-contamination/README.md)
- [LLM-as-a-Judge](10-evaluation-and-research/llm-as-a-judge/README.md)
- [Agent 评估](10-evaluation-and-research/agent-evaluation/README.md)
- [强化学习评估](10-evaluation-and-research/rl-evaluation/README.md)
- [可解释性与机制分析](10-evaluation-and-research/interpretability/README.md)
- [可复现性与安全评测](10-evaluation-and-research/reproducibility-and-safety/README.md)

## 维护入口

[导读写作规范](CONTRIBUTING.md) · [知识点模板](templates/knowledge-note.md) · [论文阅读模板](templates/paper-reading.md) · [学习日志](journal/README.md) · [资料库](resources/README.md) · [维护说明](00-learning-roadmap/README.md)
