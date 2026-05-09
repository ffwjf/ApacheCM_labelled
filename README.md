# Label Dataset 筛选与处理流水线

本目录包含了从原始 `full.jsonl` 数据集中筛选、清洗并标注 Java、C++ 和 Python 项目提交记录的完整工具链和处理结果。

## 目录结构

```text
label_dataset/
├── Java/               # Java 项目处理流程与结果
│   ├── extract_java_projects.py    # 步骤1：按项目名提取
│   ├── filter_java_dataset.py     # 步骤2：整合筛选与打标
│   ├── full_java_projects.jsonl   # 中间产物：Java 项目全量记录(untracked)
│   ├── full_java_balanced.jsonl   # 最终产物：正负类均衡的数据集
│   └── 筛选流程记录.md             # Java 详细处理步骤与统计
├── cpp/                # C++ 项目处理流程与结果
│   ├── extract_cpp_projects.py     # 步骤1：按项目名提取
│   ├── filter_cpp_dataset.py      # 步骤2：整合筛选与打标
│   ├── full_cpp_projects.jsonl    # 中间产物：C++ 项目全量记录(untracked)
│   ├── full_cpp_balanced.jsonl    # 最终产物：正负类均衡的数据集
│   └── 筛选流程记录.md             # C++ 详细处理步骤与统计
├── python/             # Python 项目处理流程与结果
│   ├── extract_python_projects.py  # 步骤1：按项目名提取
│   ├── filter_python_dataset.py   # 步骤2：整合筛选与打标
│   ├── full_python_projects.jsonl # 中间产物：Python 项目全量记录(untracked)
│   ├── full_python_balanced.jsonl # 最终产物：正负类均衡的数据集
│   └── 筛选流程记录.md             # Python 详细处理步骤与统计
├── full.jsonl          # 原始全量数据集（约 25 万条）(untracked)
├── 项目语言分类.md       # 参与筛选的项目名单及语言分类
└── calculate_stats.py   # 跨语言通用的均衡数据集统计脚本
```

## 核心筛选逻辑

为了构建用于“核心类定位”任务的数据集，我们采用了统一的简化筛选策略：

1.  **项目提取**：根据各语言预定义的开源项目名单，从 `full.jsonl` 中提取特定语言的子集。
2.  **Diff 锚点提取**：解析提交的 Diff 内容，提取受影响的实质性代码实体（Java/C++ 的类、结构体，Python 的类、函数）。
3.  **动态匹配**：
    *   将 Diff 中的实体名作为锚点，在 Commit Message 中进行搜索。
    *   **动态大小写敏感**：若 Diff 实体列表中无大小写冲突，则进行不区分大小写匹配；若存在冲突（如 `Buffer` 与 `buffer`），则强制区分大小写匹配。
4.  **均衡性过滤**：
    *   涉及实体总数 $N \ge 2$。
    *   被 Message 提到的实体（Positive）数量 $P \ge 1$。
    *   未被 Message 提到的实体（Negative）数量 $M \ge 1$。
    *   即：$1 \le P < N$。

## 统计摘要

| 语言 | 原始项目记录 | 最终均衡样本 | 平均实体数/样本 |
| :--- | :--- | :--- | :--- |
| **Java** | 172,277 | 18,726 | 3.7841 |
| **Python** | 20,081 | 5,037 | 8.5076 |
| **C++** | 16,468 | 1,545 | 4.3540 |

## 使用说明

### 1. 重新生成数据集
进入对应语言目录，依次运行提取和筛选脚本。例如处理 C++：
```bash
cd cpp
python3 extract_cpp_projects.py --input ../full.jsonl
python3 filter_cpp_dataset.py
```

### 2. 更新统计信息
使用根目录下的 `calculate_stats.py` 对任何 `balanced.jsonl` 文件进行指标统计：
```bash
python3 calculate_stats.py Java/full_java_balanced.jsonl
```
