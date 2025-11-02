"""
简单测试脚本 - 验证系统是否正常工作
"""

import sys
import os
from pathlib import Path

# 设置Windows控制台编码为UTF-8
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8')

# 添加backend到路径
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from core.event_bus import EventBus
from core.state_tracker import StateTracker
from modules.theory_module import TheoryModule
from modules.work_module import WorkModule

def main():
    print("="*60)
    print("Film Theory RAG - System Test")
    print("="*60)

    # 1. 创建事件总线
    print("\n[1] Creating Event Bus...")
    event_bus = EventBus()
    print("✓ Event Bus created")

    # 2. 创建状态追踪器
    print("\n[2] Creating State Tracker...")
    state_tracker = StateTracker(event_bus)
    print("✓ State Tracker created")

    # 3. 创建知识模块
    print("\n[3] Loading Knowledge Modules...")
    kb_path = Path(__file__).parent / 'knowledge-base'

    theory_module = TheoryModule(
        event_bus,
        yaml_path=str(kb_path / 'theory_database.yaml')
    )

    work_module = WorkModule(
        event_bus,
        yaml_path=str(kb_path / 'work_database.yaml')
    )
    print("✓ Knowledge Modules loaded")

    # 4. 测试用户输入
    print("\n[4] Testing User Input...")
    print("-"*60)

    user_input = "我在构思一个关于记忆消逝的场景"
    print(f"User Input: {user_input}")
    print("-"*60)

    # 分析状态
    state = state_tracker.analyze_input(user_input)

    print(f"\n✓ State Identified:")
    print(f"  - Stage: {state.stage.value}")
    print(f"  - Keywords: {', '.join(state.keywords)}")
    print(f"  - Structure: {state.structure_dimension}")
    print(f"  - Progress: {state.progress * 100:.0f}%")

    # 等待模块响应
    import time
    time.sleep(0.5)

    # 获取激发内容
    inspiration_events = event_bus.get_history('inspiration_found', limit=10)

    print(f"\n✓ Inspirations Found: {len(inspiration_events)} modules responded")

    for event in inspiration_events:
        module = event.data.get('module')
        inspirations = event.data.get('inspirations', [])

        print(f"\n  From {module}:")
        for insp in inspirations:
            print(f"    • {insp['title']}")
            print(f"      Relevance: {insp['relevance_score']:.2f}")
            print(f"      {insp['content'][:100]}...")

    print("\n" + "="*60)
    print("✓ Test Completed Successfully!")
    print("="*60)

if __name__ == "__main__":
    main()
