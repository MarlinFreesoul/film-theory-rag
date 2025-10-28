# 电影理论RAG知识库文档

## 概述

本知识库是基于三篇工作论文构建的电影理论知识体系，用于支持AI辅助电影创作系统。

**核心论文基础**:
- Working Paper 01: 马尔可夫电影创作状态理论
- Working Paper 02: 认知共振理论与五阶段创作流
- Working Paper 03: 动态充分性与三维创作导航系统

## 知识库架构

```
knowledge_base/
├── theory_state.py        # 理论状态库（三状态模型、张力理论）
├── work_memory.py         # 作品记忆库（多媒体片段、作品分析）
├── creator_profile.py     # 创作者状态库（动态画像、进度追踪）
└── data_loader.py         # 数据加载器（YAML数据加载）

data/
├── theories/              # 理论数据（YAML格式）
│   ├── 三结构理论.yaml
│   └── 五阶段创作流.yaml
├── directors/             # 导演数据（YAML格式）
│   ├── 侯孝贤.yaml
│   └── 诺兰.yaml
├── works/                 # 作品数据（待填充）
└── media/                 # 多媒体素材（待填充）
```

## 三大核心库

### 1. 理论状态库 (Theory State Base)

**功能**: 管理电影理论的结构化知识

**核心概念**:

#### 1.1 导演核心张力 (Director Tension)

每个导演都有其独特的核心张力，这是第三结构（创作意图层）的核心。

```python
class DirectorTension:
    director: str                    # 导演名称
    tension_pair: (str, str)         # 张力对（左↔右）
    tension_type: TensionType        # 张力类型
    alpha: float                     # 压缩系数α (0-1)
    description: str                 # 张力描述
    representative_works: List[str]  # 代表作品
```

**已收录导演**:

| 导演 | 核心张力 | α值 | 类型 |
|------|---------|------|------|
| 侯孝贤 | 静止 ↔ 流逝 | 0.8 | 时间性 |
| 诺兰 | 秩序 ↔ 熵增 | 0.5 | 形而上 |
| 林奇 | 表层 ↔ 潜意识 | 0.3 | 感知性 |

**α值的含义** (来自WP01):
- α = 0.8: 强烈偏向左侧（侯孝贤偏向"静止"）
- α = 0.5: 平衡点（诺兰在秩序与混沌间）
- α = 0.3: 偏向右侧（林奇偏向"潜意识"）

#### 1.2 三结构理论 (Three-Structure Theory)

```
L3: 第三结构（创作意图层）
    └── 核心张力、哲学命题

L2: 第二结构（隐喻象征层）
    └── 视觉隐喻、声音象征

L1: 第一结构（故事剧情层）
    └── 叙事结构、人物关系
```

**检索能力**:
- 按张力类型搜索导演
- 按结构层次检索概念
- 概念关联网络查询

### 2. 作品记忆库 (Work Memory Base)

**功能**: 管理多媒体片段和作品分析数据

**核心概念**:

#### 2.1 媒体片段 (Media Fragment)

```python
class MediaFragment:
    fragment_id: str           # 片段ID
    media_type: MediaType      # 媒体类型（图像/音频/视频/文本）
    source_work: str           # 来源作品
    director: str              # 导演
    content_path: str          # 内容路径
    duration_seconds: float    # 时长（音视频）
    description: str           # 片段描述
    tags: List[str]            # 标签
```

#### 2.2 张力关联 (Tension Association)

每个作品片段都标注了其表现的核心张力：

```python
class TensionAssociation:
    tension_left: str          # 张力左侧
    tension_right: str         # 张力右侧
    balance_point: float       # 平衡点 (0-1)
    confidence: float          # 关联置信度 (0-1)
```

**示例**:
```yaml
fragment: 《悲情城市》开场长镜头
tension:
  left: 静止
  right: 流逝
  balance_point: 0.8  # 偏向静止
  confidence: 0.9
```

**检索能力**:
- 按张力搜索片段
- 按结构层次搜索
- 按情感标签搜索
- 按导演搜索
- 按媒体类型过滤

### 3. 创作者状态库 (Creator Profile Base)

**功能**: 动态构建和追踪创作者画像

**核心概念** (来自WP03动态充分性原则):

#### 3.1 创作者画像 (Creator Profile)

