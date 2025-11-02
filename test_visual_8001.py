"""测试8001端口的视觉化场景生成"""
import requests
import json
import sys
import io

# 设置UTF-8编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("=" * 60)
print("测试视觉化场景生成 (端口8001)")
print("=" * 60)

response = requests.post(
    'http://localhost:8001/inspire',
    json={'user_input': '我想拍一部关于记忆的电影'}
)

data = response.json()

print(f"\n[OK] Status code: {response.status_code}")
print(f"会话ID: {data.get('session_id')}")
print(f"轮次: {data.get('turn_number')}")
print(f"阶段: {data.get('state', {}).get('stage')}")
print(f"关键词: {data.get('state', {}).get('keywords')}")

# 检查视觉化场景
visual_scenes = data.get('visual_scenes', [])
print(f"\n[SCENES] Count: {len(visual_scenes)}")

for i, scene in enumerate(visual_scenes, 1):
    print(f"\n{'=' * 50}")
    print(f"场景 {i}: {scene.get('title', 'N/A')}")
    print(f"{'=' * 50}")
    # 使用errors='replace'处理无法编码的字符
    tension = scene.get('tension', 'N/A')
    print(f"张力标签: {tension}")
    print(f"\n[VISUAL] {scene.get('visual', 'N/A')}")
    print(f"\n[SOUND] {scene.get('sound', 'N/A')}")
    print(f"\n[DURATION] {scene.get('duration', 'N/A')}")
    print(f"\n[PURPOSE] {scene.get('purpose', 'N/A')}")
