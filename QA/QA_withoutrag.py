import os
import asyncio
import json
from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)

client = AsyncOpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


async def ask_llm(question: str, context: str, system_prompt=None) -> str:
    """Query LLM directly without RAG"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if context:
        messages.append({"role": "user", "content": f"Please answer based on the following context:\n\n{context}"})
    messages.append({"role": "user", "content": question})

    try:
        response = await client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM call error: {e}")
        return "Error: Unable to get answer"


async def process_questions(context_file: str, question_file: str, output_file: str):
    """Process multiple questions and save results"""
    with open(context_file, 'r', encoding='utf-8') as f:
        context = f.read()

    with open(question_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)

    results = []

    for i, item in enumerate(questions_data):
        question = item.get("question", "").strip()
        if not question:
            continue
        print(f"\n🟡 Processing question {i+1}: {question}")
        answer = await ask_llm(question, context)
        results.append({"question": question, "answer": answer})
        await asyncio.sleep(1)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ All answers saved to: {output_file}")


def main():
    """Main function"""
    context_file = "QA/data_connector.txt"
    input_question_file = "QA/questions&reference/questions_5.json"
    output_answer_file = "QA/answer.json"

    asyncio.run(process_questions(context_file, input_question_file, output_answer_file))


if __name__ == "__main__":
    main()