```python
class CreatorProfile:
    # Personality 部分
    core_tensions: List[TensionPair]      # 核心张力
    cognitive_style: CognitiveStyle       # 认知风格
    experience_level: ExperienceLevel     # 经验水平
    current_mood: str                     # 当前心境

    # Principle 部分（动态充分性核心）
    stimulus_preference: StimulusPreference
        - visual_effect: float            # 视觉刺激效果 (0-1)
        - auditory_effect: float          # 听觉刺激效果 (0-1)
        - textual_effect: float           # 文本概念效果 (0-1)
        - sufficiency_threshold: float    # 充分性阈值 (0-1)
    thinking_pace: str                    # 思考节奏

    # Knowledge 部分（当前状态）
    current_position: CreativePosition    # 三维空间位置
        - structure_level: StructureLevel # 结构层次 (L1/L2/L3)
        - creative_stage: CreativeStage   # 创作阶段 (5阶段)
        - progress: float                 # 进度 (0-1)

    stagnation_count: int                 # 卡点计数
    idle_seconds: float                   # 操作停滞时间
```

#### 3.2 三维创作空间导航 (3D Creative Navigation)

创作者的位置可表示为：`(结构层次, 阶段, 进度)`

**示例位置**:
- `(L3, 明确, 0.8)`: 在意图层的明确阶段，完成80%
- `(L2, 发散, 0.3)`: 在隐喻层的发散阶段，完成30%
- `(L1, 整理, 0.9)`: 在故事层的整理阶段，完成90%

#### 3.3 三重触发机制 (Three-Trigger Mechanism)

AI系统应支持三种触发条件来建议结构层次切换：

1. **创作者主动请求**: 直接表达想切换视角
2. **AI卡点检测**: `stagnation_count >= 3`
3. **操作停滞检测**: `idle_seconds >= 120.0`

#### 3.4 动态充分性计算

```python
sufficiency_score = (
    visual_count * visual_effect +
    auditory_count * auditory_effect +
    textual_count * textual_effect
) / 3.0

is_sufficient = sufficiency_score >= sufficiency_threshold
```

**关键原则** (来自WP03):
- 充分性是**关系性的**而非绝对的
- 基于创作者角色动态判断
- 每次引导都是精准的、个性化的

## 五阶段创作流 (Five-Stage Creative Flow)

来自WP02的核心理论，定义了AI辅助创作的过程模型：

### 阶段1: 明确 (Clarification)

**目标**: 明确核心张力与创作意图

**AI支持**:
- 引导性提问
- 张力识别
- 导演参考

**成功标准**: 创作者能明确陈述核心张力

### 阶段2: 聚焦 (Focusing)

**目标**: 将抽象意图聚焦到具体场景/情节

**AI支持**:
- 场景具化
- 作品片段参考
- 三结构对应

**成功标准**: 有初步的场景/故事想法

### 阶段3: 发散 (Divergence)

**目标**: 发散可能性，探索不同表现方式

**AI支持**:
- 多模态激发（动态配比）
- 变奏建议
- 跨导演参考

**成功标准**: 产生3-5个不同方案

### 阶段4: 收束 (Convergence)

**目标**: 从多个方案中选择最优方案

**AI支持**:
- 方案对比
- 充分性检验
- 直觉确认

**成功标准**: 选定核心方案，理由清晰

### 阶段5: 整理 (Organization)

**目标**: 将选定方案整理成完整结构

**AI支持**:
- 结构化建议
- 三结构整合
- 完整性检验

**成功标准**: 有完整创作蓝图

## 数据格式规范

### YAML格式: 导演数据

```yaml
director_id: unique_id
name: 导演名称
name_en: English Name
nationality: 国籍

core_tension:
  left: 张力左侧
  right: 张力右侧
  alpha: 0.5
  description: 张力描述

aesthetic_features:
  visual: [特征列表]
  auditory: [特征列表]

representative_works:
  - title: 作品名称
    year: 年份
    structure_analysis:
      L3_intention: 创作意图
      L2_metaphor: [隐喻列表]
      L1_narrative: 故事叙述

references:
  - 参考文献
```

### YAML格式: 理论数据

```yaml
theory_id: unique_id
name: 理论名称
author: 作者
description: 描述

structures:
  - level: L1/L2/L3
    name: 层次名称
    elements: [元素列表]
    examples: [示例列表]

references:
  - 参考文献
```

## API使用示例

### 1. 加载知识库

```python
from backend.knowledge_base.data_loader import get_knowledge_base_loader

loader = get_knowledge_base_loader()
theory_base = loader.theory_base
work_memory = loader.work_memory
creator_profiles = loader.creator_profiles
```

