"""
知识库查询接口 - FastAPI实现

提供RESTful API用于查询知识库的三大模块：
- 理论状态库查询
- 作品记忆库查询
- 创作者状态库查询
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from backend.knowledge_base.data_loader import get_knowledge_base_loader
from backend.knowledge_base.theory_state import TensionType, ThreeStructureLevel
from backend.knowledge_base.work_memory import MediaType, ThreeStructureLayer
from backend.knowledge_base.creator_profile import (
    CreativeStage,
    StructureLevel,
    CognitiveStyle,
    ExperienceLevel,
    CreatorProfile
)


app = FastAPI(
    title="Film Theory RAG Knowledge Base API",
    description="电影理论RAG知识库查询接口",
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

# 全局加载器
loader = get_knowledge_base_loader()


# ==================== Response Models ====================

class DirectorTensionResponse(BaseModel):
    """导演张力响应模型"""
    director: str
    tension_left: str
    tension_right: str
    tension_type: str
    alpha: float
    description: str
    representative_works: List[str]


class MediaFragmentResponse(BaseModel):
    """媒体片段响应模型"""
    fragment_id: str
    media_type: str
    source_work: str
    director: str
    description: str
    tags: List[str]
    structure_layer: str
    keywords: List[str]
    emotional_tags: List[str]


class CreatorPositionResponse(BaseModel):
    """创作者位置响应模型"""
    structure_level: str
    creative_stage: str
    progress: float


# ==================== Theory State API ====================

@app.get("/")
async def root():
    """API根路径"""
    return {
        "message": "Film Theory RAG Knowledge Base API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/api/v1/directors", response_model=List[str])
async def list_directors():
    """获取所有导演列表"""
    return list(loader.theory_base.director_tensions.keys())


@app.get("/api/v1/directors/{director_name}", response_model=DirectorTensionResponse)
async def get_director_tension(director_name: str):
    """获取导演核心张力"""
    tension = loader.theory_base.get_director_tension(director_name)
    if not tension:
        raise HTTPException(status_code=404, detail=f"Director '{director_name}' not found")

    return DirectorTensionResponse(
        director=tension.director,
        tension_left=tension.tension_pair[0],
        tension_right=tension.tension_pair[1],
        tension_type=tension.tension_type.value,
        alpha=tension.alpha,
        description=tension.description,
        representative_works=tension.representative_works
    )


@app.get("/api/v1/directors/{director_name}/full")
async def get_director_full_info(director_name: str) -> Dict[str, Any]:
    """获取导演完整信息（包含YAML所有字段）"""
    info = loader.get_director_info(director_name)
    if not info:
        raise HTTPException(status_code=404, detail=f"Director '{director_name}' not found")
    return info


@app.get("/api/v1/directors/search/by-tension-type", response_model=List[DirectorTensionResponse])
async def search_directors_by_tension_type(
    tension_type: str = Query(..., description="张力类型: temporal/spatial/emotional/metaphysical/perceptual")
):
    """按张力类型搜索导演"""
    try:
        t_type = TensionType(tension_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tension type: {tension_type}")

    tensions = loader.theory_base.search_by_tension_type(t_type)
    return [
        DirectorTensionResponse(
            director=t.director,
            tension_left=t.tension_pair[0],
            tension_right=t.tension_pair[1],
            tension_type=t.tension_type.value,
            alpha=t.alpha,
            description=t.description,
            representative_works=t.representative_works
        )
        for t in tensions
    ]


@app.get("/api/v1/directors/search/by-keyword", response_model=List[str])
async def search_directors_by_keyword(
    keyword: str = Query(..., description="搜索关键词（在张力描述中搜索）")
):
    """按关键词搜索导演"""
    return loader.search_directors_by_tension_keyword(keyword)


# ==================== Work Memory API ====================

@app.get("/api/v1/works/fragments/search/by-tension", response_model=List[MediaFragmentResponse])
async def search_fragments_by_tension(
    tension_left: str = Query(..., description="张力左侧"),
    tension_right: str = Query(..., description="张力右侧"),
    balance_min: float = Query(0.0, ge=0.0, le=1.0, description="平衡点最小值"),
    balance_max: float = Query(1.0, ge=0.0, le=1.0, description="平衡点最大值"),
    min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="最小置信度")
):
    """按张力搜索作品片段"""
    fragments = loader.work_memory.search_by_tension(
        tension_left=tension_left,
        tension_right=tension_right,
        balance_range=(balance_min, balance_max),
        min_confidence=min_confidence
    )

    return [
        MediaFragmentResponse(
            fragment_id=f.fragment.fragment_id,
            media_type=f.fragment.media_type.value,
            source_work=f.fragment.source_work,
            director=f.fragment.director,
            description=f.fragment.description,
            tags=f.fragment.tags,
            structure_layer=f.structure_layer.value,
            keywords=f.keywords,
            emotional_tags=f.emotional_tags
        )
        for f in fragments
    ]


@app.get("/api/v1/works/fragments/search/by-structure", response_model=List[MediaFragmentResponse])
async def search_fragments_by_structure(
    structure_level: str = Query(..., description="结构层次: 第一结构/第二结构/第三结构")
):
    """按结构层次搜索作品片段"""
    try:
        layer = ThreeStructureLayer(structure_level)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid structure level: {structure_level}")

    fragments = loader.work_memory.search_by_structure_layer(layer)

    return [
        MediaFragmentResponse(
            fragment_id=f.fragment.fragment_id,
            media_type=f.fragment.media_type.value,
            source_work=f.fragment.source_work,
            director=f.fragment.director,
            description=f.fragment.description,
            tags=f.fragment.tags,
            structure_layer=f.structure_layer.value,
            keywords=f.keywords,
            emotional_tags=f.emotional_tags
        )
        for f in fragments
    ]


@app.get("/api/v1/works/fragments/search/by-emotion", response_model=List[MediaFragmentResponse])
async def search_fragments_by_emotion(
    tags: List[str] = Query(..., description="情感标签列表"),
    match_all: bool = Query(False, description="是否匹配所有标签")
):
    """按情感标签搜索作品片段"""
    fragments = loader.work_memory.search_by_emotional_tags(tags, match_all)

    return [
        MediaFragmentResponse(
            fragment_id=f.fragment.fragment_id,
            media_type=f.fragment.media_type.value,
            source_work=f.fragment.source_work,
            director=f.fragment.director,
            description=f.fragment.description,
            tags=f.fragment.tags,
            structure_layer=f.structure_layer.value,
            keywords=f.keywords,
            emotional_tags=f.emotional_tags
        )
        for f in fragments
    ]


@app.get("/api/v1/works/fragments/search/by-director/{director_name}", response_model=List[MediaFragmentResponse])
async def search_fragments_by_director(director_name: str):
    """按导演搜索作品片段"""
    fragments = loader.work_memory.search_by_director(director_name)

    return [
        MediaFragmentResponse(
            fragment_id=f.fragment.fragment_id,
            media_type=f.fragment.media_type.value,
            source_work=f.fragment.source_work,
            director=f.fragment.director,
            description=f.fragment.description,
            tags=f.fragment.tags,
            structure_layer=f.structure_layer.value,
            keywords=f.keywords,
            emotional_tags=f.emotional_tags
        )
        for f in fragments
    ]


# ==================== Creator Profile API ====================

@app.post("/api/v1/creators", response_model=Dict[str, str])
async def create_creator_profile(creator_id: str = Query(..., description="创作者ID")):
    """创建新的创作者画像"""
    profile = loader.creator_profiles.create_profile(creator_id)
    return {
        "creator_id": profile.creator_id,
        "message": "Creator profile created successfully"
    }


@app.get("/api/v1/creators/{creator_id}", response_model=Dict[str, Any])
async def get_creator_profile(creator_id: str):
    """获取创作者画像"""
    profile = loader.creator_profiles.get_profile(creator_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Creator '{creator_id}' not found")

    return profile.model_dump()


@app.get("/api/v1/creators/{creator_id}/position", response_model=CreatorPositionResponse)
async def get_creator_position(creator_id: str):
    """获取创作者当前位置"""
    profile = loader.creator_profiles.get_profile(creator_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Creator '{creator_id}' not found")

    pos = profile.current_position
    return CreatorPositionResponse(
        structure_level=pos.structure_level.value,
        creative_stage=pos.creative_stage.value,
        progress=pos.progress
    )


@app.put("/api/v1/creators/{creator_id}/position")
async def update_creator_position(
    creator_id: str,
    structure_level: Optional[str] = Query(None, description="结构层次"),
    creative_stage: Optional[str] = Query(None, description="创作阶段"),
    progress: Optional[float] = Query(None, ge=0.0, le=1.0, description="进度")
):
    """更新创作者位置"""
    profile = loader.creator_profiles.get_profile(creator_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Creator '{creator_id}' not found")

    s_level = StructureLevel(structure_level) if structure_level else None
    c_stage = CreativeStage(creative_stage) if creative_stage else None

    loader.creator_profiles.update_position(
        creator_id=creator_id,
        structure_level=s_level,
        creative_stage=c_stage,
        progress=progress
    )

    return {"message": "Position updated successfully"}


@app.post("/api/v1/creators/{creator_id}/stagnation")
async def record_stagnation(creator_id: str):
    """记录卡点事件"""
    should_trigger = loader.creator_profiles.record_stagnation(creator_id)
    return {
        "creator_id": creator_id,
        "should_trigger_structure_switch": should_trigger,
        "message": "切换结构层次" if should_trigger else "继续当前层次"
    }


@app.put("/api/v1/creators/{creator_id}/idle")
async def update_idle_time(
    creator_id: str,
    seconds: float = Query(..., description="停滞秒数")
):
    """更新操作停滞时间"""
    should_trigger = loader.creator_profiles.update_idle_time(creator_id, seconds)
    return {
        "creator_id": creator_id,
        "idle_seconds": seconds,
        "should_trigger_check": should_trigger,
        "message": "建议主动询问" if should_trigger else "继续观察"
    }


@app.post("/api/v1/creators/{creator_id}/sufficiency")
async def calculate_sufficiency(
    creator_id: str,
    visual_count: int = Query(..., description="视觉激发数量"),
    auditory_count: int = Query(..., description="听觉激发数量"),
    textual_count: int = Query(..., description="文本激发数量")
):
    """计算激发充分性"""
    score, is_sufficient = loader.creator_profiles.calculate_stimulus_sufficiency(
        creator_id=creator_id,
        visual_count=visual_count,
        auditory_count=auditory_count,
        textual_count=textual_count
    )

    return {
        "creator_id": creator_id,
        "sufficiency_score": round(score, 2),
        "is_sufficient": is_sufficient,
        "message": "激发已充分" if is_sufficient else "建议增加激发"
    }


# ==================== Theory API ====================

@app.get("/api/v1/theories/{theory_id}")
async def get_theory_info(theory_id: str) -> Dict[str, Any]:
    """获取理论完整信息"""
    info = loader.get_theory_info(theory_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Theory '{theory_id}' not found")
    return info


@app.get("/api/v1/theories")
async def list_theories() -> List[str]:
    """获取所有理论列表"""
    return [
        "三结构理论",
        "五阶段创作流"
    ]


# ==================== Utility API ====================

@app.post("/api/v1/reload")
async def reload_knowledge_base():
    """重新加载知识库"""
    global loader
    from backend.knowledge_base.data_loader import reload_knowledge_base
    loader = reload_knowledge_base()
    return {"message": "Knowledge base reloaded successfully"}


@app.get("/api/v1/stats")
async def get_knowledge_base_stats():
    """获取知识库统计信息"""
    return {
        "directors_count": len(loader.theory_base.director_tensions),
        "concepts_count": len(loader.theory_base.theoretical_concepts),
        "work_fragments_count": len(loader.work_memory.work_fragments),
        "creator_profiles_count": len(loader.creator_profiles.creator_profiles)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
