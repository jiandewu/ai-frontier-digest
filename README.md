# AI Frontier Digest

AI 前沿的中文科普导读：每天从研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文中精选最值得一读的 10 条以内，每条附通俗的中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★ | [OpenAI推出Decisions API：快速低成本的决策接口](https://openai.com/index/decisions-api) | OpenAI发布了专为轻量、专注且快速决策设计的Decisions API，帮助开发者以更低成本构建响应更迅捷的智能应用。 | OpenAI |
| ★★★★ | [2045年的计算机芯片会是什么样？](https://www.dwarkesh.com/p/intel-tour) | 作者走访了Intel最先进的晶圆代工厂并对话高管，探讨半导体制造技术在未来二十年的演进路线与物理极限挑战。 | Dwarkesh Podcast |
| ★★★★ | [“无人”民调：当统计预测模糊了抽样调查的边界](https://www.argmin.net/p/polls-without-people) | 文章探讨了在社会调查中，基于AI和算法的统计预测如何逐渐替代传统人类抽样，以及这种方法带来的方法论挑战。 | arg min |
| ★★★★ | [DeepMind绘制全球10米级森林类型高清地图](https://deepmind.google/blog/beyond-tree-cover-mapping-the-worlds-forest-types/) | Google DeepMind利用遥感与AI技术，将全球陆地按每10米分辨率细致分类出不同的森林类型，助力生态保护与碳汇监测。 | Google DeepMind |
| ★★★★ | [OpenAI利用AI发现波及全球70%网站的PHP核心漏洞](https://www.latent.space/p/ainews-openais-patch-the-planet-program) | OpenAI的“修补地球”项目借助未公开模型GPT-5.6 Sol，协助发现了影响全球大部分网站的PHP2Shell重大漏洞，并参与了长达两个月的协同修复。这标志着前沿AI正在成为守护底层互联网基础设施安全的关键力量。 | Latent Space |
| ★★★★ | [Anthropic捐赠Agent Skills开放标准](https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation) | Anthropic将专为智能体提供专业技能和工作流的标准协议捐给Agentic AI基金会，该标准已被ChatGPT和VS Code等70多个平台采用。 | Anthropic |
| ★★★★ | [Anthropic利用大模型实现大规模代码形式化验证](https://www.anthropic.com/research/formal-verification) | 形式化验证能用数学方法严谨证明代码无特定漏洞，但过去成本极高；Anthropic借助Claude在数周内完成了上百个开源库的安全属性验证。 | Anthropic |
| ★★★ | [OpenShell：专为自主智能体集群打造的安全私密运行时](https://github.com/NVIDIA/OpenShell) | OpenShell为大规模运行自主AI智能体（自主感知并执行任务的程序）提供了隔离、安全且保护隐私的底层运行环境，在社区引发热烈讨论。 | Hacker News |
| ★★★ | [访谈Modal CEO：AI算力的经济学与弹性调度](https://www.latent.space/p/modal-d) | 探讨了云端弹性GPU资源调度、沙盒隔离机制以及AI智能体兴起后背后计算云基础设施的经济学逻辑。 | Latent Space |
| ★★★ | [OlmoEarth v1.3：覆盖全球的高性能地球表征模型](https://huggingface.co/blog/allenai/olmoearth-v1-3) | Hugging Face开源了OlmoEarth v1.3，提供涵盖全球尺度的地理空间嵌入向量（将地理数据转换为高维数学特征），用于地球观测分析。 | Hugging Face |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
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
