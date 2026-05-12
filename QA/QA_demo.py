import os
import asyncio
import inspect
import logging
import logging.config
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc, logger, set_verbose_debug
import numpy as np
from lightrag.kg.shared_storage import initialize_pipeline_status
from dotenv import load_dotenv
load_dotenv()
load_dotenv(dotenv_path="./.env")

WORKING_DIR = "./dickens_valve"


def configure_logging():
    """Configure logging for the application"""
    for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error", "lightrag"]:
        logger_instance = logging.getLogger(logger_name)
        logger_instance.handlers = []
        logger_instance.filters = []

    log_dir = os.getenv("LOG_DIR", os.getcwd())
    log_file_path = os.path.abspath(os.path.join(log_dir, "lightrag_compatible_demo.log"))

    print(f"\nLightRAG compatible demo log file: {log_file_path}\n")
    os.makedirs(os.path.dirname(log_dir), exist_ok=True)

    log_max_bytes = int(os.getenv("LOG_MAX_BYTES", 10485760))
    log_backup_count = int(os.getenv("LOG_BACKUP_COUNT", 5))

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": "%(levelname)s: %(message)s"},
            "detailed": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"},
        },
        "handlers": {
            "console": {"formatter": "default", "class": "logging.StreamHandler", "stream": "ext://sys.stderr"},
            "file": {"formatter": "detailed", "class": "logging.handlers.RotatingFileHandler",
                     "filename": log_file_path, "maxBytes": log_max_bytes, "backupCount": log_backup_count, "encoding": "utf-8"},
        },
        "loggers": {"lightrag": {"handlers": ["console", "file"], "level": "INFO", "propagate": False}},
    })

    logger.setLevel(logging.INFO)
    set_verbose_debug(os.getenv("VERBOSE_DEBUG", "false").lower() == "true")


if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def llm_model_func(prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
    """LLM model function wrapper"""
    return await openai_complete_if_cache(
        "gpt-4.1",
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


async def test_funcs():
    """Test basic functions"""
    result = await llm_model_func("How are you?")
    print("llm_model_func: ", result)

    result = await embedding_func(["How are you?"])
    print("embedding_func: ", result)


asyncio.run(test_funcs())


async def print_stream(stream):
    """Print streaming response"""
    async for chunk in stream:
        if chunk:
            print(chunk, end="", flush=True)


async def initialize_rag():
    """Initialize RAG instance"""
    embedding_dimension = await get_embedding_dim()
    print(f"Detected embedding dimension: {embedding_dimension}")

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


async def main():
    """Main function: load document and query"""
    try:
        rag = await initialize_rag()

        with open("QA/data_valve.txt", "r", encoding="utf-8") as f:
            await rag.ainsert(f.read())

        print("\n=====================")
        print("Query mode: mix")
        print("=====================")
        resp = await rag.aquery(
            "What tools and parts are needed for each assembly process of check valve [Model ID]?",
            param=QueryParam(mode="mix", stream=True),
        )
        if inspect.isasyncgen(resp):
            await print_stream(resp)
        else:
            print(resp)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if rag:
            await rag.finalize_storages()


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())