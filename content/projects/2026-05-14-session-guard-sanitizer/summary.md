## 项目概述

**Session Guard Phase 1: Pre-Request Sanitizer** 是一个防御性的预请求审查器设计，用于解决 OpenAI 兼容 API 中常见的 HTTP 400 错误：

```
an assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'
```

该审查器通过扫描消息历史中的孤立 `assistant.tool_calls` 条目，并插入合成的 `role="tool"` 消息来修复问题。

## 迁移价值

- **安全功能设计**: 完整记录了防御性编程的实现方案
- **可复用**: 审查器模式可应用于其他类似场景
- **测试覆盖**: 包含 6 个合成测试用例，验证各种边界条件
- **长期参考**: 作为工具调用错误处理的参考实现

## 内容摘要

- **核心函数**: `_sanitize_orphan_tool_calls_before_request()`
- **集成点**: `call_llm()` (同步) 和 `async_call_llm()` (异步)
- **关键特性**:
  - 深拷贝输入，不修改调用者状态
  - 幂等性：重复运行产生相同结果
  - 日志输出限制（最多 10 个 ID）
  - 合成消息清晰标记 `[RECOVERED_ORPHAN_TOOL_CALL]`
- **测试覆盖**: 6 个测试用例，全部通过
- **风险等级**: 低 — 仅添加合成消息，不删除或修改现有消息

## 使用建议

- 作为 OpenAI API 工具调用错误处理的参考实现
- 了解防御性编程和预请求审查模式
- 参考合成测试用例的设计方法

## 注意事项

- 该审查器是临时修复，根本问题（上下文压缩器中的截断/压缩 bug）需要单独修复
- 建议监控网关日志，评估孤儿工具调用的频率
- 如需回滚，可从备份恢复原始文件

## 是否长期参考

是。作为防御性编程和工具调用错误处理的参考案例，具有长期价值。
