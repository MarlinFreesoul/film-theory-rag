"""
知识库API测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_directors_api():
    """测试导演API"""
    print_section("测试导演API")

    # 1. 获取所有导演
    print("\n1. 获取所有导演列表:")
    response = requests.get(f"{BASE_URL}/api/v1/directors")
    directors = response.json()
    print(f"   导演列表: {directors}")

    # 2. 获取侯孝贤的核心张力
    print("\n2. 获取侯孝贤的核心张力:")
    response = requests.get(f"{BASE_URL}/api/v1/directors/侯孝贤")
    director = response.json()
    print(f"   导演: {director['director']}")
    print(f"   核心张力: {director['tension_left']} ↔ {director['tension_right']}")
    print(f"   α值: {director['alpha']}")
    print(f"   类型: {director['tension_type']}")

    # 3. 按张力类型搜索
    print("\n3. 搜索时间性张力的导演:")
    response = requests.get(
        f"{BASE_URL}/api/v1/directors/search/by-tension-type",
        params={"tension_type": "temporal"}
    )
    temporal_directors = response.json()
    print(f"   找到 {len(temporal_directors)} 位导演")
    for d in temporal_directors:
        print(f"   - {d['director']}: {d['tension_left']} ↔ {d['tension_right']}")

    # 4. 按关键词搜索
    print("\n4. 搜索包含'时间'关键词的导演:")
    response = requests.get(
        f"{BASE_URL}/api/v1/directors/search/by-keyword",
        params={"keyword": "时间"}
    )
    keyword_directors = response.json()
    print(f"   找到导演: {keyword_directors}")


def test_creator_profile_api():
    """测试创作者画像API"""
    print_section("测试创作者画像API")

    creator_id = "test_creator_001"

    # 1. 创建创作者画像
    print(f"\n1. 创建创作者画像 (ID: {creator_id}):")
    response = requests.post(
        f"{BASE_URL}/api/v1/creators",
        params={"creator_id": creator_id}
    )
    print(f"   {response.json()['message']}")

    # 2. 获取创作者画像
    print(f"\n2. 获取创作者画像:")
    response = requests.get(f"{BASE_URL}/api/v1/creators/{creator_id}")
    profile = response.json()
    print(f"   创作者ID: {profile['creator_id']}")
    print(f"   认知风格: {profile['cognitive_style']}")
    print(f"   经验水平: {profile['experience_level']}")

    # 3. 更新创作位置
    print(f"\n3. 更新创作位置到 (L3, 明确, 0.5):")
    response = requests.put(
        f"{BASE_URL}/api/v1/creators/{creator_id}/position",
        params={
            "structure_level": "第三结构",
            "creative_stage": "明确",
            "progress": 0.5
        }
    )
    print(f"   {response.json()['message']}")

    # 4. 获取当前位置
    print(f"\n4. 获取当前位置:")
    response = requests.get(f"{BASE_URL}/api/v1/creators/{creator_id}/position")
    position = response.json()
    print(f"   位置: ({position['structure_level']}, {position['creative_stage']}, {position['progress']})")

    # 5. 记录卡点（3次）
    print(f"\n5. 测试三重触发机制 - 卡点检测:")
    for i in range(1, 4):
        response = requests.post(f"{BASE_URL}/api/v1/creators/{creator_id}/stagnation")
        result = response.json()
        print(f"   第{i}次卡点: {result['message']}")
        if result['should_trigger_structure_switch']:
            print(f"   ✓ 触发结构切换建议！")

    # 6. 测试操作停滞检测
    print(f"\n6. 测试三重触发机制 - 操作停滞检测:")
    response = requests.put(
        f"{BASE_URL}/api/v1/creators/{creator_id}/idle",
        params={"seconds": 150.0}
    )
    result = response.json()
    print(f"   停滞时间: {result['idle_seconds']}秒")
    print(f"   {result['message']}")
    if result['should_trigger_check']:
        print(f"   ✓ 触发主动询问！")

    # 7. 计算充分性
    print(f"\n7. 测试动态充分性计算:")
    response = requests.post(
        f"{BASE_URL}/api/v1/creators/{creator_id}/sufficiency",
        params={
            "visual_count": 3,
            "auditory_count": 1,
            "textual_count": 2
        }
    )
    result = response.json()
    print(f"   激发组合: 视觉×3 + 听觉×1 + 文本×2")
    print(f"   充分性得分: {result['sufficiency_score']}")
    print(f"   是否充分: {'是' if result['is_sufficient'] else '否'}")
    print(f"   建议: {result['message']}")


def test_work_memory_api():
    """测试作品记忆库API"""
    print_section("测试作品记忆库API")

    # 1. 按张力搜索片段
    print("\n1. 搜索'静止↔流逝'张力的片段:")
    response = requests.get(
        f"{BASE_URL}/api/v1/works/fragments/search/by-tension",
        params={
            "tension_left": "静止",
            "tension_right": "流逝",
            "balance_min": 0.7,
            "balance_max": 0.9,
            "min_confidence": 0.8
        }
    )
    fragments = response.json()
    print(f"   找到 {len(fragments)} 个片段")
    for f in fragments:
        print(f"   - {f['source_work']} ({f['director']}): {f['description']}")

    # 2. 按结构层次搜索
    print("\n2. 搜索第二结构（隐喻层）的片段:")
    response = requests.get(
        f"{BASE_URL}/api/v1/works/fragments/search/by-structure",
        params={"structure_level": "第二结构"}
    )
    fragments = response.json()
    print(f"   找到 {len(fragments)} 个片段")

    # 3. 按情感标签搜索
    print("\n3. 搜索带有'沉静'或'哀愁'标签的片段:")
    response = requests.get(
        f"{BASE_URL}/api/v1/works/fragments/search/by-emotion",
        params={"tags": ["沉静", "哀愁"], "match_all": False}
    )
    fragments = response.json()
    print(f"   找到 {len(fragments)} 个片段")
    for f in fragments:
        print(f"   - {f['source_work']}: 标签={f['emotional_tags']}")


def test_theory_api():
    """测试理论API"""
    print_section("测试理论API")

    # 1. 获取所有理论
    print("\n1. 获取所有理论列表:")
    response = requests.get(f"{BASE_URL}/api/v1/theories")
    theories = response.json()
    print(f"   理论列表: {theories}")

    # 2. 获取五阶段创作流理论
    print("\n2. 获取五阶段创作流理论详情:")
    response = requests.get(f"{BASE_URL}/api/v1/theories/五阶段创作流")
    theory = response.json()
    print(f"   理论名称: {theory['name']}")
    print(f"   作者: {theory['author']}")
    print(f"   阶段数量: {len(theory['stages'])}")
    for stage in theory['stages']:
        print(f"   - {stage['name']} ({stage['name_en']}): {stage['goal']}")


def test_utility_api():
    """测试工具API"""
    print_section("测试工具API")

    # 1. 获取统计信息
    print("\n1. 获取知识库统计信息:")
    response = requests.get(f"{BASE_URL}/api/v1/stats")
    stats = response.json()
    print(f"   导演数量: {stats['directors_count']}")
    print(f"   概念数量: {stats['concepts_count']}")
    print(f"   作品片段数量: {stats['work_fragments_count']}")
    print(f"   创作者画像数量: {stats['creator_profiles_count']}")

    # 2. 重新加载知识库
    print("\n2. 重新加载知识库:")
    response = requests.post(f"{BASE_URL}/api/v1/reload")
    print(f"   {response.json()['message']}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  电影理论RAG知识库API测试")
    print("  确保API服务已启动: python backend/api/query_interface.py")
    print("=" * 60)

    try:
        # 测试连接
        response = requests.get(BASE_URL)
        print(f"\n✓ API服务连接成功 (版本: {response.json()['version']})")

        # 运行测试
        test_directors_api()
        test_theory_api()
        test_work_memory_api()
        test_creator_profile_api()
        test_utility_api()

        print("\n" + "=" * 60)
        print("  ✓ 所有测试完成！")
        print("=" * 60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n✗ 无法连接到API服务")
        print("  请先启动服务: python backend/api/query_interface.py")
        print()


if __name__ == "__main__":
    main()
