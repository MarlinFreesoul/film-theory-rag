"""
测试视觉化场景生成功能
"""
import requests
import json

print("=" * 60)
print("测试视觉化场景生成")
print("=" * 60)

response = requests.post(
    'http://localhost:8000/inspire',
    json={'user_input': '我想拍一部关于记忆的电影'}
)

data = response.json()

print(f"\n会话ID: {data['session_id']}")
print(f"轮次: {data['turn_number']}")
print(f"阶段: {data['state']['stage']}")
print(f"关键词: {data['state']['keywords']}")

# 检查视觉化场景
print(f"\n视觉化场景数量: {len(data.get('visual_scenes', []))}")

for i, scene in enumerate(data.get('visual_scenes', []), 1):
    print(f"\n{'=' * 50}")
    print(f"场景 {i}: {scene['title']}")
    print(f"{'=' * 50}")
    print(f"张力: {scene['tension']}")
    print(f"\n🎥 画面:")
    print(f"  {scene['visual']}")
    print(f"\n🔊 声音:")
    print(f"  {scene['sound']}")
    print(f"\n⏱ 时长: {scene['duration']}")
    print(f"\n💡 激发目的:")
    print(f"  {scene['purpose']}")
