# 个人笔记

## 接受

**最核心的接受点是"决定论 → 概率式"范式跃迁这一框架本身。** 我以前零散地思考过 AI 产品的层次问题（模型、上下文、提示词、UI），但从未把它们组织成一个清晰的 6 层结构、并放到 Garrett → Mill → Campbell 的设计史脉络里。Emily Campbell 的厉害之处在于她把"涌现（Emergence）"显式地列为第 6 层——很多讨论 AI 设计的文章都回避这一点，把它当成"非设计问题"或"工程问题"，但她坚持认为：涌现是产品体验的一部分，设计师需要为之设计、监测、响应。这一立场我完全接受。

**第二点接受：渐进式自主（progressive autonomy）取代渐进式信息披露（progressive disclosure）。** 传统产品的 onboarding 假设"用户不懂产品 → 慢慢揭示功能"，但 AI 产品的 onboarding 反过来——"系统不懂用户 → 慢慢学习如何理解用户"。这个视角的翻转非常有解释力，能解释为什么 ChatGPT 早期那种"先教你怎么写 prompt"的 UX 范式正在快速过时。

**第三点接受：治理层（Governance）应该被产品团队正视。** 我以前觉得"Anthropic vs. OpenAI 的安全策略差异"是供应商问题，设计师管不了。但 Emily 的论证让我意识到——一个拒绝回答 X 的模型本身就是一个交互模式，用户能感受到"这家产品更谨慎 / 那家更开放"的差异。设计师至少要为这种差异设计相应的提示与 fallback，而不是假装模型是黑盒。

## 反思

**我自己做 AI 产品时最薄弱的层是驾驭层（Harness）。** 我习惯性地把工具调用、权限、技能、智能体编排都丢给"工程实现"去管，但 Emily 明确指出这些是 UX 的一部分——用户需要看到"系统连了什么、有什么权限、能用什么工具"。我之前为 Hermes 设计 connector / tool 授权时确实让用户能"看到连接了什么"，但没有系统性地想清楚"用户应如何观察 access patterns over time"以及"在什么时点该引入更细粒度的权限"。

**关于涌现的反思——我倾向于低估"小改动级联为大后果"的风险。** OpenAI goblins 那个案例（一个针对"geeky persona"的小训练激励，最终让模型在无关场景里反复出现 goblin 隐喻）是一个深刻的提醒：在概率系统里，你训练时关注的东西会以你预测不到的方式渗入推理。我做 agent prompt / skill 设计时，常常只考虑"这会不会让模型在目标场景里表现更好"，没有充分考虑"这会以什么方式渗入到非目标场景"。下次做 skill 调整前，我应该专门为"副作用"留一轮评估。

**关于 Chat 是否是好界面——我之前过于偏向"非 chat 化"的判断。** Emily 的论证让我看到，chat 之所以流行不是因为它"是最优解"，而是因为它能在一个表面上同时承载"早期直接指令"和"后期监督"两种状态。当系统对用户和任务理解还不够时，chat 是合理的；但当系统已经"earned the user's trust"后，chat 会退化为"instrument panel"。我以前过早地否定 chat，是因为我在评估的总是"成熟期"的 AI，而忽略了"导入期"的 chat 确实有不可替代性。

## 联想

**Emily 的 6 层模型与 OpenClaw/Hermes 的 provider-routing 抽象有结构上的相似性。** 我自己的 Hermes Agent 实际上就在做"对用户可见的层（UI/Telegram）+ 上下文注入层（memory palace）+ provider-routing（harness 的一种） + 不同 LLM provider（model） + provider 政策差异（governance）"的分层。但我没有把"涌现"显式列为第 6 层。**我应该在 Hermes 的 next major version 里引入一个 "emergence monitor" 子系统**，对每个任务跟踪"用户预期 vs. 实际产出"的偏差，作为涌现层的可观测性。

