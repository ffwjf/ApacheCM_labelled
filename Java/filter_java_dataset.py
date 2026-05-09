#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

# Java file extensions to consider
JAVA_EXTENSIONS = {".java"}

# Regex to find class, interface, enum, or record declarations in diff lines
CLASS_DECL_RE = re.compile(r"\b(?:class|interface|enum|record)\s+([a-zA-Z0-9_]+)\b")

# Regex for git diff file paths
GIT_DIFF_PATH_RE = re.compile(r"[ab]/(.+)")

def get_class_from_path(path_text: str) -> str | None:
    path = Path(path_text)
    if path.suffix.lower() not in JAVA_EXTENSIONS:
        return None
    stem = path.stem
    # Java classes usually match the filename
    if stem and stem[0].isupper():
        return stem
    return None

def parse_diff_classes(diff_text: str) -> set[str]:
    classes_in_diff: set[str] = set()

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                right_path = parts[3]
                m = GIT_DIFF_PATH_RE.match(right_path)
                if m:
                    class_name = get_class_from_path(m.group(1))
                    if class_name:
                        classes_in_diff.add(class_name)
            continue

        if not line or len(line) < 2:
            continue

        # Look for declarations in added or context lines
        content = line[1:] if line[0] in "+- " else line
        
        for match in CLASS_DECL_RE.finditer(content):
            classes_in_diff.add(match.group(1))
            
    return classes_in_diff

def is_class_mentioned(message: str, class_name: str, case_sensitive: bool = False) -> bool:
    flags = 0 if case_sensitive else re.IGNORECASE
    # Use word boundaries to avoid partial matches
    pattern = r"\b" + re.escape(class_name) + r"\b"
    if re.search(pattern, message, flags):
        return True
    return False

def process_record(item: dict) -> dict | None:
    diff_text = item.get("diff", "")
    message = item.get("message", "")
    if not isinstance(diff_text, str) or not isinstance(message, str):
        return None

    diff_classes = parse_diff_classes(diff_text)
    if not diff_classes:
        return None

    # Filter out very short or numeric "classes"
    diff_classes = {c for c in diff_classes if len(c) > 2 and not c.isdigit()}
    
    if len(diff_classes) < 2:
        return None

    # Optimization: Check for case conflicts
    lower_to_orig = {}
    case_conflicts = set()
    for cls in diff_classes:
        lcls = cls.lower()
        if lcls in lower_to_orig and lower_to_orig[lcls] != cls:
            case_conflicts.add(lcls)
        lower_to_orig[lcls] = cls

    class_labels = {}
    positive_count = 0
    
    for cls in sorted(diff_classes):
        needs_case_sensitive = cls.lower() in case_conflicts
        if is_class_mentioned(message, cls, case_sensitive=needs_case_sensitive):
            class_labels[cls] = "positive"
            positive_count += 1
        else:
            class_labels[cls] = "negative"

    # Balanced condition: at least one positive AND at least one negative
    if 1 <= positive_count < len(diff_classes):
        item["class_labels"] = class_labels
        return item
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Unified Java dataset filter and labeler.")
    parser.add_argument("--input", default="full_java_projects.jsonl", help="Input JSONL path")
    parser.add_argument("--output", default="full_java_balanced.jsonl", help="Output JSONL path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        script_dir = Path(__file__).parent
        input_path = (script_dir / args.input).resolve()
        if not input_path.exists():
            print(f"Error: Input file {args.input} not found.")
            return

    total = 0
    kept = 0
    
    with input_path.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line: continue
            total += 1
            try:
                item = json.loads(line)
            except:
                continue
                
            result = process_record(item)
            if result:
                fout.write(json.dumps(result, ensure_ascii=False) + "\n")
                kept += 1

    print(f"Processed {total} records.")
    print(f"Kept {kept} balanced records.")
    print(f"Output saved to {output_path}")

if __name__ == "__main__":
    main()
