import os
import asyncio
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import EmbeddingFunc
import numpy as np
import json

WORKING_DIR = "./dickens"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def llm_model_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
    """LLM model function wrapper"""
    return await openai_complete_if_cache(
        "gpt-3.5-turbo",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        **kwargs,
    )


async def embedding_func(texts: list[str]) -> np.ndarray:
    """Embedding function with batch processing"""
    all_embeddings = []
    batch_size = 10

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        embeddings = await openai_embed(
            batch,
            model="text-embedding-v4",
            api_key=os.getenv("Embedding_API_KEY"),
            base_url=os.getenv("Embedding_BASE_URL"),
        )
        all_embeddings.append(embeddings)

    return np.concatenate(all_embeddings, axis=0)


async def get_embedding_dim():
    """Get embedding dimension"""
    test_text = ["This is a test sentence."]
    embedding = await embedding_func(test_text)
    embedding_dim = embedding.shape[1]
    return embedding_dim


async def initialize_rag():
    """Initialize RAG instance"""
    embedding_dimension = await get_embedding_dim()
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dimension,
            max_token_size=512,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    return rag


async def query_and_write(rag, question, output_file):
    """Query RAG and write result to file"""
    try:
        question = question.strip()
        if question:
            answer = await rag.aquery(question, param=QueryParam(mode="mix"))
            qa_pair = {"question": question, "answer": answer}
            
            with open(output_file, 'a', encoding='utf-8') as out_f:
                json.dump(qa_pair, out_f, ensure_ascii=False, indent=2)
                out_f.write("\n")
            
            print(f"Question: {question}\nAnswer: {answer}\n")
            await asyncio.sleep(10)

    except Exception as e:
        print(f"Error processing question: {e}")


async def process_file(rag, file_path, output_file):
    """Process questions from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write("[\n")

        for i, data in enumerate(questions_data):
            question = data.get("question", "").strip()
            if question:
                await query_and_write(rag, question, output_file)

            with open(output_file, 'a', encoding='utf-8') as out_f:
                if i == len(questions_data) - 1:
                    out_f.write("\n")
                else:
                    out_f.write(",\n")

        with open(output_file, 'a', encoding='utf-8') as out_f:
            out_f.write("]\n")

    except FileNotFoundError:
        print(f"File {file_path} not found.")
    except Exception as e:
        print(f"Error processing file: {e}")


def main():
    """Main function"""
    rag = asyncio.run(initialize_rag())

    # Insert assembly data into RAG
    data_file = "QA/data_connector.txt"
    if os.path.exists(data_file):
        with open(data_file, "r", encoding="utf-8") as f:
            rag.insert(f.read())
    data_file2 = "QA/data_valve.txt"
    if os.path.exists(data_file2):
        with open(data_file2, "r", encoding="utf-8") as f:
            rag.insert(f.read())

    input_question_file = os.path.join("QA", "questions&reference", "questions_5.json")
    output_answer_file = "QA/answers_5.json"

    asyncio.run(process_file(rag, input_question_file, output_answer_file))


if __name__ == "__main__":
    main()