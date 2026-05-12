📄 [AssemPlanner: A Multi-Agent Based Task Planning Framework for Flexible Assembly System](https://arxiv.org/abs/2605.08831)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Conda or virtual environment
- OpenAI API Key (for LLM access)

### Environment Setup

```bash
# Create and activate environment
conda create --name assemplanner python=3.10
conda activate assemplanner

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
Embedding_API_KEY=your_embedding_key_here
Embedding_BASE_URL=https://api.openai.com/v1
```

## 📁 Project Structure

```
assemplanner/
├── QA/                    # RAG Question Answering Module
│   ├── QA_demo.py         # Demo script for RAG functionality
│   ├── QA_test.py         # Batch testing for QA pipeline
│   ├── test_acc.py        # Accuracy evaluation module
│   └── data_*.txt         # Dataset files
├── lightrag/              # Core RAG Implementation
│   ├── lightrag.py        # Main RAG configuration
│   ├── prompt.py          # Prompt templates for QA
│   ├── kg/                # Knowledge Graph implementations
│   └── llm/               # LLM integrations
├── LineBalancing/         # Line Balancing Optimization
│   ├── run.py             # Main execution script
│   ├── agent.py           # Line balancing agent
│   ├── reflexion.py       # Reflection mechanism
│   ├── memory.py          # Memory management
│   └── dataset/           # Line balance datasets
├── React/                 # ReAct Agent Module
│   ├── agent.py           # Main ReAct agent
│   ├── tools.py           # Tool definitions
│   ├── scene_graph.json   # Scene graph data
│   └── scene_graph.py     # Scene graph utilities
├── AssemPlanner/           # Visualization Dashboard
│   ├── flask_app.py       # Backend API
│   └── templates/         # Frontend templates
```

## 🧪 Running the Project

Follow these steps to run the complete pipeline:

### Step 1: Test RAG Module
```bash
python QA/QA_demo.py
```

### Step 2: Test Line Balancing
```bash
python LineBalancing/run.py
```

### Step 3: Test ReAct Agent
```bash
python React/agent.py
```

### Step 4: Launch Visualization Dashboard
```bash
python AssemPlanner/flask_app.py
```

## 📖 Module Details

### QA Module
- **QA_demo.py**: Generates knowledge graph and tests the complete QA pipeline
- **QA_test.py**: Runs batch testing with multiple questions
- **test_acc.py**: Evaluates answer accuracy against reference data

### LineBalancing Module
- **run.py**: Executes the line balancing optimization pipeline
- **agent.py**: LLM-based agent for solving line balancing problems
- **reflexion.py**: Self-reflection mechanism for iterative improvement
- **memory.py**: Stores and retrieves past solutions

### React Module
- **agent.py**: Integrates RAG and line balancing into a unified agent
- **scene_graph.py**: Scene graph visualization utilities
- **tools.py**: Tool definitions for the agent

### AssemPlanner Module
- **flask_app.py**: REST API for the web interface
- **templates/index.html**: Frontend dashboard
- **graph_visual_with_html.py**: Knowledge graph visualization

## 📊 Dataset Preparation

1. Place your assembly process data in `QA/data_*.txt`
2. Add test questions in `QA/questions&reference/`
3. Include reference answers in `QA/questions&reference/reference_*.json`

> To use your own data and prompts, refer to `QA/data_readme.md` for a detailed guide on dataset creation, prompt design, and knowledge graph construction.

## 🛠️ Available Tools

| Tool | Description |
|------|-------------|
| `RAGQuery` | Query assembly knowledge from knowledge graph |
| `LineBalance` | Optimize production line balancing |
| `DescribeMap` | Describe scene graph contents |

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Citation

```bibtex
@article{assemplanner,
  title={AssemPlanner: A Multi-Agent Based Task Planning Framework for Flexible Assembly System},
  author={Chenhao Zhang, Chaoran Zhang, Zhaobo Xu, YongboYang, Pingfa Feng, Long Zeng},
  journal={arXiv preprint arXiv:2605.08831},
  year={2026}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Note**: This is a research project for assembly process planning. Please ensure you have proper API credentials before running the code.