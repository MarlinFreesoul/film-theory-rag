# 知识库查询API

基于FastAPI构建的RESTful API，提供电影理论RAG知识库的完整查询接口。

## 快速开始

### 1. 安装依赖

```bash
cd /c/Users/MARLIN/film-theory-rag
pip install -r requirements.txt
```

### 2. 启动服务

```bash
python backend/api/query_interface.py
```

服务将在 `http://localhost:8000` 启动

### 3. 查看文档

访问 `http://localhost:8000/docs` 查看交互式API文档（Swagger UI）

## API端点概览

### Theory State API (理论状态库)

#### 导演相关

- `GET /api/v1/directors` - 获取所有导演列表
- `GET /api/v1/directors/{director_name}` - 获取导演核心张力
- `GET /api/v1/directors/{director_name}/full` - 获取导演完整信息
- `GET /api/v1/directors/search/by-tension-type` - 按张力类型搜索导演
- `GET /api/v1/directors/search/by-keyword` - 按关键词搜索导演

#### 理论相关

- `GET /api/v1/theories` - 获取所有理论列表
- `GET /api/v1/theories/{theory_id}` - 获取理论完整信息

### Work Memory API (作品记忆库)

#### 作品片段搜索

- `GET /api/v1/works/fragments/search/by-tension` - 按张力搜索作品片段
- `GET /api/v1/works/fragments/search/by-structure` - 按结构层次搜索
- `GET /api/v1/works/fragments/search/by-emotion` - 按情感标签搜索
- `GET /api/v1/works/fragments/search/by-director/{director_name}` - 按导演搜索

### Creator Profile API (创作者状态库)

#### 创作者管理

- `POST /api/v1/creators` - 创建新的创作者画像
- `GET /api/v1/creators/{creator_id}` - 获取创作者画像
- `GET /api/v1/creators/{creator_id}/position` - 获取创作者当前位置
- `PUT /api/v1/creators/{creator_id}/position` - 更新创作者位置

#### 创作状态追踪

- `POST /api/v1/creators/{creator_id}/stagnation` - 记录卡点事件
- `PUT /api/v1/creators/{creator_id}/idle` - 更新操作停滞时间
- `POST /api/v1/creators/{creator_id}/sufficiency` - 计算激发充分性

### Utility API (工具接口)

- `POST /api/v1/reload` - 重新加载知识库
- `GET /api/v1/stats` - 获取知识库统计信息

## 使用示例

### 1. 获取导演核心张力

```bash
curl http://localhost:8000/api/v1/directors/侯孝贤
```

响应：
```json
{
  "director": "侯孝贤",
  "tension_left": "静止",
  "tension_right": "流逝",
  "tension_type": "temporal",
  "alpha": 0.8,
  "description": "时间的双重性：静止的凝视与不可逆的流逝...",
  "representative_works": ["悲情城市", "最好的时光", "刺客聂隐娘"]
}
```

### 2. 按张力类型搜索导演

```bash
curl "http://localhost:8000/api/v1/directors/search/by-tension-type?tension_type=temporal"
```

### 3. 创建创作者画像

```bash
curl -X POST "http://localhost:8000/api/v1/creators?creator_id=creator_001"
```

### 4. 更新创作者位置

```bash
curl -X PUT "http://localhost:8000/api/v1/creators/creator_001/position?structure_level=第二结构&creative_stage=发散&progress=0.3"
```

### 5. 计算激发充分性

```bash
curl -X POST "http://localhost:8000/api/v1/creators/creator_001/sufficiency?visual_count=3&auditory_count=1&textual_count=2"
```

响应：
```json
{
  "creator_id": "creator_001",
  "sufficiency_score": 0.73,
  "is_sufficient": false,
  "message": "建议增加激发"
}
```

### 6. 按张力搜索作品片段

```bash
curl "http://localhost:8000/api/v1/works/fragments/search/by-tension?tension_left=静止&tension_right=流逝&balance_min=0.7&balance_max=0.9&min_confidence=0.8"
```

### 7. 记录卡点事件

```bash
curl -X POST "http://localhost:8000/api/v1/creators/creator_001/stagnation"
```

