# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★★ | [OpenAI利用AI发现波及全球70%网站的PHP核心漏洞](https://www.latent.space/p/ainews-openais-patch-the-planet-program) | OpenAI的“修补地球”项目借助未公开模型GPT-5.6 Sol，协助发现了影响全球大部分网站的PHP2Shell重大漏洞，并参与了长达两个月的协同修复。这标志着前沿AI正在成为守护底层互联网基础设施安全的关键力量。 | Latent Space |
| ★★★★★ | [AI不会像人们预想的那样完全替代放射科医生](https://www.jasonwei.net/blog/ai-will-not-automate-radiologists-like-you-think) | 回顾了Geoff Hinton在2016年关于放射科医生将被深度学习取代的激进预言，指出当前该岗位需求不降反升，并分析了AI在医疗影像领域更实际的演进方向。 | Jason Wei |
| ★★★★ | [OpenAI 模型及 Codex 工作流上线 Google Cloud](https://openai.com/index/openai-models-google-cloud) | OpenAI 与 Google Cloud 达成合作，将其前沿模型与 Codex 工作流引入 Gemini Model Garden 及云市场。 | OpenAI |
| ★★★★ | [清华系团队将可辨识隐变量世界模型落地机器人](https://www.qbitai.com/2026/10/504653.html) | 清华系创业公司千诀聚焦隐变量可辨识性研究，主打物理规律学习与跨本体复用，将世界模型实际部署于机器人系统中。 | 量子位 |
| ★★★★ | [DeepSeek 开源推理系统 DeepInfer：单集群日处理 155T tokens](https://www.latent.space/p/ainews-deepseek-deepinfer-open-source) | DeepSeek 开源了前沿推理框架 DeepInfer，单集群每日吞吐达 155T tokens，展现出极高的推理效率与投资回报率。 | Latent Space |
| ★★★★ | [OpenAI 携手科研机构利用数千个 AI 智能体挖掘生物学新线索](https://openai.com/index/scaling-ai-research-for-complex-biological-data) | OpenAI 联合 PerturbAI 与 Scripps Research，通过部署大规模分布式 AI 智能体从数百万脑细胞数据中发掘潜在研究线索。 | OpenAI |
| ★★★★ | [Ropedia W0：融合人类经验的跨本体移动操作世界模型](https://huggingface.co/papers/2610.26855) | Ropedia W0 提出统一运动学表征整合人类与机器人数据，构建支持跨本体复杂移动操作的世界基础模型。 | HF Daily Papers |
| ★★★★ | [Matrix-Game 4.0：利用视频生成模型驱动实时可玩游戏世界](https://huggingface.co/papers/2610.27999) | 该研究将游戏逻辑与视觉合成解耦，结合可执行引擎与自回归视频渲染器，实现低延迟的实时交互式游戏体验。 | HF Daily Papers |
| ★★★★ | [Anthropic展示Claude模型设计抗蝎神经毒素的微型蛋白](https://www.anthropic.com/research/claude-scorpion-toxin-binder-design) | 研究人员利用内部研发版Claude成功设计出能紧密结合蝎神经毒素的微结合蛋白（minibinders），展示了大模型在蛋白质设计等生物物理领域的应用潜力。 | Anthropic |
| ★★★★ | [Mistral AI 推出 Voxtral 3：支持听、想、说、行的一体化语音智能体](https://mistral.ai/news/voxtral-3/) | Mistral AI 发布 Voxtral 3 模型，支持构建具备听觉理解、逻辑推理、语音表达和工具行动能力的 AI 智能体（Agent）。这标志着语音交互进一步迈向能听会说且具备执行力的一体化全模态应用。 | Mistral AI |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
- [2026-10-22](digest/2026/2026-10-22.md)：5 条精选
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
