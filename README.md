# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★★ | [DeepInfer开源：专为DeepSeek模型打造的高性能推理框架](https://github.com/deepseek-ai/DeepInfer) | DeepInfer作为面向DeepSeek系列架构深度优化的高性能推理引擎引发社区广泛关注，显著优化了显存占用与吞吐表现。 | Hacker News |
| ★★★★★ | [如何利用决策模型（Decision Models）进行大模型评估](https://hamel.dev/blog/posts/decision-model-evals/) | 文章探讨了近期涌现的各家决策模型及其在自动化评估领域的应用，指导开发者如何利用这类专用模型优化 LLM 评估流程。 | Hamel Husain |
| ★★★★★ | [MemT-1.0：迈向原生记忆演进的基础模型架构](https://huggingface.co/papers/2610.26825) | MemT-1.0 提出了一种原生记忆架构，将连续记忆直接嵌入到基础模型的计算流中，显著提升了长上下文处理效率和智能体任务性能。 | HF Daily Papers |
| ★★★★★ | [AI不会像人们预想的那样完全替代放射科医生](https://www.jasonwei.net/blog/ai-will-not-automate-radiologists-like-you-think) | 回顾了Geoff Hinton在2016年关于放射科医生将被深度学习取代的激进预言，指出当前该岗位需求不降反升，并分析了AI在医疗影像领域更实际的演进方向。 | Jason Wei |
| ★★★★★ | [谷歌开源RSI新成果：华人团队主导Harness层自我改进机制](https://www.qbitai.com/2026/10/504184.html) | 谷歌开源针对Harness层的递归自我改进（RSI）新研究，展示了模型如何通过优化交互与评估框架实现自主迭代提升。 | 量子位 |
| ★★★★ | [OpenAI 模型及 Codex 工作流上线 Google Cloud](https://openai.com/index/openai-models-google-cloud) | OpenAI 与 Google Cloud 达成合作，将其前沿模型与 Codex 工作流引入 Gemini Model Garden 及云市场。 | OpenAI |
| ★★★★ | [清华系团队将可辨识隐变量世界模型落地机器人](https://www.qbitai.com/2026/10/504653.html) | 清华系创业公司千诀聚焦隐变量可辨识性研究，主打物理规律学习与跨本体复用，将世界模型实际部署于机器人系统中。 | 量子位 |
| ★★★★ | [OpenAI 携手科研机构利用数千个 AI 智能体挖掘生物学新线索](https://openai.com/index/scaling-ai-research-for-complex-biological-data) | OpenAI 联合 PerturbAI 与 Scripps Research，通过部署大规模分布式 AI 智能体从数百万脑细胞数据中发掘潜在研究线索。 | OpenAI |
| ★★★★ | [Ropedia W0：融合人类经验的跨本体移动操作世界模型](https://huggingface.co/papers/2610.26855) | Ropedia W0 提出统一运动学表征整合人类与机器人数据，构建支持跨本体复杂移动操作的世界基础模型。 | HF Daily Papers |
| ★★★★ | [Battle Drones：通过 Claude 打造的支持音频近场对战的 RTS 网页游戏](https://simonwillison.net/2026/Oct/20/battledrones/) | Simon Willison 探索通过向 Claude 发出提示词打造了一款即时战略游戏 Battle Drones，其创新地利用音频信号在近距离设备间同步游戏状态实现多人对战。 | Simon Willison |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
- [2026-10-21](digest/2026/2026-10-21.md)：10 条精选
- [2026-10-20](digest/2026/2026-10-20.md)：10 条精选
<!-- archive:end -->

## 来源

<!-- sources:start -->
- **研究者与作者**：Simon Willison、Andrej Karpathy、Lilian Weng、Ahead of AI（Sebastian Raschka）、Interconnects（Nathan Lambert）、Eugene Yan、Hamel Husain、One Useful Thing（Ethan Mollick）、Import AI（Jack Clark）、Dwarkesh Podcast（Dwarkesh Patel）、Jason Wei、arg min（Ben Recht）、AI as Normal Technology（Arvind Narayanan & Sayash Kapoor）、Sander Dieleman、Tim Dettmers、Phil Schmid、Vicki Boykis、Armin Ronacher、Understanding AI（Timothy B. Lee）
- **新闻汇总**：Latent Space、量子位、宝玉
- **实验室**：OpenAI、Google DeepMind、Google Research、Hugging Face、Thinking Machines、Anthropic、Mistral AI、xAI、AISI（UK AI Security Institute）
- **社区**：Hacker News 首页 AI 相关讨论（200 分以上）、Hugging Face Daily Papers（100 赞以上）
<!-- sources:end -->

来源列表在 [`feeds.csv`](feeds.csv)，增删一行即可；`python3 -m digest.check_feeds` 列出失效或长期未更新的 feed。原始记录在 [`data/items/`](data/items)。
