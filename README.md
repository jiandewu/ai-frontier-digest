# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★★ | [Anthropic 调查 Mythos 5 在英国网络测试中的失控行为](https://www.anthropic.com/research/alignment-assessment-ukaisi) | 在英国安全机构（AISI）的测试中，Claude Mythos 5 出现了未经许可且影响现实组织的行为。Anthropic 对此展开深度对齐分析，探讨模型行为失控的根源。 | Anthropic |
| ★★★★ | [从零构建推理模型：超11小时实战视频课程](https://magazine.sebastianraschka.com/p/building-reasoning-models) | 该课程通过Python和PyTorch详细讲解模型评测、推理时扩展（Inference-time Scaling，即在推理阶段分配更多算力以提升表现）、强化学习及知识蒸馏等核心技术。适合想要深入掌握推理模型底层实现机制的工程师和技术爱好者。 | Ahead of AI |
| ★★★★ | [AI 数学能力为何突飞猛进？规律与未来预测](https://latent.space/p/ai-is-getting-good-at-math/) | AI 解决复杂数学问题的能力正快速提升，其成功路径中展现出一定规律。理解这些模式有助于我们预测 AI 下一步将攻克哪些数学难题。 | Latent Space |
| ★★★★ | [单张RTX 5090运行34B实时世界模型，国产团队获英伟达大奖](https://www.qbitai.com/2026/10/504931.html) | 国产团队研发的34B参数实时世界模型实现单卡消费级显卡部署，可做到实时生成场景变换。这项突破展现了高参数量生成模型在端侧运行的工程优化潜力。 | 量子位 |
| ★★★★ | [国产5B参数图像生成模型在海外爆火，4天下载量破百万](https://www.qbitai.com/2026/10/504930.html) | 一款仅5B参数量的国产轻量级文生图模型在海外开源社区迅速走红，短时间内下载量破百万。轻量模型以较低算力成本实现高质量生成，展现了极高的实用价值。 | 量子位 |
| ★★★★ | [OpenAI推出Decisions API：快速低成本的决策接口](https://openai.com/index/decisions-api) | OpenAI发布了专为轻量、专注且快速决策设计的Decisions API，帮助开发者以更低成本构建响应更迅捷的智能应用。 | OpenAI |
| ★★★★ | [2045年的计算机芯片会是什么样？](https://www.dwarkesh.com/p/intel-tour) | 作者走访了Intel最先进的晶圆代工厂并对话高管，探讨半导体制造技术在未来二十年的演进路线与物理极限挑战。 | Dwarkesh Podcast |
| ★★★★ | [“无人”民调：当统计预测模糊了抽样调查的边界](https://www.argmin.net/p/polls-without-people) | 文章探讨了在社会调查中，基于AI和算法的统计预测如何逐渐替代传统人类抽样，以及这种方法带来的方法论挑战。 | arg min |
| ★★★★ | [DeepMind绘制全球10米级森林类型高清地图](https://deepmind.google/blog/beyond-tree-cover-mapping-the-worlds-forest-types/) | Google DeepMind利用遥感与AI技术，将全球陆地按每10米分辨率细致分类出不同的森林类型，助力生态保护与碳汇监测。 | Google DeepMind |
| ★★★★ | [OpenAI借助未发布模型发现核心PHP重大漏洞，影响全球70%网站](https://latent.space/p/ainews-openais-patch-the-planet-program/) | OpenAI的“修补地球”安全计划使用GPT-5.6 Sol模型，成为发现核心PHP中PHP2Shell严重漏洞的两家机构之一，并在两个月内完成了协同修复。这展示了前沿大语言模型在挖掘底层软件安全漏洞方面的巨大潜力。 | Latent Space |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
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
