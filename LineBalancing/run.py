from agent import LineBalancingAgent
from reflexion import ReflexionWrapper
import os
from memory import MemoryManager
from utils import load_tasks, is_correct

MAX_RETRY = 20
DATA_PATH = os.path.join("LineBalancing", "dataset", "line_balance_dataset.json")
MODEL_NAME = "gpt-4.1"

def run_trial(task, model="gpt-4.1"):
    question = task["question"]
    ground_truth = task.get("ground_truth", "")

    agent = LineBalancingAgent(model)
    reflexion_agent = ReflexionWrapper(model)
    memory = MemoryManager()

    for attempt in range(MAX_RETRY):
        print(f"\n🔁 Attempt {attempt+1}...")

        memory_log = memory.format()
        answer = agent.solve(question, memory_log)
        print(f"Answer:\n{answer}")

        if is_correct(answer, ground_truth):
            print("✅ Success: Model answer is correct")
            return answer, True

        reflection = reflexion_agent.reflect(question, answer)
        print(f"🧠 Reflection:\n{reflection}")
        memory.add(question, answer, reflection)

    print("❌ Failed: Maximum attempts reached")
    return answer, False

def main():
    print("🚀 Loading task data...")
    tasks = load_tasks(DATA_PATH)
    print(f"Total {len(tasks)} tasks")

    for task in tasks:
        print(f"\n🧪 Starting task: {task['name']}")
        final_answer, success = run_trial(task, model=MODEL_NAME)
        print("📌 Final answer:", final_answer)
        print("✅ Task succeeded" if success else "❌ Task failed")
        print("=" * 60)

if __name__ == "__main__":
    main()