"""
知识库数据加载器
从YAML文件加载理论、导演、作品数据到内存结构
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
from .theory_state import (
    TheoryStateBase,
    DirectorTension,
    TensionType,
    TheoreticalConcept,
    ThreeStructureLevel
)
from .work_memory import (
    WorkMemoryBase,
    MediaFragment,
    WorkFragment,
    MediaType,
    ThreeStructureLayer,
    TensionAssociation
)
from .creator_profile import CreatorProfileBase


class KnowledgeBaseLoader:
    """知识库数据加载器"""

    def __init__(self, data_root: str = "/c/Users/MARLIN/film-theory-rag/data"):
        self.data_root = Path(data_root)
        self.theory_base = TheoryStateBase()
        self.work_memory = WorkMemoryBase()
        self.creator_profiles = CreatorProfileBase()

    def load_all(self) -> tuple[TheoryStateBase, WorkMemoryBase, CreatorProfileBase]:
        """加载所有知识库数据"""
        self.load_directors()
        self.load_theories()
        # load_works 待实现（需要实际媒体文件）
        return self.theory_base, self.work_memory, self.creator_profiles

    def load_directors(self) -> None:
        """从YAML文件加载导演数据"""
        director_dir = self.data_root / "directors"
        if not director_dir.exists():
            return

        for yaml_file in director_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # 解析核心张力
            tension_data = data.get('core_tension', {})

            # 映射张力类型
            tension_type_map = {
                '时间': TensionType.TEMPORAL,
                '空间': TensionType.SPATIAL,
                '情感': TensionType.EMOTIONAL,
                '形而上': TensionType.METAPHYSICAL,
                '感知': TensionType.PERCEPTUAL
            }

            # 根据描述推断张力类型
            description = tension_data.get('description', '')
            tension_type = TensionType.METAPHYSICAL  # 默认
            if '时间' in description or '流逝' in description:
                tension_type = TensionType.TEMPORAL
            elif '空间' in description:
                tension_type = TensionType.SPATIAL
            elif '情感' in description or '情绪' in description:
                tension_type = TensionType.EMOTIONAL
            elif '感知' in description or '意识' in description:
                tension_type = TensionType.PERCEPTUAL

            # 构建DirectorTension对象
            director_tension = DirectorTension(
                director=data['name'],
                tension_pair=(tension_data['left'], tension_data['right']),
                tension_type=tension_type,
                alpha=tension_data['alpha'],
                description=tension_data['description'],
                representative_works=[
                    work['title'] for work in data.get('representative_works', [])
                ]
            )

            self.theory_base.add_director_tension(director_tension)

    def load_theories(self) -> None:
        """从YAML文件加载理论数据"""
        theory_dir = self.data_root / "theories"
        if not theory_dir.exists():
            return

        for yaml_file in theory_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # 理论数据加载到concept库
            # 这里简化处理，实际可以更复杂
            theory_concept = TheoreticalConcept(
                concept_id=data.get('theory_id', yaml_file.stem),
                name=data.get('name', ''),
                structure_level=ThreeStructureLevel.L3,  # 理论本身在意图层
                definition=data.get('description', ''),
                keywords=data.get('style_tags', []) if 'style_tags' in data else [],
                related_concepts=[],
                examples=[]
            )

            self.theory_base.add_concept(theory_concept)

    def get_director_info(self, director_name: str) -> Optional[Dict]:
        """获取导演完整信息（包含YAML原始数据）"""
        director_dir = self.data_root / "directors"
        yaml_files = list(director_dir.glob("*.yaml"))

        for yaml_file in yaml_files:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data.get('name') == director_name or data.get('name_zh') == director_name:
                    return data
        return None

    def get_theory_info(self, theory_id: str) -> Optional[Dict]:
        """获取理论完整信息"""
        theory_dir = self.data_root / "theories"
        yaml_file = theory_dir / f"{theory_id}.yaml"

        if yaml_file.exists():
            with open(yaml_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return None

    def search_directors_by_tension_keyword(self, keyword: str) -> List[str]:
        """按张力关键词搜索导演"""
        director_dir = self.data_root / "directors"
        results = []

        for yaml_file in director_dir.glob("*.yaml"):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                tension = data.get('core_tension', {})
                if (keyword in tension.get('left', '') or
                    keyword in tension.get('right', '') or
                    keyword in tension.get('description', '')):
                    results.append(data['name'])

        return results


# 全局实例（单例模式）
_loader_instance: Optional[KnowledgeBaseLoader] = None


def get_knowledge_base_loader() -> KnowledgeBaseLoader:
    """获取知识库加载器单例"""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = KnowledgeBaseLoader()
        _loader_instance.load_all()
    return _loader_instance


def reload_knowledge_base() -> KnowledgeBaseLoader:
    """重新加载知识库"""
    global _loader_instance
    _loader_instance = KnowledgeBaseLoader()
    _loader_instance.load_all()
    return _loader_instance