**6 层模型与 OSI 7 层模型、TCP/IP 4 层模型有异曲同工之妙。** 互联网协议分层是"每层只关心相邻层、对自己之上的层提供契约"。AIUX 6 层模型虽然不是严格的"协议栈"，但也有相似的"上游决策会影响下游体验"的瀑布特性（注意 Emily 强调"small changes to one can have an outsized impact on the whole"——正是杠杆点的语言）。我可以用这张表去做 Hermes Agent 的"影响传导图"，让每个 layer owner 看到自己的改动会如何被其他层放大或缩小。

**6 层与"全栈设计师（full-stack designer）"的争论。** Emily 澄清了"全栈"不是"什么都得会"——她要的是"多语境的对话能力"（multilingual）而非"全栈工程能力"。这与 John Maeda 2017 *Design in Tech Report* 里区分"计算型设计师 / 传统型设计师"的二分法一致。我应该把这个澄清写进 Hermes 团队的设计 hiring 标准里——"我们不要求设计师会训练模型，但要求他们能跟 ML 工程师讨论 context rot 的工程原因"。

**与中文 AI 设计圈（少数派、知乎、即刻）的对照。** 国内设计圈讨论 AI UX 时多停留在"prompt 怎么写 / agent 怎么编排"这种执行层细节，缺少像 Emily 这样的"层级化、系统性"框架。少数派上能看到一些"AI 写作工具横评"类文章，但缺少一个把产品体验拆成 6 层、让团队能用同一张图讨论"我们这版改的是哪一层、影响会传到哪些层"的工具。**这是一个内容输出的机会**——可以基于本文写一篇中文版"AI 产品体验 6 层图谱"（附团队协作模板），发到少数派 / 公众号。

## 行动

1. **本周内**：把 Emily 的 6 层模型打印出来贴到工作区，next 一次产品 review 时用它去定位"我们这次的改动属于哪一层、可能级联到哪些层"。把"涌现"层显式列进 review checklist。
2. **本月内**：在 Hermes Agent 的 dev 文档里加一页"全栈式 AI 设计语言能力自检"，列出 6 层每层至少需要能问 / 能答的几个关键问题（参考 Emily 给的"杠杆点"逻辑）。
3. **下个季度**：写一篇中文"AI 产品体验的 6 层图谱"——基于本文 + 我自己的 Hermes 实践，发到少数派或公众号。视觉上用 Emily 那张图的简化版（标注"中文化：conanxin"），但内容加一层"团队如何使用这张图对齐讨论"的实践部分。
4. **长期**：在 Hermes 的 monitoring 里加一个"涌现层"——记录每次 agent 行为与用户预期的偏差，跨 session 聚合。这对应 Emily 说的"Provenance helps teams work backward from a generation to identify how it was formed"。
5. **跨议题对照**：把本文加入"AI 设计"主题的延伸阅读。同一作者 Emily Campbell 的 *Shape of AI*（https://www.shapeof.ai/）也值得单独立一个项目类型条目——它是她维护的 AI 交互模式库，模式分类本身就是"AIUX 6 层模型"的应用实例。

## 引用此文的其他思考者 / 作品

- **Jesse James Garrett** — *The Elements of User Experience* (2000)，AIUX 决定论时代的奠基文献。
- **Jamie Mill** — *Elements of Product Design* (2021)，把 Garrett 模型扩展到"问题空间 + 真实世界"。
- **Donella Meadows** — *Leverage Points*，AIUX 6 层模型背后的系统思维隐喻直接来源。
- **John Maeda** — *2017 Design in Tech Report*，"设计师变技术化 vs. 传统设计价值"二元论。
- **L. M. Sacasas** — *The Convivial Society*，语言衰退与 AI 时代的"语言机器"批评（与本文主题相关但视角不同，已入库：`2026-06-24-theconvivialsociety-owning-our-words`）。
- **Shape of AI** — Emily Campbell 自己维护的 AI 交互模式库，6 层模型的具体应用示例。
- **OpenAI *Where the Goblins Came From*** — 涌现层的经典案例（goblins 事件）。
