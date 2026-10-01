# 训练与推理工程

[返回总索引](../README.md)

## 二级知识点

| 知识点 | 子主题范围 |
| --- | --- |
| [KV Cache](kv-cache/README.md) | 为什么缓存 K/V、缓存容量估算、Prefill 与 Decode、GQA/MLA、分页、量化、淘汰与复用 |
| [Quantization（量化）](quantization/README.md) | PTQ 与 QAT、权重、激活与 KV 量化、INT8/INT4/FP8、GPTQ/AWQ、误差与硬件速度 |
| [推测解码](speculative-decoding/README.md) | Draft 与 Verify、接受与拒绝采样、分布保持、自推测、树状推测、MTP、端到端延迟 |
| [FlashAttention 与高效算子](flashattention/README.md) | IO-aware、分块、在线 softmax、重计算、FlashAttention 系列、Kernel Fusion、硬件适配 |
| [分布式并行总览](distributed-parallelism/README.md) | DP、TP、PP、SP、CP 与 EP、3D/4D 并行、通信与计算、拓扑、策略组合 |
| [数据并行与梯度同步](data-parallelism/README.md) | DDP、All-reduce、Bucket、通信重叠、有效 Batch Size、多机扩展 |
| [ZeRO 与 FSDP](zero-and-fsdp/README.md) | 参数、梯度与优化器状态分片、ZeRO Stages、All-gather、Reduce-scatter、Offload |
| [张量并行](tensor-parallelism/README.md) | 行与列切分、层内通信、Attention 与 FFN 分片、通信带宽、算子布局 |
| [流水线并行](pipeline-parallelism/README.md) | Microbatch、流水线气泡、GPipe、1F1B、交错调度、阶段均衡 |
| [序列并行与上下文并行](sequence-and-context-parallelism/README.md) | 激活切分、SP 与 CP 区别、Ring Attention、长序列通信、注意力分块 |
| [专家并行](expert-parallelism/README.md) | 专家放置、Token Dispatch、All-to-all、负载不均衡、通信与计算重叠 |
| [显存优化](memory-optimization/README.md) | 参数、梯度、状态与激活、缓存与临时张量、显存峰值、分片、重计算、Offload 与压缩 |
| [激活检查点与重计算](activation-checkpointing/README.md) | 保存与重算、选择性重计算、时间显存权衡、随机数状态、计算图生命周期 |
| [混合精度与低精度训练](mixed-precision/README.md) | FP32、FP16、BF16 与 FP8、Loss Scaling、主权重、数值稳定性、精度验证 |
| [推理服务与调度](serving-and-scheduling/README.md) | Continuous Batching、Chunked Prefill、Prefill/Decode 分离、TTFT、TPOT、吞吐与尾延迟 |
| [前缀缓存与请求复用](prefix-caching/README.md) | Prefix Cache、Radix Tree、共享 KV、命中与失效、跨请求复用、缓存隔离 |
| [数据管道与训练恢复](data-pipeline-and-checkpointing/README.md) | 数据版本、Packing、采样与随机种子、分布式 Checkpoint、断点恢复、运行状态一致性 |
| [模型剪枝与稀疏化](pruning-and-sparsity/README.md) | 结构化与非结构化稀疏、剪枝标准、稀疏训练、稀疏矩阵算子、与量化的组合、质量与真实加速 |
| [性能分析与计算瓶颈](performance-profiling/README.md) | FLOPs 与实际延迟、Roofline、计算受限与带宽受限、Profiler、GPU 利用率、通信瓶颈、端到端成本 |

<!-- new-note-index -->
