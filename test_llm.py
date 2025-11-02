"""
测试LLM关键词提取功能
"""
import requests
import json

# 测试请求
response = requests.post(
    'http://localhost:8000/inspire',
    json={'user_input': '我想要更现代的感觉'}
)

print("=" * 60)
print("测试: 我想要更现代的感觉")
print("=" * 60)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

# 查看用量统计
usage = requests.get('http://localhost:8000/usage')
print("=" * 60)
print("LLM用量统计")
print("=" * 60)
print(json.dumps(usage.json(), indent=2, ensure_ascii=False))
