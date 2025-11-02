"""测试渐进式智能体 - 验证它不再像傻逼一样"""
import requests
import json
import sys
import io

# 设置UTF-8编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("测试渐进式智能体 - 多轮对话")
print("=" * 70)

API_URL = 'http://localhost:8001'
session_id = None

def send_message(user_input, turn_number):
    global session_id

    print(f"\n{'=' * 70}")
    print(f"Turn {turn_number}")
    print(f"{'=' * 70}")
    print(f"[用户输入] {user_input}")

    payload = {'user_input': user_input}
    if session_id:
        payload['session_id'] = session_id

    response = requests.post(f'{API_URL}/inspire', json=payload)
    data = response.json()

    session_id = data['session_id']

    print(f"\n[系统响应]")
    print(f"  会话ID: {session_id[:8]}...")
    print(f"  轮次: {data['turn_number']}")
    print(f"  阶段: {data['state']['stage']}")

    # 关键词
    if data['state']['keywords']:
        print(f"\n  关键词: {', '.join(data['state']['keywords'])}")

    # 理论/作品灵感
    if data.get('theory_inspirations') or data.get('work_inspirations'):
        inspirations = (data.get('theory_inspirations', []) +
                       data.get('work_inspirations', []))
        if inspirations:
            print(f"\n  灵感内容 ({len(inspirations)}个):")
            for insp in inspirations:
                print(f"    - [{insp['type']}] {insp['title']}")

    # 视觉场景
    if data.get('visual_scenes'):
        scenes = data['visual_scenes']
        print(f"\n  视觉场景 ({len(scenes)}个):")
        for i, scene in enumerate(scenes, 1):
            print(f"    {i}. {scene['title']}")
            print(f"       画面: {scene['visual'][:60]}...")
            print(f"       声音: {scene['sound'][:60]}...")

    # 引导问题
    if data.get('guiding_questions'):
        questions = data['guiding_questions']
        print(f"\n  引导问题:")
        for q in questions:
            print(f"    ❓ {q['question']}")

    return data


# ========== 模拟多轮对话 ==========

print("\n\n开始测试...")

# Turn 1: 首次输入
print("\n测试点1: Turn 1应该只返回关键词+问题")
turn1 = send_message("我想拍一部关于记忆的电影", 1)

# Turn 2: 回答问题
print("\n\n测试点2: Turn 2应该返回理论+问题")
turn2 = send_message("我想探讨遗忘带来的身份危机", 2)

# Turn 3: 继续对话
print("\n\n测试点3: Turn 3应该返回作品参考+问题")
turn3 = send_message("普鲁斯特的理论很有启发", 3)

# Turn 4: 进入场景生成
print("\n\n测试点4: Turn 4应该返回第1个场景+问题")
turn4 = send_message("我喜欢非线性叙事", 4)

# Turn 5: 继续场景
print("\n\n测试点5: Turn 5应该返回第2个场景+问题")
turn5 = send_message("第一个场景很好,继续", 5)

# Turn 6: 测试挫败感检测
print("\n\n测试点6: 用户挫败时,系统应该调整策略")
turn6 = send_message("为什么始终没有具体的结果呢", 6)

print("\n\n" + "=" * 70)
print("测试完成!")
print("=" * 70)

print("\n验证要点:")
print("1. Turn 1是否只返回关键词?")
print("2. Turn 2是否返回理论?")
print("3. Turn 3是否返回作品?")
print("4. Turn 4-5是否逐个返回场景?")
print("5. Turn 6检测到挫败感,是否改变策略?")
