#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


JAVA_PROJECTS = {
    "beam",
    "camel",
    "cassandra",
    "dolphinscheduler",
    "doris",
    "druid",
    "dubbo",
    "dubbo-spring-boot-project",
    "flink",
    "flink-cdc",
    "hadoop",
    "hbase",
    "hertzbeat",
    "hive",
    "hudi",
    "iceberg",
    "incubator-kie-drools",
    "incubator-seata",
    "incubator-weex",
    "iotdb",
    "jmeter",
    "kafka",
    "pinot",
    "pulsar",
    "rocketmq",
    "seatunnel",
    "shardingsphere",
    "shardingsphere-elasticjob",
    "shenyu",
    "skywalking",
    "storm",
    "tomcat",
    "zeppelin",
    "zookeeper",
}


def extract_java_records(input_path: Path, output_path: Path) -> tuple[int, int, int]:
    total = 0
    matched = 0
    invalid = 0

    with input_path.open("r", encoding="utf-8") as fin, output_path.open(
        "w", encoding="utf-8"
    ) as fout:
        for raw_line in fin:
            line = raw_line.strip()
            if not line:
                continue

            total += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                invalid += 1
                continue

            if item.get("repo") in JAVA_PROJECTS:
                fout.write(raw_line if raw_line.endswith("\n") else raw_line + "\n")
                matched += 1

    return total, matched, invalid


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract Java project records from a JSONL file."
    )
    parser.add_argument(
        "--input",
        default="full.jsonl",
        help="Input JSONL file path (default: full.jsonl)",
    )
    parser.add_argument(
        "--output",
        default="full_java_projects.jsonl",
        help="Output JSONL file path (default: full_java_projects.jsonl)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    total, matched, invalid = extract_java_records(input_path, output_path)
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Total non-empty lines: {total}")
    print(f"Matched Java project lines: {matched}")
    print(f"Invalid JSON lines skipped: {invalid}")


if __name__ == "__main__":
    main()
