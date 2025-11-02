"""
Film Theory RAG - API Gateway

FastAPI应用入口
提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import time
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.event_bus import EventBus
from core.state_tracker import StateTracker
from core.session_manager import SessionManager
from core.llm_keyword_extractor import LLMKeywordExtractor
from core.usage_tracker import get_tracker
from core.visualization_generator import VisualizationGenerator, VisualScene
from core.progressive_controller import get_progressive_controller
from modules.theory_module import TheoryModule
from modules.work_module import WorkModule

# ========== FastAPI App ==========

app = FastAPI(
    title="Film Theory RAG API",
    description="基于RAG的电影理论激发系统",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 初始化系统 ==========

# 创建事件总线
event_bus = EventBus()

# 创建会话管理器
session_manager = SessionManager()

# 创建LLM关键词提取器（使用环境变量中的API key）
llm_extractor = LLMKeywordExtractor()

# 创建状态追踪器（注入LLM提取器）
state_tracker = StateTracker(event_bus, llm_extractor=llm_extractor)

# 获取知识库路径
kb_path = Path(__file__).parent.parent.parent / 'knowledge-base'

# 初始化知识模块
theory_module = TheoryModule(
    event_bus,
    yaml_path=str(kb_path / 'theory_database.yaml')
)

work_module = WorkModule(
    event_bus,
    yaml_path=str(kb_path / 'work_database.yaml')
)

# 创建视觉化生成器
visualization_generator = VisualizationGenerator()

print("[API] System initialized successfully")

# ========== API Models ==========

class InspireRequest(BaseModel):
    """激发请求"""
    user_input: str
    session_id: Optional[str] = None  # 会话ID（可选，不传则创建新会话）
    context: Optional[Dict[str, Any]] = None


class StateInfo(BaseModel):
    """状态信息"""
    stage: str
    keywords: List[str]
    structure_dimension: str
    progress: float


class InspirationItem(BaseModel):
    """激发内容项"""
    type: str
    title: str
    content: str
    relevance_score: float
    source: str
    metadata: Optional[Dict[str, Any]] = None


class GuidingQuestionItem(BaseModel):
    """引导性问题"""
    question: str
    purpose: str  # 问题目的


class VisualSceneItem(BaseModel):
    """视觉化场景"""
    title: str  # 场景标题
    visual: str  # 画面描述
    sound: str  # 声音描述
    duration: str  # 持续时间
    purpose: str  # 激发目的
    tension: str  # 对应张力


class InspireResponse(BaseModel):
    """激发响应"""
    session_id: str  # 会话ID
    turn_number: int  # 当前是第几轮
    state: StateInfo
    inspirations: List[InspirationItem]
    total_count: int
    guiding_questions: List[GuidingQuestionItem] = []  # 系统引导问题（新增）
    visual_scenes: List[VisualSceneItem] = []  # 视觉化场景（新增）


# ========== API Endpoints ==========

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Film Theory RAG API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    stats = event_bus.get_stats()
    return {
        "status": "ok",
        "event_bus_stats": stats,
        "modules": ["StateTracker", "TheoryModule", "WorkModule"]
    }


@app.post("/inspire", response_model=InspireResponse)
async def get_inspiration(request: InspireRequest):
    """
    获取激发内容（支持多轮对话）

    基于用户输入，识别创作状态，返回相关的理论和作品激发
    """
    try:
        # 1. 获取或创建会话
        session_id = request.session_id
        if not session_id or not session_manager.get_session(session_id):
            session_id = session_manager.create_session()
            print(f"[API] Created new session: {session_id}")

        # 2. 获取上下文关键词和轮数
        context_keywords = session_manager.get_context_keywords(session_id)
        is_first_turn = session_manager.is_first_turn(session_id)
        turn_number = len(session_manager.get_session(session_id).turns) + 1

        print(f"[API] Session {session_id}, Turn {turn_number}")
        print(f"[API] Context keywords: {context_keywords}")

        # 3. 分析状态（融合上下文 + 五阶段检测）
        state = state_tracker.analyze_input(request.user_input, context_keywords, turn_number)

        # 4. 等待模块响应（简单实现：短暂延迟让事件传播）
        time.sleep(0.3)

        # 5. 收集激发内容
        inspiration_events = event_bus.get_history('inspiration_found', limit=20)

        # 合并所有激发内容
        all_inspirations = []
        for event in inspiration_events:
            for insp_dict in event.data.get('inspirations', []):
                all_inspirations.append(InspirationItem(**insp_dict))

        # 去重并按相关度排序
        seen = set()
        unique_inspirations = []
        for insp in all_inspirations:
            key = (insp.type, insp.title)
            if key not in seen:
                seen.add(key)
                unique_inspirations.append(insp)

        unique_inspirations.sort(key=lambda x: x.relevance_score, reverse=True)

        # 6. 记录本轮对话
        session_manager.add_turn(
            session_id=session_id,
            user_input=request.user_input,
            keywords=state.keywords,
            stage=state.stage.value,
            inspirations_count=len(unique_inspirations)
        )

        session = session_manager.get_session(session_id)
        turn_number = len(session.turns)

        # 7. 【智能体核心】使用渐进式控制器决定返回什么内容
        controller = get_progressive_controller()
        content_plan = controller.plan_content(
            turn_number=turn_number,
            stage=state.stage.value,
            user_input=request.user_input,
            conversation_history=[]  # 暂时传空,后续可以优化
        )

        print(f"[ProgressiveController] {content_plan.reason}")

        # 8. 根据内容计划准备响应数据
        response_inspirations = []
        response_scenes = []

        # 8.1 理论灵感 (如果计划要求)
        if content_plan.return_theory:
            theory_items = [insp for insp in unique_inspirations if insp.type == 'theory']
            response_inspirations.extend(theory_items[:content_plan.theory_limit])
            print(f"[ProgressiveController] 返回 {len(theory_items[:content_plan.theory_limit])} 个理论")

        # 8.2 作品参考 (如果计划要求)
        if content_plan.return_works:
            work_items = [insp for insp in unique_inspirations if insp.type == 'work']
            response_inspirations.extend(work_items[:content_plan.works_limit])
            print(f"[ProgressiveController] 返回 {len(work_items[:content_plan.works_limit])} 个作品")

        # 8.3 视觉场景 (如果计划要求)
        if content_plan.return_scenes:
            # 生成场景
            visual_scenes = visualization_generator.generate_visual_scenes(
                user_input=request.user_input,
                keywords=state.keywords,
                stage=state.stage.value,
                inspirations=[insp.dict() for insp in unique_inspirations[:3]]
            )

            # 根据计划返回指定数量的场景
            if content_plan.scenes_limit == 1:
                # 逐个返回场景模式
                if content_plan.scene_index < len(visual_scenes):
                    selected_scenes = [visual_scenes[content_plan.scene_index]]
                else:
                    selected_scenes = []
            else:
                # 返回多个场景
                selected_scenes = visual_scenes[:content_plan.scenes_limit]

            response_scenes = [
                VisualSceneItem(
                    title=scene.title,
                    visual=scene.visual,
                    sound=scene.sound,
                    duration=scene.duration,
                    purpose=scene.purpose,
                    tension=scene.tension
                )
                for scene in selected_scenes
            ]
            print(f"[ProgressiveController] 返回 {len(response_scenes)} 个场景")

        # 9. 生成引导性问题（始终生成）
        guiding_questions = state_tracker.generate_guiding_questions(turn_number)
        guiding_questions_items = [
            GuidingQuestionItem(
                question=q.question,
                purpose=q.purpose
            )
            for q in guiding_questions
        ]

        # 10. 构造响应
        return InspireResponse(
            session_id=session_id,
            turn_number=turn_number,
            state=StateInfo(
                stage=state.stage.value,
                keywords=state.keywords if content_plan.return_keywords else [],  # 按计划返回
                structure_dimension=state.structure_dimension,
                progress=state.progress
            ),
            inspirations=response_inspirations,  # 渐进式返回
            total_count=len(unique_inspirations),
            guiding_questions=guiding_questions_items,  # 系统引导问题
            visual_scenes=response_scenes  # 渐进式返回场景
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/event_history")
async def get_event_history(event_type: Optional[str] = None, limit: int = 10):
    """获取事件历史（调试用）"""
    events = event_bus.get_history(event_type, limit)

    return {
        "events": [
            {
                "id": e.id,
                "type": e.type,
                "source": e.source,
                "timestamp": e.timestamp.isoformat(),
                "data": e.data
            }
            for e in events
        ]
    }


@app.get("/usage")
async def get_usage_stats():
    """获取LLM用量统计"""
    tracker = get_tracker()
    return tracker.get_stats()


@app.get("/usage/cost")
async def get_cost_breakdown():
    """获取成本明细"""
    tracker = get_tracker()
    return tracker.get_cost_breakdown()


@app.post("/usage/reset")
async def reset_usage():
    """重置用量统计"""
    tracker = get_tracker()
    tracker.reset()
    return {"message": "Usage stats reset successfully"}


# ========== 启动 ==========

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
