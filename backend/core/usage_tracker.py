"""
Usage Tracker - LLM用量监控

功能：
- 跟踪每次LLM调用的token使用量
- 计算成本（基于Claude Haiku定价）
- 提供统计报表
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from datetime import datetime
import json


@dataclass
class UsageRecord:
    """单次调用记录"""
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    purpose: str  # "keyword_extraction", "translation", etc.


class UsageTracker:
    """用量跟踪器"""

    # Claude Haiku定价（2024年价格）
    PRICING = {
        "claude-3-haiku-20240307": {
            "input": 0.25 / 1_000_000,   # $0.25 per 1M tokens
            "output": 1.25 / 1_000_000,  # $1.25 per 1M tokens
        }
    }

    def __init__(self):
        self.records: List[UsageRecord] = []
        print("[UsageTracker] Initialized")

    def record(self, model: str, input_tokens: int, output_tokens: int, purpose: str = "unknown"):
        """
        记录一次LLM调用

        Args:
            model: 模型名称
            input_tokens: 输入token数
            output_tokens: 输出token数
            purpose: 调用目的
        """
        # 计算成本
        pricing = self.PRICING.get(model, self.PRICING["claude-3-haiku-20240307"])
        cost = (input_tokens * pricing["input"]) + (output_tokens * pricing["output"])

        record = UsageRecord(
            timestamp=datetime.now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            purpose=purpose
        )

        self.records.append(record)

        print(f"[UsageTracker] {purpose}: {input_tokens}in + {output_tokens}out = ${cost:.6f}")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据"""
        if not self.records:
            return {
                "total_calls": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost_usd": 0,
                "avg_cost_per_call": 0,
                "by_purpose": {}
            }

        total_input = sum(r.input_tokens for r in self.records)
        total_output = sum(r.output_tokens for r in self.records)
        total_cost = sum(r.cost_usd for r in self.records)

        # 按用途分组统计
        by_purpose = {}
        for record in self.records:
            if record.purpose not in by_purpose:
                by_purpose[record.purpose] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0
                }

            by_purpose[record.purpose]["calls"] += 1
            by_purpose[record.purpose]["input_tokens"] += record.input_tokens
            by_purpose[record.purpose]["output_tokens"] += record.output_tokens
            by_purpose[record.purpose]["cost_usd"] += record.cost_usd

        return {
            "total_calls": len(self.records),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_input + total_output,
            "total_cost_usd": total_cost,
            "avg_cost_per_call": total_cost / len(self.records),
            "by_purpose": by_purpose,
            "latest_records": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "purpose": r.purpose,
                    "tokens": f"{r.input_tokens}in + {r.output_tokens}out",
                    "cost": f"${r.cost_usd:.6f}"
                }
                for r in self.records[-10:]  # 最近10条
            ]
        }

    def get_cost_breakdown(self) -> Dict[str, Any]:
        """获取成本明细"""
        stats = self.get_stats()

        return {
            "summary": {
                "total_cost": f"${stats['total_cost_usd']:.4f}",
                "total_calls": stats['total_calls'],
                "avg_per_call": f"${stats['avg_cost_per_call']:.6f}"
            },
            "by_purpose": {
                purpose: {
                    "calls": data["calls"],
                    "cost": f"${data['cost_usd']:.4f}",
                    "tokens": data["input_tokens"] + data["output_tokens"]
                }
                for purpose, data in stats['by_purpose'].items()
            },
            "pricing_info": {
                "model": "claude-3-haiku-20240307",
                "input_price": "$0.25 / 1M tokens",
                "output_price": "$1.25 / 1M tokens"
            }
        }

    def reset(self):
        """重置统计"""
        self.records.clear()
        print("[UsageTracker] Stats reset")

    def export_to_json(self, filepath: str):
        """导出为JSON"""
        data = {
            "exported_at": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "records": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "model": r.model,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "cost_usd": r.cost_usd,
                    "purpose": r.purpose
                }
                for r in self.records
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"[UsageTracker] Exported to {filepath}")


# 全局单例
_tracker_instance = None

def get_tracker() -> UsageTracker:
    """获取全局跟踪器实例"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = UsageTracker()
    return _tracker_instance
