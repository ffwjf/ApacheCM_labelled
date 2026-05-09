#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

# Python file extensions to consider
PYTHON_EXTENSIONS = {".py"}

# Regex to find class or function declarations in diff lines
# It matches 'class Name' or 'def Name'
DECL_RE = re.compile(r"\b(?:class|def)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b")

# Regex for git diff file paths
GIT_DIFF_PATH_RE = re.compile(r"[ab]/(.+)")

def get_symbol_from_path(path_text: str) -> str | None:
    path = Path(path_text)
    if path.suffix.lower() not in PYTHON_EXTENSIONS:
        return None
    stem = path.stem
    # If it's a module name, it might be relevant
    if stem and stem != "__init__":
        return stem
    return None

def parse_diff_symbols(diff_text: str) -> set[str]:
    symbols_in_diff: set[str] = set()

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            if len(parts) >= 4:
                right_path = parts[3]
                m = GIT_DIFF_PATH_RE.match(right_path)
                if m:
                    symbol_name = get_symbol_from_path(m.group(1))
                    if symbol_name:
                        symbols_in_diff.add(symbol_name)
            continue

        if not line or len(line) < 2:
            continue

        # Look for declarations in added or context lines
        content = line[1:] if line[0] in "+- " else line
        
        for match in DECL_RE.finditer(content):
            symbols_in_diff.add(match.group(1))
            
    return symbols_in_diff

def is_symbol_mentioned(message: str, symbol_name: str, case_sensitive: bool = False) -> bool:
    flags = 0 if case_sensitive else re.IGNORECASE
    # Use word boundaries to avoid partial matches
    pattern = r"\b" + re.escape(symbol_name) + r"\b"
    if re.search(pattern, message, flags):
        return True
    return False

def process_record(item: dict) -> dict | None:
    diff_text = item.get("diff", "")
    message = item.get("message", "")
    if not isinstance(diff_text, str) or not isinstance(message, str):
        return None

    diff_symbols = parse_diff_symbols(diff_text)
    if not diff_symbols:
        return None

    # Filter out very short symbols
    diff_symbols = {s for s in diff_symbols if len(s) > 2}
    
    if len(diff_symbols) < 2:
        return None

    # Optimization: Check for case conflicts
    lower_to_orig = {}
    case_conflicts = set()
    for sym in diff_symbols:
        lsym = sym.lower()
        if lsym in lower_to_orig and lower_to_orig[lsym] != sym:
            case_conflicts.add(lsym)
        lower_to_orig[lsym] = sym

    class_labels = {}
    positive_count = 0
    
    for symbol in sorted(diff_symbols):
        needs_case_sensitive = symbol.lower() in case_conflicts
        if is_symbol_mentioned(message, symbol, case_sensitive=needs_case_sensitive):
            class_labels[symbol] = "positive"
            positive_count += 1
        else:
            class_labels[symbol] = "negative"

    # Balanced condition: at least one positive AND at least one negative
    if 1 <= positive_count < len(diff_symbols):
        item["class_labels"] = class_labels
        return item
    
    return None

def main():
    parser = argparse.ArgumentParser(description="Unified Python dataset filter and labeler.")
    parser.add_argument("--input", default="full_python_projects.jsonl", help="Input JSONL path")
    parser.add_argument("--output", default="full_python_balanced.jsonl", help="Output JSONL path")
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
