import numpy as np
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc
from LineBalancing.reflexion import ReflexionWrapper
from LineBalancing.memory import MemoryManager
from LineBalancing.linebalancing import LineBalancingAgent
import json
import os


async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
    """Configure and call LLM model"""
    return await openai_complete_if_cache(
        model="gpt-4.1",
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        **kwargs,
    )


async def embedding_func(texts: list[str]) -> np.ndarray:
    """Embedding function for text embedding"""
    all_embeddings = []
    batch_size = 10
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = await openai_embed(
            batch,
            model="text-embedding-v4",
            api_key=os.getenv("Embedding_API_KEY"),
            base_url=os.getenv("Embedding_BASE_URL")
        )
        all_embeddings.append(embeddings)
    return np.concatenate(all_embeddings, axis=0)


async def get_embedding_dim():
    """Get embedding dimension"""
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    return embedding.shape[1]


async def RAGQuery(query: str, mode: str = "mix") -> str:
    """RAG Tool for querying assembly-related knowledge"""
    embedding_dim = await get_embedding_dim()
    rag = LightRAG(
        working_dir="./dickens_valve",
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=512,
            func=embedding_func
        )
    )
    await rag.initialize_storages()

    prompt = "Please answer the following question in English:\n" + query
    resp = await rag.aquery(prompt, param=QueryParam(mode=mode))
    return resp.answer if hasattr(resp, "answer") else str(resp)


MAX_RETRY = 3

async def LineBalance(question: str) -> str:
    """Line balancing tool for assembly line optimization"""
    agent = LineBalancingAgent("gpt-4o")
    reflexion_agent = ReflexionWrapper("gpt-4o")
    memory = MemoryManager()

    answer = ""
    for attempt in range(MAX_RETRY):
        print(f"\n🔁 Attempt {attempt+1}...")
        answer = agent.solve(question, memory.format())
        print(f"Answer:\n{answer}")

        reflection = reflexion_agent.reflect(question, answer)
        print(f"🧠 Reflection:\n{reflection}")
        memory.add(question, answer, reflection)

    return f"Final Answer (Attempt {MAX_RETRY}):\n{answer}"


async def DescribeMap() -> str:
    """DescribeMap tool: Read scene graph and return natural language description"""
    file_path = os.path.join(os.path.dirname(__file__), "scene_graph.json")

    if not os.path.exists(file_path):
        return f"❌ Scene graph file not found: {file_path}. Please verify the file path."

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"❌ Error reading scene graph: {str(e)}"

    nodes = {node["id"]: node for node in data["nodes"]}
    room_contents = {}

    for edge in data["edges"]:
        item_id = edge["source"]
        room_id = edge["target"]
        if room_id not in room_contents:
            room_contents[room_id] = []
        room_contents[room_id].append(nodes[item_id]["name"])

    descriptions = []
    for room_id, contents in room_contents.items():
        room = nodes[room_id]
        tools = [name for name in contents if "Tool" in name]
        parts = [name for name in contents if name not in tools]

        desc = f"{room['name']} contains:"
        items = []
        if tools:
            items.append("Tools (" + ", ".join(tools) + ")")
        if parts:
            items.append("Parts (" + ", ".join(parts) + ")")
        desc += "; ".join(items) + "."
        descriptions.append(desc)

    return "\n".join(descriptions)