响应：
```json
{
  "creator_id": "creator_001",
  "should_trigger_structure_switch": false,
  "message": "继续当前层次"
}
```

### 8. 获取知识库统计

```bash
curl http://localhost:8000/api/v1/stats
```

响应：
```json
{
  "directors_count": 3,
  "concepts_count": 2,
  "work_fragments_count": 1,
  "creator_profiles_count": 0
}
```

## Python客户端示例

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 获取导演信息
response = requests.get(f"{BASE_URL}/api/v1/directors/侯孝贤")
director = response.json()
print(f"{director['director']}: {director['tension_left']} ↔ {director['tension_right']}")

# 2. 创建创作者
requests.post(f"{BASE_URL}/api/v1/creators?creator_id=creator_001")

# 3. 更新位置
requests.put(
    f"{BASE_URL}/api/v1/creators/creator_001/position",
    params={
        "structure_level": "第三结构",
        "creative_stage": "明确",
        "progress": 0.5
    }
)

# 4. 获取创作者位置
response = requests.get(f"{BASE_URL}/api/v1/creators/creator_001/position")
position = response.json()
print(f"当前位置: ({position['structure_level']}, {position['creative_stage']}, {position['progress']})")

# 5. 计算充分性
response = requests.post(
    f"{BASE_URL}/api/v1/creators/creator_001/sufficiency",
    params={"visual_count": 3, "auditory_count": 1, "textual_count": 2}
)
result = response.json()
print(f"充分性得分: {result['sufficiency_score']}, 是否充分: {result['is_sufficient']}")
```

## 核心概念

### 张力类型 (Tension Type)

- `temporal`: 时间性张力（如 静止↔流逝）
- `spatial`: 空间性张力（如 封闭↔开放）
- `emotional`: 情感性张力（如 连接↔孤独）
- `metaphysical`: 形而上张力（如 秩序↔熵增）
- `perceptual`: 感知性张力（如 表层↔潜意识）

### 结构层次 (Structure Level)

- `第三结构` (L3): 创作意图层
- `第二结构` (L2): 隐喻象征层
- `第一结构` (L1): 故事剧情层

### 创作阶段 (Creative Stage)

- `明确`: 明确核心张力与创作意图
- `聚焦`: 将抽象意图聚焦到具体场景
- `发散`: 发散可能性，探索不同表现方式
- `收束`: 从多个方案中选择最优方案
- `整理`: 将选定方案整理成完整结构

### 三维创作空间位置

位置表示为：`(结构层次, 创作阶段, 进度)`

示例：
- `(第三结构, 明确, 0.8)`: 在意图层的明确阶段，完成80%
- `(第二结构, 发散, 0.3)`: 在隐喻层的发散阶段，完成30%

## 三重触发机制

系统支持三种触发条件来建议结构层次切换：

1. **创作者主动请求**: 直接调用切换API
2. **AI卡点检测**: `stagnation_count >= 3` 时，`record_stagnation` 返回 `should_trigger_structure_switch: true`
3. **操作停滞检测**: `idle_seconds >= 120.0` 时，`update_idle_time` 返回 `should_trigger_check: true`

## 动态充分性计算

充分性得分计算公式：

```
score = (visual_count * visual_effect +
         auditory_count * auditory_effect +
         textual_count * textual_effect) / 3.0

is_sufficient = score >= sufficiency_threshold
```

其中 `visual_effect`, `auditory_effect`, `textual_effect` 和 `sufficiency_threshold` 来自创作者画像的 `stimulus_preference`。

## 错误处理

API使用标准HTTP状态码：

- `200 OK`: 请求成功
- `400 Bad Request`: 参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## 开发计划

### v0.2.0 (计划中)

- [ ] 向量检索接口（基于ChromaDB）
- [ ] 批量查询接口
- [ ] WebSocket支持（实时创作追踪）
- [ ] 多媒体片段上传接口

### v0.3.0 (计划中)

- [ ] 认证与授权
- [ ] 创作历史记录
- [ ] 推荐算法接口
- [ ] 数据导出接口

## 参考文档

- [知识库文档](../../docs/KNOWLEDGE_BASE.md)
- [三篇工作论文](../../research/papers/)
- [FastAPI文档](https://fastapi.tiangolo.com/)
