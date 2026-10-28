# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★★ | [Google DeepMind 发布 Genie 4：新一代实时超写实世界模拟器](https://deepmind.google/blog/genie-4-a-new-generation-of-world-simulation/) | Google DeepMind 推出全新的世界模型 Genie 4，能够在实时交互模拟中呈现前所未有的超高逼真度。世界模型即能理解物理规律并预测环境变化的 AI 系统，该技术对于具身智能与交互式虚拟世界构建具有重大价值。 | Google DeepMind |
| ★★★★ | [人形机器人全开源：从机械硬件图纸到运动算法完整公开](https://www.qbitai.com/2026/10/505865.html) | 该项目开源了人形机器人的全部图纸、关节硬件设计与核心运动算法，支持个人直接下载复刻。极大降低了具身智能硬件的开发与学习门槛。 | 量子位 |
| ★★★★ | [OCR新开源框架打破限制：KV缓存压降96%，长文档无上限](https://www.qbitai.com/2026/10/505773.html) | 该开源文档解析模型将大模型注意力的KV Cache（键值缓存，存放历史上下文计算结果的显存）优化到近乎常数，显存消耗骤降96%。大幅提升了海量页面文档智能识别的处理速度与成本效益。 | 量子位 |
| ★★★★ | [Anthropic冲刺2万亿美元IPO：招股书核心数据曝光](https://latent.space/p/ainews-anthropic-s1/) | 报道梳理了Anthropic披露的高达1400%增长率、巨额现金储备及云计算渠道收入等关键财务数据。这是观察大模型独角兽商业化进程与财务健康度的重要行业风向标。 | Latent Space |
| ★★★★ | [Anthropic 实测研究：AI 智能体如何潜移默化影响人类专家的决策](https://www.anthropic.com/research/agents-judgment-calls) | Anthropic 让 50 名专业分析师使用编程智能体 Claude Code 完成统计分析，并在两个均合理的方案间随机植入 AI 偏向。结果显示大部分专家顺从了 AI 的倾向，且事后很少承认受其影响，揭示了人机协同中不易察觉的算法偏好引导风险。 | Anthropic |
| ★★★★ | [OpenAI携手学界探索基础科学：公布多项数学与物理难题的模型研究结果](https://openai.com/index/building-scientific-understanding-with-academic-communities) | OpenAI公开了模型在挂谷猜想、指数时间假设及量子色动力学等前沿科学课题上的推理成果，并探讨科研人员如何验证及在此基础上进一步探索，体现了AI辅助重大科学发现的潜力。 | OpenAI |
| ★★★ | [Survival LLM：可完全在本地电脑离线运行的应急知识库与 AI 助手](https://www.brangus.io/survival-llm) | 该开源项目将大语言模型与应急生存资料库打包，支持在个人电脑上完全离线部署。用户即使在断网或极端紧急情况下，也能随时检索关键知识并获取 AI 答疑支持。 | Hacker News |
| ★★★ | [Anthropic团队揭秘：如何用Claude打造Claude平台](https://latent.space/p/opus55/) | Anthropic工程团队分享了Claude平台的工程架构实践，重点阐述了如何将模型的推理“大脑”与执行工具的“双手”解耦以构建可靠的AI智能体。对理解企业级Agent系统架构设计很有启发。 | Latent Space |
| ★★★ | [Google 提出睡眠机制框架：助力大语言模型在持续学习中保留旧知识](https://research.google/blog/the-sleep-framework-a-new-way-for-llms-to-retain-knowledge-in-continual-learning/) | Google Research 探索了一种名为睡眠机制的新框架，旨在解决大语言模型在持续吸收新知识时容易遗忘旧知识的问题。该机制借鉴生物大脑在睡眠中巩固记忆的原理，提升模型的终身学习能力。 | Google Research |
| ★★★ | [大语言模型能否准确评估科研构想的新颖性？](https://huggingface.co/blog/allenai/novelty-bench) | 该研究探讨了大模型作为科研评审工具的可信度，专门测试其在识别研究 Idea 原创性与创新度方面的表现，对未来 AI 辅助科研和学术同行评议具有重要参考意义。 | Hugging Face |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
- [2026-10-28](digest/2026/2026-10-28.md)：10 条精选
- [2026-10-27](digest/2026/2026-10-27.md)：4 条精选
- [2026-10-26](digest/2026/2026-10-26.md)：10 条精选
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
