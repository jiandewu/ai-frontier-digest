# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★★ | [Interconnects 播客：解读 Kimi K3.1 Pro、网络新现实与 Muse 模型](https://www.interconnects.ai/p/podcast-kimi-k31-pro-the-new-cyber) | 本期播客讨论了 Kimi K3.1 Pro、AI 带来的网络新现实以及对 Muse 相关进展的思考。内容涵盖近期前沿模型的最新动态与行业观察。 | Interconnects |
| ★★★★ | [芯片厂商 Cerebras 成功部署万亿参数级 AI 模型](https://www.cerebras.ai/blog/how-we-deploy-trillion-parameter-frontier-models-on-cerebras) | 主打超大晶圆级芯片的 Cerebras 宣布实现万亿参数（Trillion-Parameter）规模 AI 模型的部署。这验证了其专用硬件在支撑超大规模模型低延迟运行方面的工程与算力扩展能力。 | Hacker News |
| ★★★★ | [从零构建推理模型：超11小时实战视频课程](https://magazine.sebastianraschka.com/p/building-reasoning-models) | 该课程通过Python和PyTorch详细讲解模型评测、推理时扩展（Inference-time Scaling，即在推理阶段分配更多算力以提升表现）、强化学习及知识蒸馏等核心技术。适合想要深入掌握推理模型底层实现机制的工程师和技术爱好者。 | Ahead of AI |
| ★★★★ | [单张RTX 5090运行34B实时世界模型，国产团队获英伟达大奖](https://www.qbitai.com/2026/10/504931.html) | 国产团队研发的34B参数实时世界模型实现单卡消费级显卡部署，可做到实时生成场景变换。这项突破展现了高参数量生成模型在端侧运行的工程优化潜力。 | 量子位 |
| ★★★★ | [国产5B参数图像生成模型在海外爆火，4天下载量破百万](https://www.qbitai.com/2026/10/504930.html) | 一款仅5B参数量的国产轻量级文生图模型在海外开源社区迅速走红，短时间内下载量破百万。轻量模型以较低算力成本实现高质量生成，展现了极高的实用价值。 | 量子位 |
| ★★★ | [美国媒体与艺术领域流失20万工作岗位，AI究竟造成了多大冲击？](https://www.apricitas.io/p/ai-and-the-fall-of-the-creative-class) | 文章探讨了美国媒体、影视及艺术行业近年来减少20万个岗位的现状，深入分析人工智能技术在其中实际起到的替代与分流作用。这引发了公众对生成式AI对真实劳动力市场和创意产业深远影响的广泛讨论。 | Hacker News |
| ★★★ | [LayerEditor：将图像编辑转化为可复用图层的全新方法](https://huggingface.co/papers/2610.24738) | 新研究提出 LayerEditor，通过联合Token建模和编辑先验蒸馏，将自然语言图像编辑转化为带有透明通道的RGBA图层生成。这使得局部修改与图层复用变得更加精准高效，对数字设计工具意义重大。 | HF Daily Papers |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
- [2026-10-25](digest/2026/2026-10-25.md)：3 条精选
- [2026-10-24](digest/2026/2026-10-24.md)：7 条精选
- [2026-10-23](digest/2026/2026-10-23.md)：10 条精选
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
