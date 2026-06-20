---
name: transformer-decoding
description: Amit Shekhar 的 Transformer 架构解析博客，系统讲解 Transformer 各组件
tags: [transformer, deep-learning, architecture, llm, tutorial]
hall: research
date: 2026-04-07
version: 1.0.0
---

# Decoding Transformer Architecture

## 基本信息

- **作者**: Amit Shekhar (Outcome School 创始人, IIT 2010-14)
- **来源**: x.com/amitiitbhu/status/2041479290580287543
- **浏览**: 3,077

## 核心观点

> "Transformer 将一系列 token 作为输入，输出一系列 token。本质上是一个 tokens-in, tokens-out 的机器。每个组件都是简单的，复杂性来自于它们的堆叠方式。"

## 文章大纲

1. **为什么需要 Transformer** — 解决 RNN 的遗忘和速度问题
2. **架构的两半** — Encoder (理解输入) + Decoder (生成输出)
3. **Tokenization、Embedding、Positional Encoding**
4. **Attention 机制和 Multi-Head Attention**
5. **Feed-Forward Networks、Residual Connections、Layer Normalization**
6. **Encoder 和 Decoder 如何工作**
7. **数据流经整个架构**
8. **Transformer 的三种变体**
9. **为什么 Transformer 如此强大**

## 关键概念

### RNN 的问题

- **问题 1: 遗忘** — 句子越长，早期单词越容易被遗忘
- **问题 2: 速度慢** — 单词逐个处理，后面的词必须等待

### Transformer 的解决方案

- 同时处理所有输入 token
- 允许 attention 机制建立任意位置之间的联系

### 架构组成

```
输入 → Tokenization → Embedding → Positional Encoding
     → Encoder (self-attention + FFN)
     → Decoder (self-attention + encoder-decoder attention)
     → 输出
```

## 来源

- 博客: outcomeschool.com
- 论文: "Attention Is All You Need" (2017)
