# AI Frontier Digest

AI 前沿技术、研究和应用的中文导读：来自研究者博客、实验室新闻、Hacker News 和 Hugging Face 热门论文，每条附中文标题、摘要、类别和重要度（★1–5）。

## 最新精选

<!-- latest:start -->
| 重要度 | 标题 | 摘要 | 来源 |
|---|---|---|---|
| ★★★★ | [NVIDIA发布Cosmos3-H-Dreams：通过生成式模拟赋能临床手术](https://huggingface.co/blog/nvidia/cosmos3-h-dreams) | NVIDIA推出Cosmos3-H-Dreams，利用先进的生成式模拟技术将真实临床手术场景数字化，为医学培训与手术规划提供高保真环境。 | Hugging Face |
| ★★★★ | [DeepInfer开源：专为DeepSeek模型打造的高性能推理框架](https://github.com/deepseek-ai/DeepInfer) | DeepInfer作为面向DeepSeek系列架构深度优化的高性能推理引擎引发社区广泛关注，显著优化了显存占用与吞吐表现。 | Hacker News |
| ★★★★ | [如何利用决策模型（Decision Models）进行大模型评估](https://hamel.dev/blog/posts/decision-model-evals/) | 文章探讨了近期涌现的各家决策模型及其在自动化评估领域的应用，指导开发者如何利用这类专用模型优化 LLM 评估流程。 | Hamel Husain |
| ★★★★ | [Claude 新模型细节曝光：强调跳出思维定势与根治代码 Bug](https://www.qbitai.com/2026/10/504314.html) | 报道披露了 Claude 新模型的技术特点与实测表现，重点展示其在打破常规思维、深度定位并彻底修复 Bug 方面的能力。 | 量子位 |
| ★★★★ | [MemT-1.0：迈向原生记忆演进的基础模型架构](https://huggingface.co/papers/2610.26825) | MemT-1.0 提出了一种原生记忆架构，将连续记忆直接嵌入到基础模型的计算流中，显著提升了长上下文处理效率和智能体任务性能。 | HF Daily Papers |
| ★★★★ | [OpenAI宣布收购生命科学AI平台Orchestra Bio](https://openai.com/index/openai-to-acquire-orchestra-bio) | OpenAI通过收购Orchestra Bio将AI运营能力引入生命科学研发领域，旨在赋能生物医药团队加速药物开发与创新治疗方案落地。 | OpenAI |
| ★★★★ | [OpenAI提升低资源编程语言代码能力，覆盖COBOL迁移等场景](https://openai.com/index/low-resource-programming-languages) | OpenAI针对ChatGPT在低资源编程语言上的表现进行了增强，并引入面向软件工程、SQLite以及传统COBOL迁移的新基准评估。 | OpenAI |
| ★★★★ | [谷歌开源RSI新成果：华人团队主导Harness层自我改进机制](https://www.qbitai.com/2026/10/504184.html) | 谷歌开源针对Harness层的递归自我改进（RSI）新研究，展示了模型如何通过优化交互与评估框架实现自主迭代提升。 | 量子位 |
| ★★★★ | [深入未知：在开放性科学研究难题上评测AI智能体](https://huggingface.co/papers/2610.19159) | 研究人员通过让 AI 智能体根据未发表的研究方向起草后续论文，系统评估其应对开放科学问题的能力。结果显示目前没有智能体能达到专家级标准，且多数存在虚假论断或自相矛盾的证据。 | HF Daily Papers |
| ★★★★ | [GPT-6-Astra 是否已实现具身智能？](https://huggingface.co/papers/2610.22471) | 论文评测了 GPT-6-Astra 通过上下文学习在多种机器人任务上的高表现，指出其在真实部署中仍面临高昂演示成本、过长执行时间以及具身实用性上的明显差距。 | HF Daily Papers |
| ★★★★ | [LEV：通过循环决策模型实现无需生成Token的深度推理](https://huggingface.co/papers/2610.20951) | LEV 提出一种循环决策模型架构，通过在不生成 Token 的情况下循环迭代层结构来加深推理深度。该方法显著提升了模型在难题上的准确率，并能利用停止机制实现自适应计算。 | HF Daily Papers |
| ★★★★ | [ACT3D：利用强化学习在3D世界中实现主动思考与探索](https://huggingface.co/papers/2610.21783) | ACT3D 通过强化学习训练视觉语言模型，仅凭单张第一人称视角图像即可主动探索 3D 环境。该方法在无需直接探索监督的情况下，通过自适应且针对具体问题的导航显著提升了回答准确率。 | HF Daily Papers |
<!-- latest:end -->

## 每日汇总

<!-- archive:start -->
- [2026-10-20](digest/2026/2026-10-20.md)：61 条
<!-- archive:end -->

## 来源

- **研究者与作者**：Simon Willison、Andrej Karpathy、Lilian Weng、Sebastian Raschka（Ahead of AI）、Nathan Lambert（Interconnects）、Chip Huyen、Eugene Yan、Hamel Husain、Ethan Mollick（One Useful Thing）、Jack Clark（Import AI）、Dwarkesh Patel
- **新闻汇总**：AINews、Latent Space、量子位、宝玉
- **实验室**：OpenAI、Google DeepMind、Google Research、Hugging Face
- **社区**：Hacker News 首页 AI 相关讨论（200 分以上）、Hugging Face Daily Papers（30 赞以上）

完整列表见 [`digest/sources.py`](digest/sources.py)，原始记录在 [`data/items/`](data/items)。
