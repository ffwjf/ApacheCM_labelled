#!/usr/bin/env python3
import json
import argparse
import sys
from pathlib import Path

def calculate_stats(input_path: Path):
    if not input_path.exists():
        print(f"Error: File {input_path} not found.")
        return None

    total_records = 0
    
    class_counts = []
    positive_counts = []
    negative_counts = []

    with input_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                labels = item.get("class_labels", {})
                if not labels:
                    continue
                
                total_records += 1
                
                n_total = len(labels)
                n_pos = sum(1 for v in labels.values() if v == "positive")
                n_neg = n_total - n_pos
                
                class_counts.append(n_total)
                positive_counts.append(n_pos)
                negative_counts.append(n_neg)
            except:
                continue

    if not class_counts:
        print("No valid records found.")
        return None

    def get_metrics(data):
        return {
            "max": max(data),
            "min": min(data),
            "avg": sum(data) / len(data),
            "total": sum(data)
        }

    stats = {
        "class": get_metrics(class_counts),
        "positive": get_metrics(positive_counts),
        "negative": get_metrics(negative_counts),
        "records": total_records
    }
    
    return stats

def format_stats(stats):
    lines = []
    for key in ["class", "positive", "negative"]:
        m = stats[key]
        lines.append(f"- {key}：")
        lines.append(f"  - max：`{m['max']}`")
        lines.append(f"  - min：`{m['min']}`")
        lines.append(f"  - avg：`{m['avg']:.4f}`")
        lines.append(f"  - total：`{m['total']}`")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Calculate stats for balanced jsonl.")
    parser.add_argument("input", help="Input JSONL path")
    args = parser.parse_args()
    
    stats = calculate_stats(Path(args.input))
    if stats:
        print(format_stats(stats))

if __name__ == "__main__":
    main()
