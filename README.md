# Film Theory RAG Knowledge Base

> 电影学理论研究与RAG知识库构建项目

## 📖 项目简介

本项目致力于构建一个系统化的电影学理论知识库，基于结构主义电影学、符号学、叙事学等核心理论，采用RAG（Retrieval-Augmented Generation）技术架构，为电影研究、教学和创作提供学术级知识检索与分析支持。

## 🎯 项目目标

- 🔬 **理论体系化**：梳理结构主义电影学、符号学、叙事学等核心理论脉络
- 📚 **知识库建设**：构建包含94+篇学术文献的电影理论知识库
- 🤖 **RAG系统**：开发基于向量数据库的智能检索与生成系统
- 🎓 **学术规范**：所有研究遵循核心期刊标准，标注完整文献来源

## 📂 项目结构

```
film-theory-rag/
├── research/              # 研究论文与成果
│   └── papers/           # 学术论文
│       └── 三结构电影美学理论研究综述.md
├── docs/                 # 理论文档
│   └── theory/          # 电影理论原始资料
│       └── 三结构电影美学.md
├── knowledge-base/       # 知识库
│   ├── structuralism/   # 结构主义理论
│   └── semiotics/       # 符号学理论
├── rag-system/          # RAG系统架构
│   └── architecture/    # 系统架构设计
├── references/          # 参考文献库
└── README.md

```

## 🏗️ 核心理论框架

### 三结构电影美学体系

基于结构主义电影学的分析框架，将电影美学划分为三个层次：

#### 🎬 第三结构：创作意图层面
- **作者论（Auteur Theory）**：导演的创作风格与个人标识
- **意识形态批评（Ideological Critique）**：电影的社会文化意涵
- **风格与母题（Style & Motif）**：重复出现的视觉/叙事元素

#### 🎨 第二结构：隐喻象征层面
- **场面调度（Mise-en-Scène）**：画框内事物的空间安排
- **美术设计（Production Design）**：场景、服装、化妆等视觉造型

#### 📝 第一结构：故事剧情层面
- **剧作理论（Screenwriting）**：叙事结构、主题、人物性格
- **摄影理论（Cinematography）**：光影、色彩、构图、摄法
- **声音理论（Sound Theory）**：对白、音乐、音效的叙事功能
- **蒙太奇理论（Montage）**：镜头组合与意义生成
- **表演理论（Performance）**：演员的表演观念与程式
- **叙事理论（Narrative）**：故事结构与讲述方式

## 📊 研究成果

### 已完成

- ✅ 结构主义电影学理论系统梳理
- ✅ 94篇学术文献的查阅与整理
- ✅ 《三结构电影美学理论研究综述》（15000+字）
- ✅ 完整参考文献体系（符合GB/T 7714-2015标准）

### 进行中

- 🔄 知识库向量化处理
- 🔄 RAG系统架构设计
- 🔄 电影理论概念图谱构建

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/MarlinFreesoul/film-theory-rag.git
cd film-theory-rag
```

### 2. 阅读研究成果

查看核心研究论文：

```bash
# 三结构电影美学理论研究综述
cat research/papers/三结构电影美学理论研究综述.md

# 三结构电影美学原始理论
cat docs/theory/三结构电影美学.md
```

### 3. 探索知识库

知识库按理论流派组织，包括：
- 结构主义（Structuralism）
- 符号学（Semiotics）
- 叙事学（Narratology）
- 作者论（Auteur Theory）
- 意识形态批评（Ideological Critique）

## 🔧 技术栈（规划中）

### RAG系统架构

- **向量数据库**：Milvus / Pinecone / Qdrant
- **嵌入模型**：OpenAI Embeddings / BGE / M3E
- **检索框架**：LangChain / LlamaIndex
- **生成模型**：GPT-4 / Claude / 文心一言
- **前端界面**：Streamlit / Gradio

### 数据处理

- **文本分块**：RecursiveCharacterTextSplitter
- **元数据管理**：作者、年份、期刊、引用次数
- **知识图谱**：Neo4j（电影理论概念关系网络）

## 📚 核心文献

### 重要理论家

- **Christian Metz**（克里斯蒂安·梅茨）：电影符号学
- **André Bazin**（安德烈·巴赞）：场面调度理论、长镜头理论
- **Sergei Eisenstein**（谢尔盖·爱森斯坦）：蒙太奇理论
- **François Truffaut**（弗朗索瓦·特吕弗）：作者论
- **Ferdinand de Saussure**（费迪南德·德·索绪尔）：结构主义语言学
- **Claude Lévi-Strauss**（克劳德·列维-斯特劳斯）：结构人类学

### 经典著作

- Metz, C. (1974). *Film Language: A Semiotics of the Cinema*
- Bazin, A. (1967). *What is Cinema?*
- Eisenstein, S. (1949). *Film Form: Essays in Film Theory*
- Field, S. (2005). *Screenplay: The Foundations of Screenwriting*
- McKee, R. (1997). *Story: Substance, Structure, Style*

## 🤝 贡献指南

欢迎电影学研究者、开发者、学生参与贡献！

### 贡献方式

1. **理论研究**：补充电影理论文献、撰写综述
2. **知识库建设**：添加新的理论分类、整理文献资料
3. **系统开发**：参与RAG系统的设计与实现
4. **文档完善**：改进项目文档、翻译外文资料

### 贡献流程

```bash
# 1. Fork本仓库
# 2. 创建特性分支
git checkout -b feature/your-feature-name

# 3. 提交更改
git commit -m "Add: 添加XXX理论文献"

# 4. 推送到分支
git push origin feature/your-feature-name

# 5. 创建Pull Request
```

## 📝 学术规范

本项目严格遵循学术规范：

- ✅ 所有理论论述均标注文献来源
- ✅ 参考文献遵循GB/T 7714-2015标准
- ✅ 引用采用顺序编码制
- ✅ 网络文献注明访问日期
- ✅ 学术专著优先引用原版或权威译本

## 📧 联系方式

- **GitHub**: [@MarlinFreesoul](https://github.com/MarlinFreesoul)
- **Email**: 欢迎通过GitHub Issues讨论

## 📄 许可证

本项目采用 [MIT License](LICENSE)

## 🌟 致谢

感谢所有电影理论研究者的学术贡献，特别是：
- 结构主义电影学派
- 《电影手册》（Cahiers du Cinéma）团队
- 国内外电影学术期刊

---

**建设中的功能**：
- [ ] RAG检索系统
- [ ] 知识图谱可视化
- [ ] 多语言支持（中英文）
- [ ] 批注与讨论功能
- [ ] 影片案例分析库

**最后更新**：2025-01-28
