# Dataset Creation & Prompt Design & Knowledge Graph Building Guide

## Table of Contents

- [1. Dataset Creation](#1-dataset-creation)
- [2. Prompt Design](#2-prompt-design)
- [3. Knowledge Graph Construction](#3-knowledge-graph-construction)
- [4. Evaluation & Iteration](#4-evaluation--iteration)

---

## 1. Dataset Creation

### 1.1 Raw Data Format

Refer to `QA/data_connector.txt` and `QA/data_valve.txt`. Raw process documents follow this format:

```
Assembly Process for check valve cn1

1. Install O-ring: install O-ring, O-ring p175 along guide sleeve, push into plug corresponding groove. Tool: O-ring tool. Part: 1 O-ring p175, 1 plug p111.
2. Install valve core: place valve core into valve housing. Tool: general tool. Part: 1 valve core p113, 1 valve housing p109.
...
```

**Conventions:**

- One section per product, title format: `Assembly Process for <product_type> <product_id>`
- Step format: `<step_number>. <operation>: <description>. Tool: <tool>. Part: <part_list>`
- Separate multiple products with blank lines
- Use obfuscated IDs consistently (e.g. cn1, cm1)

### 1.2 Creating Question Sets

Refer to `questions_*.json` under `QA/questions&reference/`. Each JSON file corresponds to one question type:

| File | Question Type | Example |
|------|---------------|---------|
| `questions_1.json` | Single step query | "What is step 1 of connector cm1 assembly?" |
| `questions_2.json` | Parts & tools query | "What parts and tools are needed for step 1 of connector cm1 assembly?" |
| `questions_3.json` | Role identification | "In step 1 operation 05 install socket part of connector cm1, which part is the reference part?" |
| `questions_4.json` | Full process | "What is the complete assembly process of connector cm1?" |
| `questions_5.json` | Next step prediction | "What is the next step after step 1 of connector cm1 assembly?" |
| `questions_6.json` | Binary classification | "Does the assembly of connector cm1 require laser marking?" |

**Steps:**

1. Define the product scope (e.g. cn1~cn19)
2. Determine question types (the 6 types above cover most reasoning needs)
3. Generate question JSONs via script, ensuring coverage for every product and type
4. Check edge cases for each question (e.g. last step's "next step" should be empty)

### 1.3 Creating Reference Answers

Refer to `reference_*.json` under `QA/questions&reference/`. Format: `question` + `answer` pairs:

```json
{
  "question": "What is step 1 of connector cm1 assembly?",
  "answer": "1: install socket part ,single positive sheet-type socket part p163 install into insulator core p195 inner ."
}
```

**Conventions:**
- Extract answers directly from raw data for accuracy
- Keep answers concise, containing only essential information
- Match numbering with question sets (`reference_N.json` ↔ `questions_N.json`)

---

## 2. Prompt Design

Refer to `lightrag/prompt.py`. All prompts are managed in a single dictionary. Key design patterns below:

### 2.1 Prompt Architecture Overview

| Key | Purpose | Core Variables |
|-----|---------|----------------|
| `entity_extraction` | Extract entities & relations from text | `{entity_types}`, `{input_text}`, `{examples}` |
| `entity_continue_extraction` | Retrieve missed entities/relations | Same as above |
| `entity_if_loop_extraction` | Check if any missed entities remain | None (answers yes/no) |
| `summarize_entity_descriptions` | Merge/summarize entity descriptions | `{entity_name}`, `{description_list}` |
| `keywords_extraction` | Extract keywords from query | `{query}`, `{history}` |
| `rag_response` | Answer based on knowledge graph | `{context_data}`, `{history}` |
| `naive_rag_response` | Answer based on raw text chunks | `{content_data}`, `{history}` |
| `mix_rag_response` | Answer using KG + vector hybrid | `{kg_context}`, `{vector_context}`, `{history}` |
| `similarity_check` | Check two questions for similarity (cache) | `{original_prompt}`, `{cached_prompt}` |
| `fail_response` | Fallback when no answer available | Static string |

### 2.2 Entity Extraction Prompt Template (GSED Pattern)

```
---Goal---
Given a text document and a list of entity types ...

---Steps---
1. Identify all entities. Format: ("entity"<|>name<|>type<|>description)
2. Identify relationships: ("relationship"<|>source<|>target<|>desc<|>keywords<|>strength)
3. Extract content-level keywords

---Examples---
{examples}

---Real Data---
Entity_types: [{entity_types}]
Text: {input_text}

Output:
```

**Key Points:**
- **Delimiters**: `<|>` for fields, `##` for records, `<|COMPLETE|>` for termination
- **Few-shot examples**: Must be domain-relevant (e.g. assembly process) so the LLM understands the output format
- **Structured output**: Custom tuple format instead of JSON for easier parsing

### 2.3 QA Prompt Template (RGCR Pattern)

```
---Role---
You are a helpful assistant that can answer user queries about ...

---Goal---
Generate concise responses based on the knowledge base ...

---Knowledge Base---
{context_data}

---Response Rules---
- Answer in the same language as the user's question
- If the question is "What is step X of xxx assembly?", only answer "Step name: brief explanation"
- ...
```

**Key Points:**
- **Explicit response rules**: Format constraints for each question type
- **No hallucination**: LLM must answer based solely on provided data
- **Language consistency**: Match the user's query language

### 2.4 Prompt Design Best Practices

1. **Domain-specific Entity Types**: Avoid generic types. Define assembly-specific ones like `["AssemblyProcess", "Product", "Connector", "AssemblyAction", "Component"]`
2. **Align few-shot examples with real data**: Products and operations in examples should resemble actual data
3. **Output format constraints**: Custom delimiters are more reliable than JSON (avoid JSON escaping issues)
4. **Gleaning loop**: First pass may miss entities; use `continue_extraction` + `if_loop_extraction` for multi-round supplementation
5. **Specific Response Rules**: Write different rules per question type to control output length and format
6. **Consistent constants**: Keep `DEFAULT_TUPLE_DELIMITER`, `DEFAULT_RECORD_DELIMITER`, etc. uniform

---

## 3. Knowledge Graph Construction

KG construction pipeline based on LightRAG:

### 3.1 Pipeline

```
Raw Documents
    │
    ▼
Chunking (chunking_by_token_size)
    │
    ▼
Entity Extraction per Chunk (entity_extraction prompt)
    │
    ▼
Parse LLM Output → Extract Entities + Relation Tuples
    │
    ▼
Gleaning Loop → Supplement Missing Entities (continue + if_loop)
    │
    ▼
Cross-chunk Merge → Dedup + Description Consolidation
    │
    ▼
Persist to Storage:
    ├── Graph Store (Neo4j / NetworkX / others)
    ├── Entity Vector DB (semantic search)
    └── Relation Vector DB (semantic search)
```

### 3.2 Key Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `chunk_size` | Document chunk size (tokens) | 1200 |
| `chunk_overlap_size` | Chunk overlap size | 100 |
| `entity_extract_max_gleaning` | Max gleaning rounds | 1 |
| `max_token_summary` | Max tokens for entity description | 500 |
| `top_k` | Top-k retrieval results | 20 |
| `max_token_text_chunk` | Max tokens for retrieved text chunk | 3000 |
| `enable_llm_cache_for_extract` | Cache extraction results | False |

### 3.3 Entity Type Definitions

Recommended entity types for the assembly domain:

```python
DEFAULT_ENTITY_TYPES = [
    "AssemblyProcess",   # e.g. Step 1 Install O-ring
    "Product",           # e.g. Check Valve cn1
    "Connector",         # Connector type
    "AssemblyAction",    # e.g. install, press-fit
    "Component",         # e.g. O-ring, valve core
    "Tool",              # e.g. O-ring tool
    "Part"               # e.g. p175
]
```

### 3.4 Relationship Definitions

Extracted relationships contain:
- `source_entity` → `target_entity`
- `relationship_description`: Description of the relationship
- `relationship_strength`: Strength score (1-10)
- `relationship_keywords`: Keywords (e.g. `"AssemblyStep"`, `"PartResource"`, `"ComponentAttribute"`)

Example relationships:
```
("relationship"<|>"Process 1 Install O-ring"<|>"Check Valve cn1"<|>"Installing O-ring is the first assembly step"<|>"AssemblyStep"<|>9)
("relationship"<|>"O-ring"<|>"Process 1 Install O-ring"<|>"Process 1 requires O-ring"<|>"PartResource"<|>9)
```

### 3.5 Query Modes

LightRAG supports multiple query modes:

| Mode | Description | Use Case |
|------|-------------|----------|
| `naive` | Vector search only on raw chunks | Simple fact queries |
| `local` | Knowledge graph only | Relation reasoning, multi-hop queries |
| `global` | KG + community summaries | Broad, summary questions |
| `mix` | KG + vector hybrid | Comprehensive queries (recommended) |
| `hybrid` | Local + Global combination | When both local and global context needed |

### 3.6 LightRAG Quick Start

```python
from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
import numpy as np

rag = LightRAG(
    working_dir="./my_project",
    llm_model_func=my_llm_func,
    embedding_func=EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=512,
        func=my_embedding_func
    ),
    addon_params={
        "language": "English",
        "entity_types": [
            "AssemblyProcess", "Product", "Connector",
            "AssemblyAction", "Component", "Tool", "Part"
        ]
    }
)

# Insert data
with open("QA/data_valve.txt") as f:
    rag.insert(f.read())

# Query
result = rag.query(
    "What tools are needed for check valve assembly?",
    param=QueryParam(mode="mix")
)
```

---

## 4. Evaluation & Iteration

### 4.1 Evaluation Process

Refer to `QA/test_acc.py` for LLM-as-Judge evaluation:

1. Load generated answers and reference answers
2. Use an LLM judge to evaluate each answer (correct / wrong / question_not_matched)
3. Calculate accuracy

### 4.2 Optimization Directions

1. **Tune Prompts**: Modify few-shot examples in `entity_extraction` to better match actual data
2. **Adjust Entity Types**: Add or merge entity types based on business needs
3. **Tweak Chunking Strategy**: Modify `chunk_size` and `chunk_overlap_size`
4. **Increase Gleaning Rounds**: Raise `entity_extract_max_gleaning` to improve recall
5. **Refine Response Rules**: Strengthen rules for question types that perform poorly

### 4.3 Recommended File Organization

```
project/
├── data/                    # Raw process data
│   ├── data_product_a.txt
│   └── data_product_b.txt
├── questions/               # Question sets
│   ├── questions_1.json
│   └── questions_2.json
├── references/              # Reference answers
│   ├── reference_1.json
│   └── reference_2.json
├── answers/                 # Model-generated answers
│   └── answers_1.json
├── comparison_results/      # Evaluation results
├── prompt.py                # Custom prompts (extend or override LightRAG defaults)
└── run.py                   # Build + query + evaluation script
```
