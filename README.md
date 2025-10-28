# Film Theory RAG Knowledge Base

电影理论RAG知识库 - AI辅助电影创作系统的理论基础与实现

> **作者**: Marlin阿杰
> **理论基础**: 三篇工作论文 ([Working Papers](./research/papers/))
> **当前版本**: v0.1.0

## 项目概述

本项目是一个基于RAG（Retrieval-Augmented Generation）架构的电影理论知识库，旨在为AI辅助电影创作提供理论支持和实现框架。

### 核心理论基础

1. **[Working Paper 01](./research/papers/01-马尔可夫电影创作状态理论.md)**: 马尔可夫电影创作状态理论
   - 三状态模型（原型/当前/投射）
   - 导演核心张力的压缩表示（α系数）
   - ACE框架的马尔可夫实现

2. **[Working Paper 02](./research/papers/02-认知共振理论与五阶段创作流.md)**: 认知共振理论与五阶段创作流
   - AI与人类的对称共振关系
   - 五阶段创作流（明确→聚焦→发散→收束→整理）
   - 按智分配的协作哲学
   - 多模态激发理论

3. **[Working Paper 03](./research/papers/03-动态充分性与三维创作导航系统.md)**: 动态充分性与三维创作导航系统
   - 动态充分性原则（关系性而非绝对）
   - 三维创作空间导航（结构×阶段×进度）
   - 三重触发机制（主动/卡点/停滞）
   - 慢协商设计哲学

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动API服务

```bash
python backend/api/query_interface.py
```

服务将在 `http://localhost:8000` 启动

### 3. 查看API文档

访问 `http://localhost:8000/docs` 查看交互式API文档

### 4. 运行测试

```bash
# 确保API服务已启动
python tests/test_api.py
```

## 核心功能

### 三大知识库模块

1. **理论状态库**: 导演核心张力、三结构理论、理论概念
2. **作品记忆库**: 多媒体片段、张力关联、多维检索
3. **创作者状态库**: 三维位置追踪、激发偏好、状态管理

### 三重触发机制

1. 创作者主动请求
2. AI卡点检测（≥3次）
3. 操作停滞检测（≥120秒）

### 动态充分性计算

基于创作者画像动态判断激发是否充分（关系性而非绝对）

## 已收录数据

- **导演**: 侯孝贤、诺兰（含核心张力与代表作分析）
- **理论**: 三结构理论、五阶段创作流
- **作品**: 7部代表作的三结构分析

## 文档

- [知识库详细文档](./docs/KNOWLEDGE_BASE.md)
- [API文档](./backend/api/README.md)
- [工作论文](./research/papers/)

## 技术栈

Python 3.8+ · FastAPI · Pydantic · YAML · ChromaDB(计划)

## 许可证

MIT License

---

**Powered by**: 马尔可夫思维 × 认知共振理论 × 动态充分性原则