### 2. 搜索导演张力

```python
# 按导演名称
tension = theory_base.get_director_tension("侯孝贤")
print(f"{tension.tension_pair}: α={tension.alpha}")

# 按张力类型
from backend.knowledge_base.theory_state import TensionType
temporal_directors = theory_base.search_by_tension_type(TensionType.TEMPORAL)
```

### 3. 检索作品片段

```python
# 按张力搜索
fragments = work_memory.search_by_tension(
    tension_left="静止",
    tension_right="流逝",
    balance_range=(0.7, 0.9),
    min_confidence=0.8
)

# 按结构层次搜索
from backend.knowledge_base.work_memory import ThreeStructureLayer
l2_fragments = work_memory.search_by_structure_layer(ThreeStructureLayer.L2)

# 按情感标签搜索
fragments = work_memory.search_by_emotional_tags(["沉静", "哀愁"])
```

### 4. 创建和管理创作者画像

```python
# 创建画像
profile = creator_profiles.create_profile("creator_001")

# 更新位置
from backend.knowledge_base.creator_profile import StructureLevel, CreativeStage
creator_profiles.update_position(
    creator_id="creator_001",
    structure_level=StructureLevel.L2,
    creative_stage=CreativeStage.DIVERGENCE,
    progress=0.3
)

# 记录卡点
should_trigger = creator_profiles.record_stagnation("creator_001")
if should_trigger:
    print("建议切换结构层次")

# 计算充分性
score, is_sufficient = creator_profiles.calculate_stimulus_sufficiency(
    creator_id="creator_001",
    visual_count=3,
    auditory_count=1,
    textual_count=2
)
```

### 5. 获取完整数据

```python
# 获取导演完整信息（包含YAML所有字段）
director_info = loader.get_director_info("侯孝贤")
print(director_info['aesthetic_features'])

# 获取理论完整信息
theory_info = loader.get_theory_info("five_stage_creative_flow")
print(theory_info['stages'])

# 按关键词搜索导演
directors = loader.search_directors_by_tension_keyword("时间")
```

## 慢协商设计哲学 (Slow Negotiation)

来自WP03的核心设计原则：

**核心思想**:
```
效率 = 思想表达充分性 / 迷茫时间
目标：最小化迷茫时间（而非总时间）
```

**区分两种"快"**:
- **思路上的快**: 通过理论引导快速理清思路 ✅
- **操作上的快**: 取消思考时间，快速完成 ❌

**实现策略**:
- 允许创作者长时间探索内心（慢）
- 快速提供参考，减少"不知如何表达"的迷茫（快）
- 鼓励充分探索，不急于收束（慢）
- 快速呈现方案对比，减少"选择困难"（快）

## 扩展建议

### 短期扩展（知识库填充）

1. **更多导演数据**:
   - 大卫·林奇（Lynch）
   - 塔可夫斯基（Tarkovsky）
   - 阿巴斯（Kiarostami）
   - 王家卫
   - 贾樟柯

2. **作品片段库**:
   - 关键场景的多媒体素材
   - 场景分析标注
   - 张力关联标注

3. **理论扩充**:
   - 长镜头美学理论
   - 声音设计理论
   - 蒙太奇理论

### 中期扩展（功能增强）

1. **向量检索**:
   - 使用ChromaDB进行语义检索
   - 多模态embedding（文本+图像）

2. **关联推荐**:
   - 基于张力相似度推荐
   - 基于创作者画像个性化推荐

3. **知识图谱**:
   - 导演-作品-理论关系图
   - 概念关联网络可视化

### 长期扩展（系统集成）

1. **实时创作追踪**:
   - 集成到创作界面
   - 实时更新创作者状态

2. **多人协作**:
   - 支持团队创作
   - 角色分工（导演/编剧/摄影）

3. **生成式扩展**:
   - 基于RAG的剧本生成
   - 场景描述生成

## 参考文献

- Marlin阿杰. Working Paper 01: 马尔可夫电影创作状态理论. 2025.
- Marlin阿杰. Working Paper 02: 认知共振理论与五阶段创作流. 2025.
- Marlin阿杰. Working Paper 03: 动态充分性与三维创作导航系统. 2025.

## 版本历史

- v0.1.0 (2025-10-28): 初始版本
  - 三大核心库架构
  - 基础导演数据（侯孝贤、诺兰）
  - 三结构理论
  - 五阶段创作流理论
  - YAML数据加载器
