# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★★ | [如何利用决策模型（Decision Models）进行大模型评估](https://hamel.dev/blog/posts/decision-model-evals/) | 文章探讨了近期涌现的各家决策模型及其在自动化评估领域的应用，指导开发者如何利用这类专用模型优化 LLM 评估流程。 | Hamel Husain |
| ★★★★ | [OpenAI 模型及 Codex 工作流上线 Google Cloud](https://openai.com/index/openai-models-google-cloud) | OpenAI 与 Google Cloud 达成合作，将其前沿模型与 Codex 工作流引入 Gemini Model Garden 及云市场。 | OpenAI |
| ★★★★ | [清华系团队将可辨识隐变量世界模型落地机器人](https://www.qbitai.com/2026/10/504653.html) | 清华系创业公司千诀聚焦隐变量可辨识性研究，主打物理规律学习与跨本体复用，将世界模型实际部署于机器人系统中。 | 量子位 |
| ★★★★ | [DeepSeek 开源推理系统 DeepInfer：单集群日处理 155T tokens](https://www.latent.space/p/ainews-deepseek-deepinfer-open-source) | DeepSeek 开源了前沿推理框架 DeepInfer，单集群每日吞吐达 155T tokens，展现出极高的推理效率与投资回报率。 | Latent Space |
| ★★★★ | [OpenAI 携手科研机构利用数千个 AI 智能体挖掘生物学新线索](https://openai.com/index/scaling-ai-research-for-complex-biological-data) | OpenAI 联合 PerturbAI 与 Scripps Research，通过部署大规模分布式 AI 智能体从数百万脑细胞数据中发掘潜在研究线索。 | OpenAI |
| ★★★★ | [Ropedia W0：融合人类经验的跨本体移动操作世界模型](https://huggingface.co/papers/2610.26855) | Ropedia W0 提出统一运动学表征整合人类与机器人数据，构建支持跨本体复杂移动操作的世界基础模型。 | HF Daily Papers |
| ★★★★ | [Matrix-Game 4.0：利用视频生成模型驱动实时可玩游戏世界](https://huggingface.co/papers/2610.27999) | 该研究将游戏逻辑与视觉合成解耦，结合可执行引擎与自回归视频渲染器，实现低延迟的实时交互式游戏体验。 | HF Daily Papers |
| ★★★★ | [Battle Drones：通过 Claude 打造的支持音频近场对战的 RTS 网页游戏](https://simonwillison.net/2026/Oct/20/battledrones/) | Simon Willison 探索通过向 Claude 发出提示词打造了一款即时战略游戏 Battle Drones，其创新地利用音频信号在近距离设备间同步游戏状态实现多人对战。 | Simon Willison |
| ★★★★ | [NVIDIA发布Cosmos3-H-Dreams：通过生成式模拟赋能临床手术](https://huggingface.co/blog/nvidia/cosmos3-h-dreams) | NVIDIA推出Cosmos3-H-Dreams，利用先进的生成式模拟技术将真实临床手术场景数字化，为医学培训与手术规划提供高保真环境。 | Hugging Face |
| ★★★★ | [开源动态观察：DeepSeek V4.1 Flash 1017、美国本土模型与中美监管新规](https://www.interconnects.ai/p/latest-open-artifacts-25-deepseek) | 文章梳理了近期开源 AI 生态进展，聚焦 DeepSeek V4.1 Flash 1017 等模型动态，并探讨西方开源力量应对策略及中美最新的 AI 监管管控政策。 | Interconnects |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
- [2026-10-21](digest/2026/2026-10-21.md)：9 条精选
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
