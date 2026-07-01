# 中文翻译（待人工补全）：Is High Quality Software Worth the Cost?

> 本条目由普通网页导入路线生成。当前仓库未配置稳定翻译引擎，因此这里先保留合法的中文占位草稿，避免伪造完整人工翻译。
> 请在后续人工或 LLM 校对流程中补全正式译文。

## 原文结构参考

# Is High Quality Software Worth the Cost?
29 May 2019
[Martin Fowler](https://martinfowler.com/)
programming style
productivity
project planning
technical debt
## Contents
- We are used to a trade-off between quality and cost
- Software quality means many things
- At first glance, internal quality does not matter to customers
- Internal quality makes it easier to enhance software
- Customers do care that new features come quickly
- Visualizing the impact of internal quality
- Even the best teams create cruft
- High quality software is cheaper to produce
### Sidebars
- Dora studies on elite teams
A common debate in software development projects is between spending time
    on improving the quality of the software versus concentrating on releasing
    more valuable features. Usually the pressure to deliver functionality
    dominates the discussion, leading many developers to complain that they
    don't have time to work on architecture and code quality.
Betteridge's Law of headlines is an
    adage that says any article with a headline or title that ends in a question
    mark can be summarized by “no”. Those that know me would not doubt my desire
    to subvert such a law. But this article goes further than that - it subverts
    the question itself. The question assumes the common trade-off between
    quality and cost. With this article I'll explain that this trade-off does
    not apply to software - that high quality software is actually cheaper to
    produce.
Although most of my writing is aimed at professional software developers,
    for this article I'm not going to assume any knowledge of the mechanics of
    software development. My hope is that this is an article that can be
    valuable to anyone involved with thinking about software efforts,
    particul