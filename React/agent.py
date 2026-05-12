import re
import asyncio
from React.tools import RAGQuery, LineBalance, llm_model_func, DescribeMap


def load_prompt_template(file_path="React/prompt_twoshot.txt") -> str:
    """Load prompt template from file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def extract_line_balance_result(final_answer: str) -> str:
    """Extract steps 6-10 from final_answer and renumber them as 1-5"""
    lines = final_answer.strip().splitlines()
    last_five = lines[-5:]
    renumbered = []

    for i, line in enumerate(last_five, start=1):
        new_line = re.sub(r"^\s*\d+\.", f"{i}.", line)
        renumbered.append(new_line)

    return "\n".join(renumbered)


async def run_react_agent(user_question: str, max_steps: int = 10):
    """Main ReAct Agent logic"""
    context = load_prompt_template()
    prompt = f"{context}\n\nQuestion: {user_question}"

    step = 0
    rag_observation = ""

    while step < max_steps:
        print(f"\n--- LLM is thinking... (Step {step+1}) ---")
        response = await llm_model_func(prompt)
        print(response.strip())

        prompt += f"\n{response}"

        match_rag = re.search(r'Action:\s*RAGQuery\("(.+?)"(?:,\s*mode="(.*?)")?\)', response)
        match_lb = re.search(r'Action:\s*LineBalance\("(.+?)"\)', response)
        match_map = re.search(r'Action:\s*DescribeMap\((?:"(.*?)")?\)', response)

        if match_rag:
            query = match_rag.group(1)
            mode = match_rag.group(2) or "mix"
            observation = await RAGQuery(query, mode)
            rag_observation = observation
            print(f"\n[Tool Output] {observation.strip()}")
            prompt += f"\nObservation: {observation}"

        elif match_lb:
            lb_input = match_lb.group(1)
            observation = await LineBalance(lb_input)
            print(f"\n[Tool Output] {observation.strip()}")
            prompt += f"\nObservation: {observation}"

        elif match_map:
            observation = await DescribeMap()
            print(f"\n[Tool Output] {observation.strip()}")
            prompt += f"\nObservation: {observation}"

        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:")[-1].strip()
            line_balance_result = extract_line_balance_result(final_answer)
            return {
                "final_answer": final_answer,
                "line_balance_result": line_balance_result,
                "rag_output": rag_observation,
            }

        step += 1

    return "Failed to complete task within the limited steps."


if __name__ == "__main__":
    user_question = input("Please enter your question:\n> ")
    result = asyncio.run(run_react_agent(user_question))

    print("\n====== Result Output ======\n")
    if isinstance(result, dict):
        print("Final Answer:\n", result["final_answer"])
        print("\nLine Balance Result:\n", result["line_balance_result"])
        print("\nRAG Tool Output:\n", result["rag_output"])
    else:
        print(result)