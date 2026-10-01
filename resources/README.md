# 论文与资料库

[返回首页](../README.md) · [论文阅读模板](../templates/paper-reading.md)

这是一组经典起点，后续根据每日知识点继续扩展。年份使用论文首次公开年份；“页面已核验”只表示链接页面已打开并核对标题，不表示已完成精读或复现。初始核验日期：2026-10-01。

## 论文

| 主题 | 论文 | 年份 | 阅读目的 | 访问核验 | 个人阅读 |
| --- | --- | --- | --- | --- | --- |
| 深度学习 | [Learning representations by back-propagating errors](https://www.nature.com/articles/323533a0) | 1986 | 反向传播的经典论文；对照链式法则推导 | 页面已核验（摘要可访问） | 待读 |
| 大语言模型 | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | 2017 | §3.2 注意力与多头机制 | 页面已核验 | 待读 |
| 后训练 | [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) | 2021 | 低秩更新如何减少可训练参数 | 页面已核验 | 待读 |
| 后训练 | [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) | 2022 | SFT、奖励模型与 PPO 的衔接 | 页面已核验 | 待读 |
| 后训练 | [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290) | 2023 | 偏好目标与奖励建模的关系 | 页面已核验 | 待读 |
| 强化学习 | [Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347) | 2017 | 策略优化目标与剪裁机制 | 页面已核验 | 待读 |
| Agent | [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | 2022 | 推理、动作与环境观测的交替 | 页面已核验 | 待读 |
| Agent / RAG | [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | 2020 | 参数知识与检索知识的结合 | 页面已核验 | 待读 |
| Agent | [Toolformer: Language Models Can Teach Themselves to Use Tools](https://arxiv.org/abs/2302.04761) | 2023 | 工具调用能力的训练方式 | 页面已核验 | 待读 |

## 教材与官方教程

| 资料 | 用途 | 访问核验 |
| --- | --- | --- |
| [Deep Learning](https://www.deeplearningbook.org/) | 数学基础与深度前馈网络；从目录进入相关章节 | 首页已核验 |
| [PyTorch Autograd 教程](https://docs.pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html) | 对照计算图、梯度与框架行为 | 页面已核验 |
| [Reinforcement Learning: An Introduction, 2nd edition](https://incompleteideas.net/book/the-book-2nd.html) | MDP、Bellman 方程、TD 与策略梯度 | 本次访问超时，待复核 |
| [Stanford CS234](https://web.stanford.edu/class/cs234/) | 强化学习课程与讲义入口 | 页面已核验 |
| [ReAct 作者项目页](https://react-lm.github.io/) | 论文演示与代码入口 | 页面已核验 |

## 收集方法

每次围绕一个问题收集资料，优先 1 篇核心论文 + 1 个官方教程 + 1 个对照方法。把阅读心得写进对应知识点文档；详细论文拆解可复制论文阅读模板放在主题的 `papers/` 子目录，并从知识点链接过去。
