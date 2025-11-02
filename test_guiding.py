"""
测试引导问题功能
"""
import requests
import json

# 第一轮对话
print("=" * 60)
print("第一轮：我想拍一部关于记忆的电影")
print("=" * 60)

response1 = requests.post(
    'http://localhost:8000/inspire',
    json={'user_input': '我想拍一部关于记忆的电影'}
)

data1 = response1.json()
print(f"\n会话ID: {data1['session_id']}")
print(f"轮次: {data1['turn_number']}")
print(f"阶段: {data1['state']['stage']}")
print(f"关键词: {data1['state']['keywords']}")
print(f"\n引导问题数量: {len(data1.get('guiding_questions', []))}")

for i, q in enumerate(data1.get('guiding_questions', []), 1):
    print(f"\n问题 {i}:")
    print(f"  - {q['question']}")
    print(f"  - 目的: {q['purpose']}")

# 第二轮对话（使用session_id）
print("\n\n" + "=" * 60)
print("第二轮：关于童年的美好时光")
print("=" * 60)

response2 = requests.post(
    'http://localhost:8000/inspire',
    json={
        'user_input': '关于童年的美好时光',
        'session_id': data1['session_id']
    }
)

data2 = response2.json()
print(f"\n会话ID: {data2['session_id']}")
print(f"轮次: {data2['turn_number']}")
print(f"阶段: {data2['state']['stage']}")
print(f"关键词: {data2['state']['keywords']}")
print(f"\n引导问题数量: {len(data2.get('guiding_questions', []))}")

for i, q in enumerate(data2.get('guiding_questions', []), 1):
    print(f"\n问题 {i}:")
    print(f"  - {q['question']}")
    print(f"  - 目的: {q['purpose']}")
